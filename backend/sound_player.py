from threading import Thread
from robot_hat import Buzzer, Music

class SoundPlayer(Thread):
    def __init__(self, song):
        self.song = song
        self.music = Music()

    def run(self):
        match self.song:
            case 'entli':
                notes = [
                        ("Middle C", 1), ("Middle D", 1), ("Middle E", 1), ("Middle F", 1),
                        ("Middle G", 2),                  ("Middle G", 2),
                        ("Middle A", 1), ("Middle A", 1), ("Middle A", 1), ("Middle A", 1),
                        ("Middle G", 4),
                        ("Middle A", 1), ("Middle A", 1), ("Middle A", 1), ("Middle A", 1),
                        ("Middle G", 4),
                        ("Middle F", 1), ("Middle F", 1), ("Middle F", 1), ("Middle F", 1),
                        ("Middle E", 2),                  ("Middle E", 2),
                        ("Middle D", 1), ("Middle D", 1), ("Middle D", 1), ("Middle D", 1),
                        ("Middle C", 4)
                        ]

                self.play_notes(notes, tempo=120)

            case 'oops':
                self.play_sound(sound='oops.wav', volume=80)

            case _:
                notes = [("Middle F", 1), ("Middle E", 1), ("Middle D#", 1),
                         ("Middle D", 3)]
                self.play_notes(notes, tempo=120)

    def play_notes(self, notes, tempo):
        buzzer = Buzzer("P0")
        self.music.tempo(tempo)

        for note in notes:
            buzzer.play(self.music.note(note[0]), self.music.beat(note[1]))

    def play_sound(self, sound, volume):
        self.music.music_set_volume(volume)
        self.music.sound_play(sound)