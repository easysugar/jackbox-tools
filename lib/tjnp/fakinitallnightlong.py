import logging

from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import TJNP_PATH


class FakinItAllNightLong(Game):
    name = 'FakinIt2'
    pack = TJNP_PATH
    international = True
    folder = './data/tjnp/fakin2/'
    build = './build/uk/TJNP/Fakin2/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A' and v['locale'] == "en"
        ]
        strings, words = count_strings_and_words([
            self.read_localization(),
            audios,
            [[x['fakerHint'], x['task']] for x in self.read_jet('FakinIt2Emojis')['content']],
            [[x['fakerHint'], x['task']] for x in self.read_jet('FakinIt2Fingers')['content']],
            [[x['fakerHint'], x['task']] for x in self.read_jet('FakinIt2Hands')['content']],
            [[x['fakerHint'], x['task']] for x in self.read_jet('FakinIt2Point')['content']],
            [[x['fakerHint'], x['task']] for x in self.read_jet('FakinIt2Thumbs')['content']],
            [[x['fakerHint'], x['task']] for x in self.read_jet('FakinIt2Write')['content']],
        ])
        logging.debug('Total strings: %s\nTotal words: %s', strings, words)
