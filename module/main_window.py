import os
import markdown
from PySide6.QtWidgets import QMainWindow, QTextEdit, QSplitter, QFileDialog
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon


class MainWindow(QMainWindow):
    def __init__(self, filepath=None):
        super().__init__()
        self.current_file = filepath
        # CSSスタイルの事前読み込み（update_preview 呼び出し前に css 属性を用意）
        self.css = ''
        css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'style.css'))
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                self.css = f.read()
        except IOError:
            pass

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

        if filepath and os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.setPlainText(text)
            self.update_preview()

    def on_text_changed(self):
        self.debounce_timer.start(300)

    def update_preview(self):
        body = markdown.markdown(
            self.editor.toPlainText(),
            extensions=['fenced_code', 'tables']
        )
        full_html = (
            '<!doctype html><html><head><meta charset="utf-8">'
            f'<style>{self.css}</style></head><body>{body}</body></html>'
        )
        self.preview.setHtml(full_html)

    def _init_splitter(self):
        w = self.width()
        self.splitter.setSizes([w // 2, w // 2])

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
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", "Markdown Files (*.md);;All Files (*)")
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.setPlainText(text)
            self.current_file = path
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(path)}")
            self.update_preview()

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(self.editor.toPlainText())

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Markdown File As", "", "Markdown Files (*.md);;All Files (*)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.current_file = path
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(path)}")
