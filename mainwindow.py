import os.path
import sys

from typing import Tuple
from music import FilesLoader, SoundsController
from PyQt5.QtCore import QSize, QObject, pyqtSignal, QThread, Qt
from PyQt5 import QtWidgets, QtCore, QtGui

from cv2 import cv2

import settings


def show_message_box(a_title, a_text, a_icon=None):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(a_title)
    msg.setText(a_text)

    if a_icon is not None:
        msg.setIcon(a_icon)

    msg.exec()


def convert_cv_qt(cv_img, size):
    """Convert from an opencv image to QPixmap"""
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
    p = convert_to_Qt_format.scaled(size[0], size[1], Qt.KeepAspectRatio)
    return QtGui.QPixmap.fromImage(p)


def get_picture_of_video(a_path, a_size):
    cap = cv2.VideoCapture(a_path)
    _, cv_img = cap.read()
    return convert_cv_qt(cv_img, a_size)


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, a_args):
        super().__init__()
        self.args = a_args

    def run(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            os_str = 'python3 {} {}'.format(os.path.join(current_dir, 'demo.py'), ' '.join(self.args))
            os.system(os_str)
        except (Exception,):
            pass
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

        self.parent = parent
        self.sounds_controller = SoundsController(FilesLoader.load('ui_sounds'))

        self.methods = {}
        self.selected_picture = None
        self.selected_video = None

        # TODO: Переделать под процентное соотношение
        self._drag_left_region = (QtCore.QPoint(24, 27), QtCore.QPoint(736, 729))
        self._drag_right_region = (QtCore.QPoint(771, 19), QtCore.QPoint(1478, 723))

        self._bair_combopart_region = (QtCore.QPoint(110, 890), QtCore.QPoint(472, 915))
        self._fashion_combopart_region = (QtCore.QPoint(112, 932), QtCore.QPoint(471, 954))
        self._mgif_combopart_region = (QtCore.QPoint(111, 970), QtCore.QPoint(471, 997))
        self._nemo_combopart_region = (QtCore.QPoint(117, 1012), QtCore.QPoint(469, 1034))
        self._taichi_combopart_region = (QtCore.QPoint(118, 1055), QtCore.QPoint(467, 1075))
        self._taichi_adv_combopart_region = (QtCore.QPoint(117, 1092), QtCore.QPoint(467, 1118))
        self._vox_combopart_region = (QtCore.QPoint(117, 1142), QtCore.QPoint(467, 1170))
        self._vox_adv_combopart_region = (QtCore.QPoint(118, 1189), QtCore.QPoint(468, 1209))

        # Convert
        self._convert_btn_region = (QtCore.QPoint(517, 1114), QtCore.QPoint(1009, 1228))

        # Checkbox
        self._adaptive_checkbox_region = (QtCore.QPoint(1040, 810), QtCore.QPoint(1132, 875))
        self._relative_checkbox_region = (QtCore.QPoint(1042, 951), QtCore.QPoint(1133, 1014))

        self._user_agreement_region = (QtCore.QPoint(402, 1291), QtCore.QPoint(1073, 1324))

        self._load_methods()
        self.init_ui()

    def init_ui(self):
        self.setAcceptDrops(True)
        self.setMouseTracking(True)

        # - background gif
        self._bg_gif = QtGui.QMovie(settings.background_files['bg'])
        self._bg_gif.setScaledSize(settings.APP_SIZE)
        self._bg_gif.start()

        self._bg_gif_lbl = QtWidgets.QLabel(self)
        self._bg_gif_lbl.setMovie(self._bg_gif)

        # - loader
        self._loader_gif = QtGui.QMovie(settings.button_files['loading'])
        self._loader_gif.setScaledSize(QSize(349, 245))
        self._loader_gif.jumpToFrame(0)

        self._loader_gif_lbl = QtWidgets.QLabel(self)
        self._loader_gif_lbl.setMovie(self._loader_gif)
        self._loader_gif_lbl.setFixedSize(QSize(349, 245))
        self._loader_gif_lbl.move(572, 785)

        # - overlay
        self._overlay_lbl = QtWidgets.QLabel()
        self._overlay_lbl.setPixmap(QtGui.QPixmap(settings.background_files['overlay']))

        # - columns overlay
        # - columns names
        self._drag_names = QtWidgets.QLabel()
        self._drag_names.setPixmap(QtGui.QPixmap(settings.background_files['column_names']))

        # -- left
        self.left_drag_overlay = FadingImage(
            a_parent=self,
            a_active_img=QtGui.QPixmap(settings.background_files['left_column_overlay']),
            a_region=self._drag_left_region
        )

        self.left_drag_icon = FadingImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.button_files['photo']),
            a_active_img=QtGui.QPixmap(settings.button_files['photo_selection']),
            a_region=self._drag_left_region
        )

        # -- right
        self.right_drag_overlay = FadingImage(
            a_parent=self,
            a_active_img=QtGui.QPixmap(settings.background_files['right_column_overlay']),
            a_region=self._drag_right_region
        )

        self.right_drag_icon = FadingImage(
            a_parent=self,
            a_inactive_img=QtGui.QPixmap(settings.button_files['video']),
            a_active_img=QtGui.QPixmap(settings.button_files['video_selection']),
            a_region=self._drag_right_region
        )

        # - convert button
        self._convert_btn = InvisibleButton(
            a_parent=self,
            a_region=self._convert_btn_region
        )

        # - user agreement btn
        self._user_agreement_btn = InvisibleButton(
            a_parent=self,
            a_region=self._user_agreement_region
        )

        # - checkbox
        self._checkbox_select_controller = SelectController()

        self._adaptive_chxbox = ComboItem(
            a_parent=self,
            a_active_img=QtGui.QPixmap(),
            a_inactive_img=QtGui.QPixmap(),
            a_selected_img=QtGui.QPixmap(settings.button_files['checkbox']),
            a_region=self._adaptive_checkbox_region,
            a_select_controller=self._checkbox_select_controller
        )
        self._adaptive_chxbox.move(1036, 760)
        self._adaptive_chxbox.set_size(QSize(89, 107))

        self._relative_chxbox = ComboItem(
            a_parent=self,
            a_active_img=QtGui.QPixmap(),
            a_inactive_img=QtGui.QPixmap(),
            a_selected_img=QtGui.QPixmap(settings.button_files['checkbox']),
            a_region=self._relative_checkbox_region,
            a_select_controller=self._checkbox_select_controller
        )
        self._relative_chxbox.move(1036, 900)
        self._relative_chxbox.set_size(QSize(89, 107))

        self._picture_of_image = QtWidgets.QLabel(self)
        self._picture_of_image.setScaledContents(True)
        self._picture_of_image.setFixedSize(QSize(712, 725))
        self._picture_of_image.move(12, 20)

        self._picture_of_video = QtWidgets.QLabel(self)
        self._picture_of_video.setScaledContents(True)
        self._picture_of_video.resize(712, 725)
        self._picture_of_video.move(758, 20)

        # - combobox
        comboparts = {
            'bair': ([path for file, path in settings.font_files.items() if 'bair_' in file], self._bair_combopart_region),
            'fashion': ([path for file, path in settings.font_files.items() if 'fashion_' in file], self._fashion_combopart_region),
            'mgif': ([path for file, path in settings.font_files.items() if 'mgif_' in file], self._mgif_combopart_region),
            'nemo': ([path for file, path in settings.font_files.items() if 'nemo_' in file], self._nemo_combopart_region),
            'taichi_adv': ([path for file, path in settings.font_files.items() if 'taichi-adv_' in file], self._taichi_adv_combopart_region),
            'taichi': ([path for file, path in settings.font_files.items() if 'taichi_' in file], self._taichi_combopart_region),
            'vox_adv': ([path for file, path in settings.font_files.items() if 'vox-adv_' in file], self._vox_adv_combopart_region),
            'vox': ([path for file, path in settings.font_files.items() if 'vox_' in file], self._vox_combopart_region),
        }

        self._combo_select_controller = SelectController()

        for name, args in comboparts.items():
            img_paths, region = args
            imgs = [QtGui.QPixmap(path) for path in sorted(img_paths)]
            setattr(self, f'_{name}_combopart', ImageButton(
                a_parent=self,
                a_inactive_img=imgs[0],
                a_active_img=imgs[1],
                a_selected_img=imgs[2],
                a_region=region,
                a_select_controller=self._combo_select_controller
            ))

        self._chbox_parts = [
            self._adaptive_chxbox,
            self._relative_chxbox,
        ]

        self._combo_parts = {
            'bair': self._bair_combopart,
            'fashion': self._fashion_combopart,
            'mgif': self._mgif_combopart,
            'nemo': self._nemo_combopart,
            'taichi-adv': self._taichi_adv_combopart,
            'taichi': self._taichi_combopart,
            'vox-adv': self._vox_adv_combopart,
            'vox': self._vox_combopart,
        }

        self._all_changeable_images = [
            self.left_drag_overlay,
            self.left_drag_icon,
            self.right_drag_overlay,
            self.right_drag_icon,
            *self._combo_parts.values()
        ]

        # - layout
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self._bg_gif_lbl, 0, 0)
        self.layout.addWidget(self._overlay_lbl, 0, 0)
        self.layout.addWidget(self._drag_names, 0, 0)

        for img in self._all_changeable_images:
            self.__add_changeable_image_to_layout(self.layout, img)

        self.setLayout(self.layout)

    def mousePressEvent(self, e):
        for part in self._combo_parts.values():
            part.change_state(e.pos(), True, self.sounds_controller, 'choose_method')

        self._chbox_parts[0].change_state(e.pos(), True, self.sounds_controller, 'adaptive')
        self._chbox_parts[1].change_state(e.pos(), True, self.sounds_controller, 'relative')

        if self._user_agreement_btn.is_clicked(e.pos()):
            self.open_user_agreement()

        if self._convert_btn.is_clicked(e.pos()):
            self._convert(False)

    def dragEnterEvent(self, e):
        self.dragMoveEvent(e)

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
            e.setDropAction(Qt.CopyAction)

            self.left_drag_overlay.change_state(e.pos())
            self.left_drag_icon.change_state(e.pos())

            if self.left_drag_overlay.activated:
                self.sounds_controller.play('image')
                self.load_picture(e.mimeData().urls()[0].toLocalFile())

            self.right_drag_overlay.change_state(e.pos())
            self.right_drag_icon.change_state(e.pos())

            if self.right_drag_overlay.activated:
                self.sounds_controller.play('video')
                self.load_video(e.mimeData().urls()[0].toLocalFile())

            self.dragLeaveEvent(e)

            e.accept()
        else:
            e.ignore()

    def load_picture(self, a_path):
        self.selected_picture = a_path
        self._set_ui_picture(a_path)

    def _set_ui_picture(self, a_path):
        img = QtGui.QPixmap(a_path)
        self._picture_of_image.setPixmap(img)

    def load_video(self, a_path):
        self.selected_video = a_path
        self._set_ui_video(a_path)

    def _set_ui_video(self, a_path):
        img = get_picture_of_video(a_path, (712, 725))
        self._picture_of_video.setPixmap(img)

    def open_user_agreement(self):
        self.sounds_controller.play('agreement', a_auto_restart=True)
        dialog = UserAgreementDialog(self)
        dialog.exec()
        self.sounds_controller.stop('agreement')

    def _select_picture(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выбрать файл", ".")
        if filename != '':
            self.selected_picture = filename

    def _select_video(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выбрать файл", ".")
        if filename != '':
            self.selected_video = filename

    def _convert(self, _a_disable_checks=False):
        if _a_disable_checks:
            self.__start_thread_to_convert([])
        else:
            if self.selected_picture is None:
                show_message_box('Ошибка', 'Картинка не выбрана', QtWidgets.QMessageBox.Critical)
            elif self.selected_video is None:
                show_message_box('Ошибка', 'Видео не выбрано', QtWidgets.QMessageBox.Critical)
            elif len(self.methods) == 0:
                show_message_box('Ошибка', 'Не загружен ни один метод конвертации', QtWidgets.QMessageBox.Critical)
            elif self.__selected_config is None:
                show_message_box('Ошибка', 'Не выбран метод обработки', QtWidgets.QMessageBox.Critical)
            else:
                dirname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выберите место для сохранение видео', '.')
                if dirname != '':
                    result_path = os.path.join(dirname, 'result.mp4')

                    args = ['--config', f'"{self.__selected_config}"', '--checkpoint', f'"{self.__selected_checkpoint}"',
                            '--source_image', f'"{self.selected_picture}"', '--driving_video', f'"{self.selected_video}"',
                            '--result_video', f'"{result_path}"']

                    if self._adaptive_chxbox.selected:
                        args.append('--adapt_scale')
                    if self._relative_chxbox.selected:
                        args.append('--relative')

                    self.__start_thread_to_convert(args)

    def _load_methods(self):
        config_path = 'config'
        checkpoints_path = 'checkpoints'

        if not os.path.exists(config_path):
            show_message_box('Ошибка чтения методов конвертации',
                             f'Папка с конфигурациями конвертации ({config_path}) не найдена!',
                             QtWidgets.QMessageBox.Critical)
        elif not os.path.exists(checkpoints_path):
            show_message_box('Ошибка чтения методов конвертации',
                             f'Папка с чекпоинтами ({checkpoints_path}) не найдена!',
                             QtWidgets.QMessageBox.Critical)
        else:
            configs = {}
            checkpoints = {}

            for root, _, files in os.walk(config_path):
                configs = {os.path.splitext(file)[0]: os.path.join(os.path.abspath(root), file) for file in files}

            for root, _, files in os.walk(checkpoints_path):
                checkpoints = {os.path.splitext(file)[0]: os.path.join(os.path.abspath(root), file) for file in files}

            for file, file_path in configs.items():
                if file not in checkpoints:
                    show_message_box('Ошибка поиска файла',
                                     f'Не найден файл {file}.yaml для файла {file}.tar',
                                     QtWidgets.QMessageBox.Critical)
                else:
                    self.methods[file] = (file_path, checkpoints[file])

    def __start_thread_to_convert(self, a_args):
        self.thread = QThread()
        self.worker = Worker(a_args)

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
        self.sounds_controller.play('conditions', a_auto_restart=True)
        self.setEnabled(False)
        self._loader_gif.start()

    def __stop_converting_ui(self):
        self.sounds_controller.stop('conditions')
        self.setEnabled(True)
        self._loader_gif.jumpToFrame(0)
        self._loader_gif.stop()

    @staticmethod
    def __add_changeable_image_to_layout(a_layout: QtWidgets.QGridLayout, a_img):
        if isinstance(a_img, FadingImage):
            a_layout.addWidget(a_img.get_img_inst(), 0, 0)
        elif isinstance(a_img, ImageButton):
            a_layout.addWidget(a_img.get_active_img_inst(), 0, 0)
            a_layout.addWidget(a_img.get_inactive_img_inst(), 0, 0)
            a_layout.addWidget(a_img.get_selected_img_inst(), 0, 0)
        else:
            RuntimeError()

    @staticmethod
    def __is_point_in_region(a_point: QtCore.QPoint, a_region_begin: QtCore.QPoint, a_region_end: QtCore.QPoint):
        return a_region_begin.x() <= a_point.x() <= a_region_end.x() and \
               a_region_begin.y() <= a_point.y() <= a_region_end.y()

    @property
    def __selected_config(self):
        for config, inst in self._combo_parts.items():
            if inst == self._combo_select_controller.selected_inst:
                return self.methods[f'{config}-256'][0]

    @property
    def __selected_checkpoint(self):
        for checkpoint, inst in self._combo_parts.items():
            if inst == self._combo_select_controller.selected_inst:
                return self.methods[f'{checkpoint}-256'][1]


class SelectController(object):
    def __init__(self):
        self.selected_inst = None

    def set_selected(self, a_inst):
        self.selected_inst = a_inst
        

class ImageButton(QObject):
    def __init__(self, a_parent, a_active_img: QtGui.QPixmap, a_inactive_img: QtGui.QPixmap,
                 a_region: Tuple[QtCore.QPoint, QtCore.QPoint], a_selected_img: QtGui.QPixmap = None,
                 a_select_controller: SelectController = None):
        super(ImageButton, self).__init__(a_parent)

        if a_selected_img is None:
            a_selected_img = QtGui.QPixmap()

        self.select_controller = a_select_controller

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

        self._is_hidden = False
        self._save_visible_inst = None

    def change_state(self, a_pos, a_is_clicked=False,
                     a_sounds_controller: SoundsController = None, a_sound_name: str = None):
        if self._is_hidden:
            return

        if self._is_point_in_region(a_pos):
            if a_is_clicked:
                if self.select_controller is not None:
                    if self.select_controller.selected_inst != self:
                        if self.select_controller.selected_inst is not None:
                            self.select_controller.selected_inst.change_to_inactive()
                        self.select_controller.set_selected(self)
                self.change_to_selected()
                if a_sounds_controller is not None and a_sound_name is not None:
                    a_sounds_controller.play(a_sound_name)
            else:
                if self.activated:
                    self.change_to_inactive()
                else:
                    self.change_to_active()
        else:
            if self.selected:
                if self.select_controller is not None:
                    if self.select_controller.selected_inst is not None and self.select_controller.selected_inst != self:
                        self.change_to_inactive()

    def get_active_img_inst(self) -> QtWidgets.QLabel:
        return self.active_img_lbl

    def get_inactive_img_inst(self) -> QtWidgets.QLabel:
        return self.inactive_img_lbl

    def get_selected_img_inst(self) -> QtWidgets.QLabel:
        return self.selected_img_lbl

    def change_to_active(self):
        if self._is_hidden:
            return

        self.activated = True
        self.selected = False
        self.active_img_lbl.setVisible(True)
        self.inactive_img_lbl.setVisible(False)
        self.selected_img_lbl.setVisible(False)

    def change_to_inactive(self):
        if self._is_hidden:
            return

        self.activated = False
        self.selected = False
        self.active_img_lbl.setVisible(False)
        self.inactive_img_lbl.setVisible(True)
        self.selected_img_lbl.setVisible(False)

    def change_to_selected(self):
        if self._is_hidden:
            return

        self.activated = False
        self.selected = True
        self.active_img_lbl.setVisible(False)
        self.inactive_img_lbl.setVisible(False)
        self.selected_img_lbl.setVisible(True)

    def hide(self):
        if self.activated:
            self._save_visible_inst = self.active_img_lbl
        elif self.selected:
            self._save_visible_inst = self.selected_img_lbl
        else:
            self._save_visible_inst = self.inactive_img_lbl
        self._save_visible_inst.setVisible(False)
        self._is_hidden = True

    def show(self):
        if not self._is_hidden and self._save_visible_inst is not None:
            self._save_visible_inst.setVisible(True)
            self._is_hidden = False
            self._save_visible_inst = None

    def is_selected(self):
        return self.selected

    def move(self, x, y):
        self.inactive_img_lbl.move(x, y)
        self.active_img_lbl.move(x, y)
        self.selected_img_lbl.move(x, y)

    def set_size(self, size):
        self.active_img_lbl.setFixedSize(size)
        self.inactive_img_lbl.setFixedSize(size)
        self.selected_img_lbl.setFixedSize(size)

    def _is_point_in_region(self, a_point: QtCore.QPoint):
        return self.begin_region.x() <= a_point.x() <= self.end_region.x() \
               and self.begin_region.y() <= a_point.y() <= self.end_region.y()


class ComboItem(ImageButton):
    def __init__(self, a_parent, a_active_img: QtGui.QPixmap, a_inactive_img: QtGui.QPixmap,
                 a_selected_img: QtGui.QPixmap, a_region: Tuple[QtCore.QPoint, QtCore.QPoint],
                 a_select_controller: SelectController):
        super().__init__(a_parent, a_active_img, a_inactive_img, a_region, a_selected_img, a_select_controller)

    def change_state(self, a_pos, a_is_clicked=False,
                     a_sounds_controller: SoundsController = None, a_sound_name: str = None):
        if self._is_point_in_region(a_pos):
            if a_is_clicked:
                if self.selected:
                    self.change_to_inactive()
                else:
                    self.change_to_selected()
                a_sounds_controller.play(a_sound_name)


class FadingImage(ImageButton):
    def __init__(self, a_parent, a_active_img: QtGui.QPixmap, a_region: Tuple[QtCore.QPoint, QtCore.QPoint],
                 a_inactive_img: QtGui.QPixmap = None):
        if a_inactive_img is None:
            a_inactive_img = QtGui.QPixmap()
        super(FadingImage, self).__init__(a_parent, a_active_img, a_inactive_img, a_region)

        self.is_constant = False
        self._save_active_img = None

    def set_constant_image(self, a_img: QtGui.QPixmap):
        self.is_constant = True
        self._save_active_img = self.active_img_lbl.pixmap()

        self.change_to_inactive()
        self.inactive_img_lbl.setPixmap(a_img)

    def unset_constant_image(self):
        if self.is_constant:
            self.is_constant = False
            self.active_img_lbl.setPixmap(self._save_active_img)
            self._save_active_img = None

    def change_state(self, a_pos, a_is_clicked=False):
        if self.is_constant:
            return

        if self._is_point_in_region(a_pos):
            if not self.activated:
                self.change_to_active()
        else:
            if self.activated:
                self.change_to_inactive()

    def get_img_inst(self):
        return super(FadingImage, self).get_active_img_inst()

    def move(self, x, y):
        self.active_img_lbl.move(x, y)


class InvisibleButton(ImageButton):
    def __init__(self, a_parent, a_region: Tuple[QtCore.QPoint, QtCore.QPoint]):
        super().__init__(a_parent, QtGui.QPixmap(), QtGui.QPixmap(), a_region)

    def is_clicked(self, e_pos):
        return self._is_point_in_region(e_pos)


class UserAgreementDialog(QtWidgets.QDialog):
    def __init__(self, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Eblya')
        self.setFixedSize(settings.USER_AGREEMENT_DIALOG_SIZE)

        self._background_lbl = QtWidgets.QLabel()
        self._background_lbl.setPixmap(QtGui.QPixmap(settings.background_files['user_agreement']))
        self._background_lbl.setFixedSize(QSize(640, 960))
        self._background_lbl.setScaledContents(True)

        # PyQt5.QtCore.QPoint(463, 23)
        # PyQt5.QtCore.QPoint(636, 52)
        self._exit_btn_region = (QtCore.QPoint(463, 24), QtCore.QPoint(636, 52))
        self._exit_btn = InvisibleButton(
            a_parent=self,
            a_region=self._exit_btn_region
        )

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self._background_lbl)

        self.show()

    def mousePressEvent(self, e):
        if self._exit_btn.is_clicked(e.pos()):
            self.close()
