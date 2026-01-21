import os

from lib.game import Game, clean_text, count_strings_and_words
from paths import JPP6_PATH


class Dictionarium(Game):
    name = 'Ridictionary'
    game = os.path.join(JPP6_PATH + rf'\games\{name}')
    folder = '../data/pp6/dictionarium/'
    build = '../build/uk/JPP6/Dictionarium/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]
        strings, words = count_strings_and_words([
            self._read_json(os.path.join(self.game, 'Localization.json'))['table']['en'],
            audios,
            self.read_jet('SingleWords'),
            self.read_jet('SingleWordsDefinitions'),
            self.read_jet('Slang'),
            self.read_jet('SlangDefinitions'),
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
