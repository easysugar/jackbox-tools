import logging
import os

from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP7_PATH


class BlatherRound(Game):
    name = 'BlankyBlank'
    game = os.path.join(JPP7_PATH + rf'\games\{name}')
    folder = './data/pp7/blather/'
    build = './build/uk/JPP7/Blather/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]
        strings, words = count_strings_and_words([
            self._read_json(os.path.join(self.game, 'Localization.json'))['table']['en'],
            audios,
            [w['word'] for c in self.read_jet('BlankyBlankWordLists')['content'] for w in c['words']],
            [[c['alternateSpellings'], c['password'], [w['word'] for w in c['tailoredWords']], c['forbiddenWords']]
             for c in self.read_jet('BlankyBlankPasswords')['content']],
            [c['structures'] for c in self.read_jet('BlankyBlankSentenceStructures')['content']],
        ])
        logging.debug('Total strings: %s\nTotal words: %s', strings, words)
