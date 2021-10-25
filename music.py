class MusicController(object):
    def __init__(self):
        self.events_songs_path = {}
        self.events_songs = {}

    def set_event(self, a_event, a_song):
        self.events_songs_path[a_event] = a_song

    def remove_event(self, a_event):
        if a_event in self.events_songs_path:
            del self.events_songs_path[a_event]
        if a_event is self.events_songs:
            del self.events_songs[a_event]

    def play_song(self, a_song):
        pass

    def stop_song(self, a_event):
        pass

    def tick(self, a_event):
        for e, s in self.events_songs_path.items():
            if a_event == e:
                self.play_song(s)
