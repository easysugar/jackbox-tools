import logging
import os

from lib.game import Game
from lib.utils import count_strings_and_words
from paths import JPP7_PATH


class DevilsAndTheDetails(Game):
    name = 'Everyday'
    international = True
    game = os.path.join(JPP7_PATH + rf'\games\{name}')
    folder = './data/pp7/devils/'
    build = './build/uk/JPP7/Devils/'

    def count_words_to_translate(self):
        audios = [
            v['text'] for m in self.read_from_data('Everyday.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]
        strings, words = count_strings_and_words([
            self._read_json(os.path.join(self.game, 'Localization.json'))['table']['en'],
            [p['name'] for p in self.read_json('cattasks')['payload']],
            [p['name'] for p in self.read_json('conversations')['payload']],
            [p['name'] for p in self.read_json('gatherlists')['payload']],
            [p['name'] for p in self.read_json('gatherlocations')['payload']],
            [p['name'] for p in self.read_json('phonebook')['payload']['listings']],
            [p['name'] for p in self.read_json('travellocations')['payload']],
            [p['name'] for p in self.read_json('searchscenarios')['payload']],
            [l['name'] for p in self.read_json('searchscenarios')['payload'] for l in p['locations']],
            [c['name'] for p in self.read_json('gatherlocations')['payload'] for c in p['containers']],
            [ct['name'] for p in self.read_json('gatherlocations')['payload'] for c in p['containers'] for ct in c['contents']],
            self.read_json('gameconfig')['payload']['OTHER_CAT_NAME_CHOICES'],
            audios,
        ])
        logging.debug('Total strings: %s\nTotal words: %s', strings, words)
