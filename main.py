import sys
from PySide6.QtWidgets import QApplication
from module.main_window import MainWindow

def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    app = QApplication(sys.argv)
    win = MainWindow(filepath)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
