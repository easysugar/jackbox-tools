from lib.game import Game
from lib.utils import count_strings_and_words
from paths import JPP8_PATH


class Wheel(Game):
    name = 'TheWheel'
    pack = JPP8_PATH
    international = True
    folder = '../data/pp8/wheel/'
    build = '../build/uk/JPP8/Wheel/'

    def count_words_to_translate(self):
        audios = [
            v['text'] for m in self.read_from_data('TheWheel.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]
        strings, words = count_strings_and_words([
            self.read_localization(),
            self.read_jet('Answer'),
            self.read_jet('Guessing'),
            self.read_jet('Matching'),
            self.read_jet('NumberTarget'),
            self.read_jet('PlayerQuestion'),
            self.read_jet('RapidFire'),
            self.read_jet('TappingList'),
            self.read_jet('TypingList'),
            audios,
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
