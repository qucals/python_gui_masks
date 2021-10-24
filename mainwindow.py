import os.path
import sys
from typing import Tuple

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
        self.setWindowTitle("Govnina")
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

        # TODO: Переделать под процентное соотношение
        self._drag_left_region = (QtCore.QPoint(24, 27), QtCore.QPoint(736, 729))
        self._drag_right_region = (QtCore.QPoint(771, 19), QtCore.QPoint(1478, 723))

        # PyQt5.QtCore.QPoint(110, 890)
        # PyQt5.QtCore.QPoint(472, 915)
        self._bair_combopart_region = (QtCore.QPoint(110, 890), QtCore.QPoint(472, 915))

        # PyQt5.QtCore.QPoint(112, 932)
        # PyQt5.QtCore.QPoint(471, 954)
        self._fashion_combopart_region = (QtCore.QPoint(112, 932), QtCore.QPoint(471, 954))

        # PyQt5.QtCore.QPoint(111, 970)
        # PyQt5.QtCore.QPoint(471, 997)
        self._mgif_combopart_region = (QtCore.QPoint(111, 970), QtCore.QPoint(471, 997))

        # PyQt5.QtCore.QPoint(117, 1012)
        # PyQt5.QtCore.QPoint(469, 1034)
        self._nemo_combopart_region = (QtCore.QPoint(117, 1012), QtCore.QPoint(469, 1034))

        # PyQt5.QtCore.QPoint(118, 1055)
        # PyQt5.QtCore.QPoint(467, 1075)
        self._taichi_combopart_region = (QtCore.QPoint(118, 1055), QtCore.QPoint(467, 1075))

        # PyQt5.QtCore.QPoint(117, 1092)
        # PyQt5.QtCore.QPoint(467, 1118)
        self._taichi_adv_combopart_region = (QtCore.QPoint(117, 1092), QtCore.QPoint(467, 1118))

        # PyQt5.QtCore.QPoint(117, 1142)
        # PyQt5.QtCore.QPoint(467, 1170)
        self._vox_combopart_region = (QtCore.QPoint(117, 1142), QtCore.QPoint(467, 1170))

        # PyQt5.QtCore.QPoint(118, 1189)
        # PyQt5.QtCore.QPoint(468, 1209)
        self._vox_adv_combopart_region = (QtCore.QPoint(110, 472), QtCore.QPoint(472, 915))

        # PyQt5.QtCore.QPoint(118, 1226)
        # PyQt5.QtCore.QPoint(468, 1247)

        # Convert
        # PyQt5.QtCore.QPoint(517, 1114)
        # PyQt5.QtCore.QPoint(1009, 1228)
        self._convert_btn_region = (QtCore.QPoint(517, 1114), QtCore.QPoint(1009, 1228))

        # Checkbox
        # PyQt5.QtCore.QPoint(1040, 810)
        # PyQt5.QtCore.QPoint(1132, 875)
        self._adaptive_checkbox_region = (QtCore.QPoint(1040, 810), QtCore.QPoint(1132, 875))

        # PyQt5.QtCore.QPoint(1042, 951)
        # PyQt5.QtCore.QPoint(1133, 1014)
        self._relative_checkbox_region = (QtCore.QPoint(1042, 951), QtCore.QPoint(1133, 1014))

        self.init_ui()
        # self._load_methods()

    def init_ui(self):
        self.setAcceptDrops(True)

        # - background gif
        self.bg_gif = QtGui.QMovie(settings.background_files['bg'])
        self.bg_gif.setScaledSize(settings.APP_SIZE)
        self.bg_gif.start()

        self.bg_gif_lbl = QtWidgets.QLabel(self)
        self.bg_gif_lbl.setMovie(self.bg_gif)

        # - overlay
        self.overlay_lbl = QtWidgets.QLabel()
        self.overlay_lbl.setPixmap(QtGui.QPixmap(settings.background_files['overlay']))
        self.overlay_lbl.setFixedSize(settings.APP_SIZE)

        # - columns overlay
        # -- left
        self.left_drag_overlay = FadingImage(
            a_parent=self,
            a_img=QtGui.QPixmap(settings.background_files['left_column_overlay']),
            a_region=self._drag_left_region
        )

        self.left_drag_icon = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.button_files['photo']),
            a_active_img=QtGui.QPixmap(settings.button_files['photo_selection']),
            a_region=self._drag_left_region
        )

        # -- right
        self.right_drag_overlay = FadingImage(
            a_parent=self,
            a_img=QtGui.QPixmap(settings.background_files['right_column_overlay']),
            a_region=self._drag_right_region
        )

        self.right_drag_icon = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.button_files['video']),
            a_active_img=QtGui.QPixmap(settings.button_files['video_selection']),
            a_region=self._drag_right_region
        )

        # - combobox
        # TODO: Можно автоматизировать
        self._bair_combopart = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.font_files['bair_256']),
            a_active_img=QtGui.QPixmap(settings.font_files['bair_256s']),
            a_selected_img=QtGui.QPixmap(settings.font_files['bair_256ss']),
            a_region=self._bair_combopart_region
        )
        # self._bair_combopart.move()

        self._fashion_combopart = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.font_files['fashion_256']),
            a_active_img=QtGui.QPixmap(settings.font_files['fashion_256s']),
            a_selected_img=QtGui.QPixmap(settings.font_files['fashion_256ss']),
            a_region=self._fashion_combopart_region
        )

        self._mgif_combopart = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.font_files['mgif_256']),
            a_active_img=QtGui.QPixmap(settings.font_files['mgif_256s']),
            a_selected_img=QtGui.QPixmap(settings.font_files['mgif_256ss']),
            a_region=self._mgif_combopart_region
        )

        self._nemo_combopart = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.font_files['nemo_256']),
            a_active_img=QtGui.QPixmap(settings.font_files['nemo_256s']),
            a_selected_img=QtGui.QPixmap(settings.font_files['nemo_256ss']),
            a_region=self._nemo_combopart_region
        )

        self._taichi_adv_combopart = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.font_files['taichi-adv_256']),
            a_active_img=QtGui.QPixmap(settings.font_files['taichi-adv_256s']),
            a_selected_img=QtGui.QPixmap(settings.font_files['taichi-adv_256ss']),
            a_region=self._taichi_adv_combopart_region
        )

        self._taichi_combopart = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.font_files['taichi_256']),
            a_active_img=QtGui.QPixmap(settings.font_files['taichi_256s']),
            a_selected_img=QtGui.QPixmap(settings.font_files['taichi_256ss']),
            a_region=self._taichi_combopart_region
        )

        self._vox_adv_combopart = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.font_files['vox-adv_256']),
            a_active_img=QtGui.QPixmap(settings.font_files['vox-adv_256s']),
            a_selected_img=QtGui.QPixmap(settings.font_files['vox-adv_256ss']),
            a_region=self._vox_adv_combopart_region
        )

        self._vox_combopart = ChangeableImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.font_files['vox_256']),
            a_active_img=QtGui.QPixmap(settings.font_files['vox_256s']),
            a_selected_img=QtGui.QPixmap(settings.font_files['vox_256ss']),
            a_region=self._vox_combopart_region
        )

        # - layout
        self.layout = QtWidgets.QGridLayout(self)

        self.layout.addWidget(self.bg_gif_lbl, 0, 0)
        self.layout.addWidget(self.overlay_lbl, 0, 0)

        self.__add_changeable_image_to_layout(self.layout, self.left_drag_overlay)
        self.__add_changeable_image_to_layout(self.layout, self.left_drag_icon)

        self.__add_changeable_image_to_layout(self.layout, self.right_drag_overlay)
        self.__add_changeable_image_to_layout(self.layout, self.right_drag_icon)

        self.__add_changeable_image_to_layout(self.layout, self._bair_combopart)
        self.__add_changeable_image_to_layout(self.layout, self._fashion_combopart)
        self.__add_changeable_image_to_layout(self.layout, self._mgif_combopart)
        self.__add_changeable_image_to_layout(self.layout, self._nemo_combopart)
        self.__add_changeable_image_to_layout(self.layout, self._taichi_adv_combopart)
        self.__add_changeable_image_to_layout(self.layout, self._taichi_combopart)
        self.__add_changeable_image_to_layout(self.layout, self._vox_adv_combopart)
        self.__add_changeable_image_to_layout(self.layout, self._vox_combopart)

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

    def mousePressEvent(self, QMouseEvent):
        # print(QMouseEvent.pos())
        pass

    def dragEnterEvent(self, e):
        if e.mimeData().hasImage:
            self.left_drag_overlay.change_state(e.pos())
            self.left_drag_icon.change_state(e.pos())

            self.right_drag_overlay.change_state(e.pos())
            self.right_drag_icon.change_state(e.pos())

            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasImage:
            self.left_drag_overlay.change_state(e.pos())
            self.left_drag_icon.change_state(e.pos())

            self.right_drag_overlay.change_state(e.pos())
            self.right_drag_icon.change_state(e.pos())

            e.accept()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        self.left_drag_overlay.change_to_inactive()
        self.left_drag_icon.change_to_inactive()

        self.right_drag_overlay.change_to_inactive()
        self.right_drag_icon.change_to_inactive()

    def dropEvent(self, e):
        if e.mimeData().hasImage:
            self.left_drag_overlay.change_state(e.pos())
            self.left_drag_icon.change_state(e.pos())

            self.right_drag_overlay.change_state(e.pos())
            self.right_drag_icon.change_state(e.pos())

            e.accept()
        else:
            e.ignore()

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

    @staticmethod
    def __add_changeable_image_to_layout(a_layout: QtWidgets.QGridLayout, a_img):
        if isinstance(a_img, FadingImage):
            a_layout.addWidget(a_img.get_img_inst(), 0, 0)
        elif isinstance(a_img, ChangeableImage):
            a_layout.addWidget(a_img.get_active_img_inst(), 0, 0)
            a_layout.addWidget(a_img.get_inactive_img_inst(), 0, 0)
            a_layout.addWidget(a_img.get_selected_img_inst(), 0, 0)
        else:
            RuntimeError()

    @staticmethod
    def __is_point_in_region(a_point: QtCore.QPoint, a_region_begin: QtCore.QPoint, a_region_end: QtCore.QPoint):
        return a_region_begin.x() <= a_point.x() <= a_region_end.x() and a_region_begin.y() <= a_point.y() <= a_region_end.y()


class ChangeableImage(object):
    def __init__(self,
                 a_parent,
                 a_active_img: QtGui.QPixmap,
                 a_inactive_img: QtGui.QPixmap,
                 a_region: Tuple[QtCore.QPoint, QtCore.QPoint],
                 a_selected_img: QtGui.QPixmap = None):
        if a_selected_img is None:
            a_selected_img = QtGui.QPixmap()

        self.inactive_img_lbl = QtWidgets.QLabel(a_parent)
        self.inactive_img_lbl.setPixmap(a_inactive_img)
        self.inactive_img_lbl.setVisible(True)

        self.active_img_lbl = QtWidgets.QLabel(a_parent)
        self.active_img_lbl.setPixmap(a_active_img)
        self.active_img_lbl.setVisible(False)

        self.selected_img_lbl = QtWidgets.QLabel(a_parent)
        self.selected_img_lbl.setPixmap(a_selected_img)
        self.selected_img_lbl.setVisible(False)

        self.begin_region, self.end_region = a_region

        self.activated = False
        self.selected = False

    def change_state(self, a_pos, a_is_clicked=False):
        if self._is_point_in_region(a_pos):
            if a_is_clicked:
                self.change_to_selected()
            else:
                self.change_to_active()
        else:
            self.change_to_inactive()

    def get_active_img_inst(self) -> QtWidgets.QLabel:
        return self.active_img_lbl

    def get_inactive_img_inst(self) -> QtWidgets.QLabel:
        return self.inactive_img_lbl

    def get_selected_img_inst(self) -> QtWidgets.QLabel:
        return self.selected_img_lbl

    def change_to_active(self):
        self.activated = True
        self.selected = False
        self.active_img_lbl.setVisible(True)
        self.inactive_img_lbl.setVisible(False)
        self.selected_img_lbl.setVisible(False)

    def change_to_inactive(self):
        self.activated = False
        self.selected = False
        self.active_img_lbl.setVisible(False)
        self.inactive_img_lbl.setVisible(True)
        self.selected_img_lbl.setVisible(False)

    def change_to_selected(self):
        self.activated = False
        self.selected = True
        self.active_img_lbl.setVisible(False)
        self.inactive_img_lbl.setVisible(False)
        self.selected_img_lbl.setVisible(True)

    def move(self, x, y):
        self.inactive_img_lbl.move(x, y)
        self.active_img_lbl.move(x, y)
        self.selected_img_lbl.move(x, y)

    def _is_point_in_region(self, a_point: QtCore.QPoint):
        return self.begin_region.x() <= a_point.x() <= self.end_region.x() \
               and self.begin_region.y() <= a_point.y() <= self.end_region.y()


class FadingImage(ChangeableImage):
    def __init__(self, a_parent, a_img: QtGui.QPixmap, a_region: Tuple[QtCore.QPoint, QtCore.QPoint]):
        super(FadingImage, self).__init__(a_parent, a_img, QtGui.QPixmap(), a_region)

    def get_img_inst(self):
        return super(FadingImage, self).get_active_img_inst()

    def move(self, x, y):
        self.active_img_lbl.move(x, y)