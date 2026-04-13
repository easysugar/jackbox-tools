import logging

from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP11_PATH


class CookieHaus(Game):
    name = 'CookiesGame'
    pack = JPP11_PATH
    international = True
    folder = './data/pp11/cookies/'
    build = './build/uk/JPP11/CookieHaus/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A' and v['locale'] == "en"
        ]
        strings, words = count_strings_and_words([
            self.read_localization(),
            audios,
            self.read_jet('Customer')['content'],
            self.read_jet('SingleCookies'),
            [c['text'] for c in self.read_jet('Redraw')['content']],
            [c['text'] for c in self.read_jet('Prompt')['content']],
        ], drop_keys=('colors', 'cookieTypes', 'id', 'key', 'shapes', 'sprinkleTypes', 'type', 'weights'))
        logging.debug('Total strings: %s\nTotal words: %s', strings, words)
