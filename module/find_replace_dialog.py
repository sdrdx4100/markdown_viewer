"""QTextEdit 内での検索と置換を提供するダイアログ。"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)


class FindReplaceDialog(QDialog):
    """検索・置換ダイアログ。"""

    def __init__(self, editor, parent=None):
        """ダイアログの初期化を行う。"""

        super().__init__(parent)
        self._editor = editor
        self.setWindowTitle("Find / Replace")

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.find_edit = QLineEdit(self)
        self.replace_edit = QLineEdit(self)
        form.addRow("Find:", self.find_edit)
        form.addRow("Replace:", self.replace_edit)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        find_btn = QPushButton("Find Next", self)
        replace_btn = QPushButton("Replace", self)
        replace_all_btn = QPushButton("Replace All", self)
        btn_layout.addWidget(find_btn)
        btn_layout.addWidget(replace_btn)
        btn_layout.addWidget(replace_all_btn)
        layout.addLayout(btn_layout)

        find_btn.clicked.connect(self.find_next)
        replace_btn.clicked.connect(self.replace_one)
        replace_all_btn.clicked.connect(self.replace_all)

    def find_next(self):
        """次を検索する。"""
        text = self.find_edit.text()
        if text:
            self._editor.find(text)

    def replace_one(self):
        """現在の選択範囲を置換して次を検索する。"""
        cursor = self._editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.find_edit.text():
            cursor.insertText(self.replace_edit.text())
        self.find_next()

    def replace_all(self):
        """文書全体を一括で置換する。"""
        needle = self.find_edit.text()
        if not needle:
            return
        replacement = self.replace_edit.text()
        content = self._editor.toPlainText()
        self._editor.setPlainText(content.replace(needle, replacement))
