import os


from typing import Dict
from PyQt5 import QtCore, QtMultimedia


class FilesLoader:
    @staticmethod
    def load(a_path):
        output = {}
        for root, _, files in os.walk(a_path):
            output = {os.path.splitext(file)[0]: os.path.join(os.path.abspath(root), file) for file in files}
        return output


class SoundsController(object):
    def __init__(self, a_files: Dict[str, str]):
        self.songs_path = a_files
        self.playing_sounds: Dict[str, QtMultimedia.QMediaPlayer] = {}
        self.is_any_playing = False
        self._playlists = {}

    def play(self, a_name, a_auto_restart=False):
        if a_name in self.playing_sounds:
            self.stop(a_name)
        self.playing_sounds[a_name] = QtMultimedia.QMediaPlayer()

        url = QtCore.QUrl.fromLocalFile(self.songs_path[a_name])
        if not a_auto_restart:
            self.playing_sounds[a_name].setMedia(QtMultimedia.QMediaContent(url))
        else:
            self._playlists[a_name] = QtMultimedia.QMediaPlaylist()
            self._playlists[a_name].addMedia(QtMultimedia.QMediaContent(url))
            self._playlists[a_name].setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)
            self.playing_sounds[a_name].setPlaylist(self._playlists[a_name])
        self.playing_sounds[a_name].play()

    def pause(self, a_name):
        if a_name in self.playing_sounds:
            if self.playing_sounds[a_name].state == QtMultimedia.QMediaPlayer.PlayingState:
                self.playing_sounds[a_name].pause()

    def ccontinue(self, a_name):
        if a_name in self.playing_sounds:
            if self.playing_sounds[a_name].state == QtMultimedia.QMediaPlayer.PausedState:
                self.playing_sounds[a_name].play()

    def stop(self, a_name):
        if a_name in self.playing_sounds:
            self.playing_sounds[a_name].stop()
            del self.playing_sounds[a_name]
        if a_name is self._playlists:
            del self._playlists[a_name]

    def all_stop(self):
        for player_inst in self.playing_sounds.values():
            player_inst.stop()