import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

from mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QtGui.QFont("MS Shell Dlg 2", 14))

    window = MainWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()