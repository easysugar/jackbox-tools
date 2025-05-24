import os

from lib.game import Game, decode_mapping
from paths import JPP8_PATH


class Drawful3(Game):
    game = os.path.join(JPP8_PATH + r'\games\DrawfulAnimate')
    folder = '../data/pp8/drawful3/'

    def encode_prompts(self):
        obj = self.read_jet('DrawfulAnimatePrompt')
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['prompt'], 'crowdinContext': self.get_context(c, ','.join(c['tags']))}
        self.write_to_data('prompts.json', res)

    def encode_decoy(self):
        obj = self.read_jet('DrawfulAnimateDecoy')
        res = {}
        for c in obj['content']:
            res[c['id']] = c['text']
        self.write_to_data('decoy.json', res)

    def encode_personal_prompts(self):
        obj = self.read_jet('DrawfulAnimatePersonalPrompt')
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['prompt'], 'crowdinContext': self.get_context(c, ','.join(c['tags']))}
        self.write_to_data('personal_prompts.json', res)

    def encode_personal_decoy(self):
        obj = self.read_jet('DrawfulAnimatePersonalDecoy')
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['text'], 'crowdinContext': self.get_context(c, c['title'])}
        self.write_to_data('personal_decoy.json', res)
