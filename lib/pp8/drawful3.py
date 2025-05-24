import os

from lib.game import Game, decode_mapping
from paths import JPP8_PATH

PATH = os.path.join(JPP8_PATH + r'\games\DrawfulAnimate')

class Drawful3(Game):
    game = PATH
    folder = '../data/pp8/drawful3/'

    @decode_mapping(PATH + r'\content\en\DrawfulAnimatePrompt.jet', folder + 'prompts.json')
    def encode_prompts(self, obj):
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['prompt'], 'crowdinContext': self.get_context(c, ','.join(c['tags']))}
        return res

    @decode_mapping(PATH + r'\content\en\DrawfulAnimateDecoy.jet', folder + 'decoy.json')
    def encode_decoy(self, obj):
        res = {}
        for c in obj['content']:
            res[c['id']] = c['text']
        return res

    @decode_mapping(PATH + r'\content\en\DrawfulAnimatePersonalPrompt.jet', folder + 'personal_prompts.json')
    def encode_personal_prompts(self, obj):
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['prompt'], 'crowdinContext': self.get_context(c, ','.join(c['tags']))}
        return res

    @decode_mapping(PATH + r'\content\en\DrawfulAnimatePersonalDecoy.jet', folder + 'personal_decoy.json')
    def encode_personal_decoy(self, obj):
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['text'], 'crowdinContext': self.get_context(c, c['title'])}
        return res
