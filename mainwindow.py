import os.path
import sys

from PyQt5.QtCore import QSize, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QMovie
from PyQt5 import QtWidgets, QtCore, QtGui

# import demo as slz
import settings


def show_message_error(a_title, a_text):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setWindowTitle(a_title)
    msg.setText(a_text)
    msg.exec()


def show_message(a_title, a_text):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(a_title)
    msg.setText(a_text)
    msg.exec()


class Worker(QObject):
    finished = pyqtSignal()

    def run(self):
        # slz.main()
        self.finished.emit()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Converter")
        self.setFixedSize(settings.APP_SIZE)

        self.form_widget = FormWidget(self)
        self.setCentralWidget(self.form_widget)

        self.show()


class FormWidget(QtWidgets.QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(FormWidget, self).__init__(parent, *args, **kwargs)

        self.methods = {}
        self.selected_picture = None
        self.selected_video = None

        self.init_ui()
        # self._load_methods()

    def init_ui(self):
        # - background gif
        self.bg_gif = QtGui.QMovie(settings.background_files['bg'])
        self.bg_gif.setScaledSize(settings.APP_SIZE)
        self.bg_gif.start()

        self.bg_gif_lbl = QtWidgets.QLabel(self)
        self.bg_gif_lbl.setMovie(self.bg_gif)

        # - overlay
        self.overlay_lbl = QtWidgets.QLabel()
        self.overlay_lbl.setPixmap(QtGui.QPixmap(settings.background_files['overlay']))

        # 

        # - layout
        self.layout = QtWidgets.QGridLayout(self)

        self.layout.addWidget(self.bg_gif_lbl, 0, 0)
        self.layout.addWidget(self.overlay_lbl, 0, 0)



        #
        # self.select_picture_btn = QtWidgets.QPushButton("Выбрать картинку")
        # self.select_picture_btn.clicked.connect(self._select_picture)
        # self.layout.addWidget(self.select_picture_btn)
        #
        # self.select_video_btn = QtWidgets.QPushButton("Выбрать видео")
        # self.select_video_btn.clicked.connect(self._select_video)
        # self.layout.addWidget(self.select_video_btn)
        #
        # self.method_combo = QtWidgets.QComboBox(self)
        # self.method_combo.currentTextChanged.connect(self._on_method_changed)
        # self.layout.addWidget(self.method_combo)
        #
        # self.adapt_scale_cbox = QtWidgets.QCheckBox(self)
        # self.adapt_scale_cbox.setText('Адаптироваться под \nпропорции исходника')
        # self.layout.addWidget(self.adapt_scale_cbox)
        #
        # self.relative_cbox = QtWidgets.QCheckBox(self)
        # self.relative_cbox.setText('Относительные \nкоординты')
        # self.layout.addWidget(self.relative_cbox)
        #
        # self.convert_btn = QtWidgets.QPushButton("Сделать Пэздато")
        # self.convert_btn.clicked.connect(self._convert)
        # self.layout.addWidget(self.convert_btn)
        #
        # self.movie = QMovie('ui_resources/loading.gif')
        # self.movie.setScaledSize(QSize(25, 25))
        #
        # self.movie_label = QtWidgets.QLabel(self)
        # self.movie_label.setMovie(self.movie)
        # self.movie_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.movie_label.setVisible(False)
        #
        # self.layout.addWidget(self.movie_label)

        self.setLayout(self.layout)

    def _select_picture(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выбрать файл", ".")
        if filename != '':
            self.selected_picture = filename

    def _select_video(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выбрать файл", ".")
        if filename != '':
            self.selected_video = filename

    def _on_method_changed(self, method):
        self.selected_config, self.selected_checkpoint = self.methods[method]

    def _convert(self, _a_disable_checks=True):
        _a_disable_checks = True

        if _a_disable_checks:
            self.__convert()
        else:
            if self.selected_picture is None:
                show_message_error('Ошибка', 'Картинка не выбрана')
            elif self.selected_video is None:
                show_message_error('Ошибка', 'Видео не выбрано')
            elif len(self.methods) == 0:
                show_message_error('Ошибка', 'Не загружен ни один метод конвертации')
            else:
                dirname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выберите место для сохранение видео', '.')
                if dirname != '':
                    result_path = os.path.join(dirname, 'result.mp4')

                    new_args = ['--config', self.selected_config, '--checkpoint', self.selected_checkpoint,
                                '--source_image', self.selected_picture, '--driving_video', self.selected_video,
                                '--result_video', result_path]
                    if self.adapt_scale_cbox.isChecked():
                        new_args.append('--adapt_scale')
                    if self.relative_cbox.isChecked():
                        new_args.append('--relative')

                    sys.argv = sys.argv + new_args
                    self.__convert()

    def _load_methods(self):
        config_path = 'config'
        checkpoints_path = 'checkpoints'

        if not os.path.exists(config_path):
            show_message_error('Ошибка чтения методов конвертации',
                               f'Папка с конфигурациями конвертации ({config_path}) не найдена!')
        elif not os.path.exists(checkpoints_path):
            show_message_error('Ошибка чтения методов конвертации',
                               f'Папка с чекпоинтами ({checkpoints_path}) не найдена!')
        else:
            configs = {}
            checkpoints = {}

            for root, _, files in os.walk(config_path):
                configs = {os.path.splitext(file)[0]: os.path.join(os.path.abspath(root), file) for file in files}

            for root, _, files in os.walk(checkpoints_path):
                checkpoints = {os.path.splitext(file)[0]: os.path.join(os.path.abspath(root), file) for file in files}

            for file, file_path in configs.items():
                if file not in checkpoints:
                    show_message_error('Ошибка поиска файла',
                                       f'Не найден файл {file}.yaml для файла {file}.tar')
                else:
                    self.methods[file] = (file_path, checkpoints[file])

            for method in self.methods.keys():
                self.method_combo.addItem(method)

    def __convert(self):
        self.thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        self.__start_converting_ui()
        self.thread.finished.connect(
            lambda: self.__stop_converting_ui()
        )

    def __start_converting_ui(self):
        self.setEnabled(False)
        self.movie_label.setVisible(True)
        self.movie.start()

    def __stop_converting_ui(self):
        self.setEnabled(True)
        self.movie_label.setVisible(False)
        self.movie.stop()
