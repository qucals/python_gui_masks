import os

from PyQt5.QtCore import QSize

APP_SIZE = QSize(1488, 1337)
USER_AGREEMENT_DIALOG_SIZE = QSize(640, 960)

SOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui_resources')

BACKGROUND_PATH = os.path.join(SOURCE_PATH, 'background')
BUTTONS_PATH = os.path.join(SOURCE_PATH, 'buttons')
FONTS_PATH = os.path.join(SOURCE_PATH, 'fonts')

exception_files = ['.DS_Store']

background_files = [
    {os.path.splitext(file)[0]: os.path.join(os.path.abspath(root), file) for file in files if
     file not in exception_files}
    for root, _, files in os.walk(BACKGROUND_PATH)
][0]

button_files = [
    {os.path.splitext(file)[0]: os.path.join(os.path.abspath(root), file) for file in files if
     file not in exception_files}
    for root, _, files in os.walk(BUTTONS_PATH)
][0]

font_files = [
    {os.path.splitext(file)[0]: os.path.join(os.path.abspath(root), file) for file in files if
     file not in exception_files}
    for root, _, files in os.walk(FONTS_PATH)
][0]
