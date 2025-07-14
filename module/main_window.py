import os
# markdown のインポートは update_preview 内で遅延実行
from PySide6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QSplitter,
    QFileDialog,
    QMenu,
    QDialog,
)
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QAction, QIcon, QFont

from .find_replace_dialog import FindReplaceDialog
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """メインウィンドウクラス。

    Parameters
    ----------
    filepath : str or None, optional
        起動時に開くファイルパス。
    """

    def __init__(self, filepath=None):
        super().__init__()
        self.current_file = filepath
        self.settings = QSettings("MarkdownViewer", "MarkdownViewer")
        self.recent_files = self.settings.value("recent_files", [], list)
        self.css = ""
        self.load_css()

        self.preview = None
        title = "Markdown Viewer"
        if filepath:
            title += f" - {os.path.basename(filepath)}"
        self.setWindowTitle(title)
        # ウィンドウアイコンの設定
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'icon.ico'))
        self.setWindowIcon(QIcon(icon_path))
        self.resize(800, 600)
        self._create_menu()
        splitter = QSplitter(Qt.Horizontal)
        self.editor = QTextEdit()
        splitter.addWidget(self.editor)
        self.load_settings()
        if self.settings.value("preview_visible", True, bool):
            self._create_preview(splitter)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)
        self.splitter = splitter
        QTimer.singleShot(0, self._init_splitter)

        self.debounce_timer = QTimer(singleShot=True)
        self.debounce_timer.timeout.connect(self.update_preview)
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.verticalScrollBar().valueChanged.connect(
            self.sync_preview_scroll
        )

        if filepath and os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.setPlainText(text)
            self.update_preview()
            self.add_recent_file(filepath)

    def on_text_changed(self):
        self.debounce_timer.start(300)

    def update_preview(self):
        # markdown モジュールを遅延インポート
        import markdown
        if self.preview is None:
            self._create_preview(self.splitter)
        body = markdown.markdown(
            self.editor.toPlainText(),
            extensions=["fenced_code", "tables"],
        )
        full_html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            f"<style>{self.css}</style></head><body>{body}</body></html>"
        )
        self.preview.setHtml(full_html)

    def _init_splitter(self):
        w = self.width()
        self.splitter.setSizes([w // 2, w // 2])

    def _create_preview(self, splitter):
        """プレビューペインを生成する。"""
        from PySide6.QtWebEngineWidgets import QWebEngineView
        # splitter を親に指定し、明示的な show() は不要
        self.preview = QWebEngineView(splitter)
        splitter.addWidget(self.preview)

    def _create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        save_as_action = QAction("Save &As...", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        recent_menu = QMenu("Recent Files", self)
        self.recent_menu = recent_menu
        file_menu.addMenu(recent_menu)
        self.update_recent_menu()
        file_menu.addSeparator()
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("&Edit")
        find_action = QAction("&Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        replace_action = QAction("&Replace", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.show_replace_dialog)
        edit_menu.addAction(replace_action)

        view_menu = menu_bar.addMenu("&View")
        self.toggle_preview_action = QAction("Toggle Preview", self, checkable=True)
        self.toggle_preview_action.setChecked(self.preview is not None)
        self.toggle_preview_action.triggered.connect(self.toggle_preview)
        view_menu.addAction(self.toggle_preview_action)

    def open_file(self):
        start_dir = self.settings.value("default_directory", "")
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            start_dir,
            "Markdown Files (*.md);;All Files (*)",
        )
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.setPlainText(text)
            self.current_file = path
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(path)}")
            self.update_preview()
            self.add_recent_file(path)

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(self.editor.toPlainText())

    def save_file_as(self):
        start_dir = self.settings.value("default_directory", "")
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File As",
            start_dir,
            "Markdown Files (*.md);;All Files (*)",
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.current_file = path
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(path)}")
            self.add_recent_file(path)

    def show_find_dialog(self):
        """検索ダイアログを表示する。"""
        dialog = FindReplaceDialog(self, self.editor)
        dialog.replace_edit.hide()
        dialog.replace_button.hide()
        dialog.replace_all_button.hide()
        dialog.exec()

    def show_replace_dialog(self):
        """置換ダイアログを表示する。"""
        dialog = FindReplaceDialog(self, self.editor)
        dialog.exec()

    def toggle_preview(self, checked):
        """プレビューの表示を切り替える。"""
        self.settings.setValue("preview_visible", checked)
        if checked:
            if self.preview is None:
                self._create_preview(self.splitter)
        if self.preview:
            self.preview.setVisible(checked)

    def open_settings(self):
        """設定ダイアログを開く。"""
        dialog = SettingsDialog(self)
        # exec() returns QDialog.Accepted or Rejected
        if dialog.exec() == QDialog.Accepted:
            dialog.save()
            self.load_settings()
            self.load_css()
            self.update_preview()

    def load_settings(self):
        """設定を読み込みエディタに反映する。"""
        font_family = self.settings.value("font_family", QFont().family())
        font_size = int(self.settings.value("font_size", 10))
        font = QFont(font_family, font_size)
        self.editor.setFont(font)
        tab_width = int(self.settings.value("tab_width", 4))
        self.editor.setTabStopDistance(self.editor.fontMetrics().horizontalAdvance(' ') * tab_width)

    def load_css(self):
        """スタイルシートを読み込む。"""
        css_name = self.settings.value("style_sheet", "style.css")
        css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', css_name))
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                self.css = f.read()
        except IOError:
            self.css = ''

    def sync_preview_scroll(self, value):
        """エディタのスクロール位置に合わせてプレビューをスクロールする。"""
        if not self.preview:
            return
        bar = self.editor.verticalScrollBar()
        ratio = value / max(1, bar.maximum())
        js = f"window.scrollTo(0, document.body.scrollHeight * {ratio});"
        self.preview.page().runJavaScript(js)

    def add_recent_file(self, path):
        """最近使ったファイルリストに追加する。"""
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:10]
        self.settings.setValue("recent_files", self.recent_files)
        self.update_recent_menu()

    def update_recent_menu(self):
        """最近使ったファイルメニューを更新する。"""
        self.recent_menu.clear()
        for path in self.recent_files:
            action = QAction(path, self)
            action.triggered.connect(lambda chk=False, p=path: self.open_recent(p))
            self.recent_menu.addAction(action)

    def open_recent(self, path):
        """最近使ったファイルを開く。"""
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.setPlainText(text)
            self.current_file = path
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(path)}")
            self.update_preview()
