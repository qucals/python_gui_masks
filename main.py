import sys

from PyQt5.QtWidgets import QApplication

from mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
