"""メインウィンドウの実装。"""

import os
import markdown
from PySide6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QSplitter,
    QFileDialog,
    QMenu,
)
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QAction, QIcon, QFont

from .find_replace_dialog import FindReplaceDialog
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Markdown 編集とプレビューを提供するメインウィンドウ。"""

    def __init__(self, filepath=None):
        """ウィンドウを初期化する。"""
        super().__init__()
        self.settings = QSettings("MarkdownViewer", "App")
        self.current_file = filepath
        self.tab_width = int(self.settings.value("tab_width", 4))
        self.default_save_dir = self.settings.value("default_save_dir", "")

        self._load_styles()
        self.current_style_name = self.settings.value(
            "style", next(iter(self.styles)) if self.styles else ""
        )

        font_family = self.settings.value("editor_font", "")
        self.editor_font = QFont(font_family) if font_family else QFont()

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
        self.editor.setFont(self.editor_font)
        metrics = self.editor.fontMetrics()
        self.editor.setTabStopDistance(
            metrics.horizontalAdvance(" ") * self.tab_width
        )
        from PySide6.QtWebEngineWidgets import QWebEngineView
        self.preview = QWebEngineView()
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)
        self.splitter = splitter
        QTimer.singleShot(0, self._init_splitter)

        self.debounce_timer = QTimer(singleShot=True)
        self.debounce_timer.timeout.connect(self.update_preview)
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.verticalScrollBar().valueChanged.connect(
            self._sync_scroll_preview
        )

        self.recent_files = self.settings.value("recent_files", [], type=list)
        self._update_recent_files_menu()

        if filepath and os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.setPlainText(text)
            self.update_preview()

    def on_text_changed(self):
        """テキスト変更後にプレビュー更新を遅延実行する。"""

        self.debounce_timer.start(300)

    def update_preview(self):
        """エディタ内容を HTML に変換しプレビューに表示する。"""

        body = markdown.markdown(
            self.editor.toPlainText(),
            extensions=["fenced_code", "tables"],
        )
        css = self.styles.get(self.current_style_name, "")
        full_html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            f"<style>{css}</style></head><body>{body}</body></html>"
        )
        self.preview.setHtml(full_html)

    def _init_splitter(self):
        """画面分割比を初期化する。"""

        w = self.width()
        self.splitter.setSizes([w // 2, w // 2])

    def _load_styles(self):
        """CSS スタイルを読み込む。"""

        self.styles = {}
        css_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "static")
        )
        for name in os.listdir(css_dir):
            if name.endswith(".css"):
                path = os.path.join(css_dir, name)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.styles[name] = f.read()
                except OSError:
                    continue

    def _create_menu(self):
        """メニューを生成する。"""

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
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        self.recent_menu = QMenu("Recent Files", self)
        file_menu.insertMenu(exit_action, self.recent_menu)

        edit_menu = menu_bar.addMenu("&Edit")
        find_action = QAction("&Find/Replace", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        edit_menu.addAction(settings_action)

        view_menu = menu_bar.addMenu("&View")
        self.toggle_preview_action = QAction("Toggle Preview", self, checkable=True, checked=True)
        self.toggle_preview_action.triggered.connect(self.toggle_preview)
        view_menu.addAction(self.toggle_preview_action)

    def open_file(self):
        """Markdown ファイルを開く。"""

        path, _ = QFileDialog.getOpenFileName(
            self, "Open Markdown File", "", "Markdown Files (*.md);;All Files (*)"
        )
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.setPlainText(text)
            self.current_file = path
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(path)}")
            self.update_preview()
            self._add_recent_file(path)

    def save_file(self):
        """現在のファイルに保存する。"""

        if not self.current_file:
            return self.save_file_as()
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(self.editor.toPlainText())

    def save_file_as(self):
        """別名で Markdown ファイルを保存する。"""

        start_dir = self.default_save_dir or ""
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
            self._add_recent_file(path)

    def show_find_dialog(self):
        """検索ダイアログを表示する。"""

        dialog = FindReplaceDialog(self.editor, self)
        dialog.exec()

    def show_settings_dialog(self):
        """設定ダイアログを表示する。"""

        dialog = SettingsDialog(self, self.styles)
        if dialog.exec() == dialog.Accepted:
            dialog.apply()
            self.update_preview()

    def toggle_preview(self):
        """プレビュー表示の ON/OFF を切り替える。"""

        if self.toggle_preview_action.isChecked():
            self.preview.show()
        else:
            self.preview.hide()

    def _add_recent_file(self, path):
        """最近使用したファイルのリストに追加する。"""

        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:5]
        self.settings.setValue("recent_files", self.recent_files)
        self._update_recent_files_menu()

    def _update_recent_files_menu(self):
        """最近使ったファイルメニューを更新する。"""

        self.recent_menu.clear()
        for path in self.recent_files:
            action = QAction(path, self)
            action.setData(path)
            action.triggered.connect(self._open_recent_file)
            self.recent_menu.addAction(action)

    def _open_recent_file(self):
        """最近使ったファイルを開く。"""

        action = self.sender()
        if not isinstance(action, QAction):
            return
        path = action.data()
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.setPlainText(text)
            self.current_file = path
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(path)}")
            self.update_preview()

    def _sync_scroll_preview(self, value):
        """エディタとプレビューのスクロール位置を同期する。"""

        bar = self.editor.verticalScrollBar()
        if bar.maximum() == 0:
            return
        ratio = value / bar.maximum()
        js = f"window.scrollTo(0, document.body.scrollHeight * {ratio});"
        self.preview.page().runJavaScript(js)
