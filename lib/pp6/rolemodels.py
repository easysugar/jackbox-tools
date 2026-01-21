import os

from lib.game import Game, clean_text
from lib.pp11.legends import drop_keys
from lib.utils import count_strings_and_words
from paths import JPP6_PATH


class RoleModels(Game):
    name = 'RoleModels'
    name_short = 'RM'
    game = os.path.join(JPP6_PATH + rf'\games\{name}')
    folder = '../data/pp6/roles/'
    build = '../build/uk/JPP6/Roles/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]
        strings, words = count_strings_and_words([
            self._read_json(os.path.join(self.game, 'Localization.json'))['table']['en'],
            audios,
            drop_keys(self.read_jet('DataAnalysis'), 'contradiction', 'opposite', 'same'),
            drop_keys(self.read_jet('PopCulturePrompt'), 'tags', 'id'),
            drop_keys(self.read_jet('SituationalPrompt'), 'tags', 'id'),
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
