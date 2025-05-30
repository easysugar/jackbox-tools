import os

from lib.game import Game, clean_text
from paths import JPP8_PATH


class Drawful3(Game):
    name = 'DrawfulAnimate'
    international = True
    game = os.path.join(JPP8_PATH + r'\games\DrawfulAnimate')
    folder = '../data/pp8/drawful3/'

    def encode_prompts(self):
        obj = self.read_jet('Prompt')
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['prompt'], 'crowdinContext': self.get_context(c, ','.join(c['tags']))}
        self.write_to_data('prompts.json', res)

    def encode_decoy(self):
        obj = self.read_jet('Decoy')
        res = {}
        for c in obj['content']:
            res[c['id']] = c['text']
        self.write_to_data('decoy.json', res)

    def encode_personal_prompts(self):
        obj = self.read_jet('PersonalPrompt')
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['prompt'], 'crowdinContext': self.get_context(c, ','.join(c['tags']))}
        self.write_to_data('personal_prompts.json', res)

    def encode_personal_decoy(self):
        obj = self.read_jet('PersonalDecoy')
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['text'], 'crowdinContext': self.get_context(c, c['title'])}
        self.write_to_data('personal_decoy.json', res)

    def encode_audio_subtitles(self):
        obj = self.read_from_data('media.json')
        audio = {
            v['id']: {'text': clean_text(v['text']), 'crowdinContext': c.get('crowdinContext', '')}
            for c in obj['media']
            for v in c['versions']
            if c['type'] == 'A' and 'SFX' not in v['text']
        }
        self.write_to_data('audio.json', audio)
