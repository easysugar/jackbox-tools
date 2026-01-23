import re

from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP8_PATH


class WeaponsDrawn(Game):
    name = 'MurderDetectives'
    pack = JPP8_PATH
    international = True
    folder = '../data/pp8/murders/'
    build = '../build/uk/JPP8/Murders/'

    def count_words_to_translate(self):
        audios = [
            clean_text(re.sub(r'(LORD\s*TIPPET|NARRATOR):', '', v['text'], flags=re.IGNORECASE))
            for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]

        strings, words = count_strings_and_words([
            self.read_localization(),
            [c['name'] for c in self.read_jet('Guest')['content']],
            [c['weapon'] for c in self.read_jet('Weapon')['content']],
            audios,
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
