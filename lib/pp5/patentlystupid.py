import os
import re

from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP5_PATH


class PatentlyStupid(Game):
    name = 'PatentlyStupid'
    game = os.path.join(JPP5_PATH + rf'\games\{name}')
    folder = '../data/pp5/patents/'
    build = '../build/uk/JPP5/Patents/'

    def count_words_to_translate(self):
        audios = [
            clean_text(re.sub('toby:|lena:', '', v['text'], flags=re.IGNORECASE))
            for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]
        prompts = []
        for c in self.read_jet('PatentlyStupidGeneDrawing')['content']:
            o = self.read_content(c['id'], 'PatentlyStupidGeneDrawing')
            prompts.append(o['Tagline']['v'])
        strings, words = count_strings_and_words([
            self._read_json(os.path.join(self.game, 'Localization.json'))['table']['en'],
            audios,
            self.read_jet('PatentlyStupidShortie'),
            self.read_jet('PatentlyStupidGeneDrawing'),
            prompts,
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
