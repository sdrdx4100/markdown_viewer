import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFontComboBox,
    QSpinBox, QLineEdit, QPushButton, QFileDialog,
    QComboBox, QDialogButtonBox
)
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont


class SettingsDialog(QDialog):
    """アプリケーション設定ダイアログ。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings = QSettings("MarkdownViewer", "MarkdownViewer")
        layout = QVBoxLayout(self)

        # font family
        layout.addWidget(QLabel("Font"))
        self.font_box = QFontComboBox()
        family = self.settings.value("font_family", QFont().family())
        self.font_box.setCurrentFont(QFont(family))
        layout.addWidget(self.font_box)

        # font size
        layout.addWidget(QLabel("Font Size"))
        self.font_size = QSpinBox()
        self.font_size.setRange(6, 72)
        self.font_size.setValue(int(self.settings.value("font_size", 10)))
        layout.addWidget(self.font_size)

        # tab width
        layout.addWidget(QLabel("Tab Width"))
        self.tab_width = QSpinBox()
        self.tab_width.setRange(1, 16)
        self.tab_width.setValue(int(self.settings.value("tab_width", 4)))
        layout.addWidget(self.tab_width)

        # default directory
        layout.addWidget(QLabel("Default Save Directory"))
        dir_layout = QHBoxLayout()
        self.dir_edit = QLineEdit(self.settings.value("default_directory", ""))
        self.dir_button = QPushButton("Browse")
        self.dir_button.clicked.connect(self.choose_dir)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(self.dir_button)
        layout.addLayout(dir_layout)

        # style sheet
        layout.addWidget(QLabel("Style Sheet"))
        self.style_combo = QComboBox()
        css_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
        for fname in os.listdir(css_dir):
            if fname.endswith('.css'):
                self.style_combo.addItem(fname)
        current_css = self.settings.value("style_sheet", "style.css")
        index = self.style_combo.findText(current_css)
        if index >= 0:
            self.style_combo.setCurrentIndex(index)
        layout.addWidget(self.style_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def choose_dir(self):
        """ディレクトリ選択ダイアログを開く。"""
        path = QFileDialog.getExistingDirectory(self, "Select Directory", self.dir_edit.text())
        if path:
            self.dir_edit.setText(path)

    def save(self):
        """設定を保存する。"""
        self.settings.setValue("font_family", self.font_box.currentFont().family())
        self.settings.setValue("font_size", self.font_size.value())
        self.settings.setValue("tab_width", self.tab_width.value())
        self.settings.setValue("default_directory", self.dir_edit.text())
        self.settings.setValue("style_sheet", self.style_combo.currentText())

