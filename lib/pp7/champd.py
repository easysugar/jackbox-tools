import os
import re

from lib.game import Game, clean_text, update_localization
from paths import JPP7_PATH


class ChampdUp(Game):
    name = 'WorldChampions'
    game = os.path.join(JPP7_PATH, 'games', name)
    folder = '../data/pp7/champd/'
    build = '../build/uk/JPP7/ChampdUp/'

    def decode_localization(self):
        update_localization(os.path.join(self.game, 'Localization.json'), os.path.join(self.build, 'Localization.json'))

    def encode_round(self):
        obj = self.read_jet('WorldChampionsRound')
        res = {}
        for c in obj['content']:
            o = self.read_content(c['id'], 'WorldChampionsRound')
            context = {'crowdinContext': self.get_context(c, title=c['contest'])}
            res[c['id']] = {
                'prompt': {'text': c['contest'], **context},
            }
            if o['HasResponseAudio']['v'] == 'true':
                res[c['id']]['response'] = {'text': o['ResponseText']['v'], **context}
        self.write_to_data('round.json', res)

    def encode_round_halfAB(self):
        A = self.read_jet('WorldChampionsSecondHalfA')
        B = self.read_jet('WorldChampionsSecondHalfB')
        resA, resB = {}, {}
        for c in A['content']:
            context = {'crowdinContext': self.get_context(c, title=c['contest'])}
            resA[c['id']] = {'prompt': {'text': c['contest'], **context}}
        for c in B['content']:
            context = {'crowdinContext': self.get_context(c, title=c['contest'])}
            resB[c['id']] = {'prompt': {'text': c['contest'], **context}}
        self.write_to_data('roundA.json', resA)
        self.write_to_data('roundB.json', resB)

    def encode_text_subtitles(self):
        obj = self.read_from_data('WorldChampions.json')
        audio = {
            v['id']: {'text': clean_text(v['text'])}
            for c in obj['media']
            for v in c['versions']
            if c['type'] == 'T' and not re.match('^(SFX|MUSIC|AMBIENCE|HOST)/', v['text'])
        }
        self.write_to_data('text.json', audio)
