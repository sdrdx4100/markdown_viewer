from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit
)


class FindReplaceDialog(QDialog):
    """検索・置換ダイアログ。

    Parameters
    ----------
    parent : QWidget
        親ウィジェット。
    text_edit : QTextEdit
        操作対象のテキストエディット。
    """

    def __init__(self, parent=None, text_edit=None):
        super().__init__(parent)
        self.text_edit = text_edit
        self.setWindowTitle("Find / Replace")
        layout = QVBoxLayout(self)

        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        self.find_edit = QLineEdit()
        find_layout.addWidget(self.find_edit)
        layout.addLayout(find_layout)

        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        self.replace_edit = QLineEdit()
        replace_layout.addWidget(self.replace_edit)
        layout.addLayout(replace_layout)

        button_layout = QHBoxLayout()
        self.find_button = QPushButton("Find Next")
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")
        self.close_button = QPushButton("Close")
        button_layout.addWidget(self.find_button)
        button_layout.addWidget(self.replace_button)
        button_layout.addWidget(self.replace_all_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        self.find_button.clicked.connect(self.find_next)
        self.replace_button.clicked.connect(self.replace_one)
        self.replace_all_button.clicked.connect(self.replace_all)
        self.close_button.clicked.connect(self.close)

    def find_next(self):
        """次を検索する。"""
        text = self.find_edit.text()
        if text:
            self.text_edit.find(text)

    def replace_one(self):
        """現在の選択を置換し次を検索する。"""
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_edit.text())
        self.find_next()

    def replace_all(self):
        """すべて置換する。"""
        text = self.find_edit.text()
        replace_text = self.replace_edit.text()
        if not text:
            return
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()
        self.text_edit.moveCursor(QTextEdit.MoveOperation.Start)
        while self.text_edit.find(text):
            cur = self.text_edit.textCursor()
            cur.insertText(replace_text)
        cursor.endEditBlock()

