"""アプリケーション設定ダイアログ。"""

import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QDialogButtonBox,
    QFontComboBox,
    QSpinBox,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
)


class SettingsDialog(QDialog):
    """エディタ設定を調整するためのダイアログ。"""

    def __init__(self, parent, styles):
        """ダイアログを初期化する。"""

        super().__init__(parent)
        self._parent = parent
        self._styles = styles
        self.setWindowTitle("Settings")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.font_combo = QFontComboBox(self)
        self.font_combo.setCurrentFont(parent.editor.font())

        self.tab_spin = QSpinBox(self)
        self.tab_spin.setRange(1, 12)
        self.tab_spin.setValue(parent.tab_width)

        dir_layout = QHBoxLayout()
        self.dir_edit = QLineEdit(parent.default_save_dir, self)
        browse_btn = QPushButton("Browse", self)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(browse_btn)

        self.style_combo = QComboBox(self)
        self.style_combo.addItems(sorted(styles.keys()))
        self.style_combo.setCurrentText(parent.current_style_name)

        form.addRow("Font", self.font_combo)
        form.addRow("Tab Width", self.tab_spin)
        form.addRow("Default Save Dir", dir_layout)
        form.addRow("Style", self.style_combo)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        browse_btn.clicked.connect(self._choose_dir)

    def _choose_dir(self):
        """保存先ディレクトリを選択する。"""
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.dir_edit.setText(path)

    def apply(self):
        """各種設定値を親ウィンドウに反映する。"""

        self._parent.editor.setFont(self.font_combo.currentFont())
        self._parent.tab_width = self.tab_spin.value()
        metrics = self._parent.editor.fontMetrics()
        self._parent.editor.setTabStopDistance(
            metrics.horizontalAdvance(" ") * self._parent.tab_width
        )
        self._parent.default_save_dir = self.dir_edit.text()
        self._parent.current_style_name = self.style_combo.currentText()
        settings = self._parent.settings
        settings.setValue("editor_font", self.font_combo.currentFont().family())
        settings.setValue("tab_width", self._parent.tab_width)
        settings.setValue("default_save_dir", self._parent.default_save_dir)
        settings.setValue("style", self._parent.current_style_name)
