"""アプリケーションのエントリポイント。"""

import sys
from PySide6.QtWidgets import QApplication

def main():
    """アプリケーションを起動する。"""

    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    app = QApplication(sys.argv)
    from module.main_window import MainWindow
    win = MainWindow(filepath)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
