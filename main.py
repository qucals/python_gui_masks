import sys
import os

from PyQt5.QtWidgets import QApplication

from mainwindow import MainWindow


def install_requirements():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.system('pytho3 -m pip install {}'.format(os.path.join(current_dir, 'requirements.txt')))


def main():
    install_requirements()

    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
