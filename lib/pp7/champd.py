import os
import re

from lib.game import Game, clean_text, update_localization
from paths import JPP7_PATH


class ChampdUp(Game):
    name = 'WorldChampions'
    game = os.path.join(JPP7_PATH, 'games', name)
    folder = '../data/pp7/champd/'
    build = '../build/uk/JPP7/ChampdUp/'
    regex = re.compile(r'чемпіон (з |зі |із |серед )?(.+)', flags=re.IGNORECASE)

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

    def decode_round(self):
        trans = self.read_from_build('round.json')
        obj = self.read_jet('WorldChampionsRound')
        for c in obj['content']:
            text = trans[str(c['id'])]['prompt']['text']
            g = self.regex.search(text).groups()
            text = f'чемпіона з {g[1]}'
            c['contest'] = text
            c['gameText'] = g[1]
        self.write_jet('WorldChampionsRound', obj)

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

    def decode_round_halfAB(self):
        trA = self.read_from_build('roundA.json')
        trB = self.read_from_build('roundB.json')
        A = self.read_jet('WorldChampionsSecondHalfA')
        B = self.read_jet('WorldChampionsSecondHalfB')
        for c in B['content']:
            text = trB[c['id']]['prompt']['text']
            g = self.regex.search(text).groups()
            text = f'чемпіона з {g[1]}'
            c['contest'] = text
            c['gameText'] = g[1]
        for c in A['content']:
            text = trA[c['id']]['prompt']['text']
            g = self.regex.search(text).groups()
            text = f'чемпіона з {g[1]}'
            c['contest'] = text
            c['gameText'] = g[1]
        self.write_jet('WorldChampionsSecondHalfA', A)
        self.write_jet('WorldChampionsSecondHalfB', B)

    def encode_text_subtitles(self):
        obj = self.read_from_data('WorldChampions.json')
        audio = {
            v['id']: {'text': clean_text(v['text'])}
            for c in obj['media']
            for v in c['versions']
            if c['type'] == 'T' and not re.match('^(SFX|MUSIC|AMBIENCE|HOST)/', v['text'])
        }
        self.write_to_data('text.json', audio)

    def encode_audio_subtitles(self):
        obj = self.read_from_data('WorldChampions.json')
        audio = {
            v['id']: {'text': clean_text(v['text']), 'crowdinContext': c.get('crowdinContext', '')}
            for c in obj['media']
            for v in c['versions']
            if c['type'] == 'A'
        }
        self.write_to_data('audio.json', audio)

    def decode_media(self):
        text = self.read_from_build('text.json')
        text = {k: v['text'] for k, v in text.items()}
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'WorldChampions.json',
                               trans=text, path_save=self.folder + 'translated_dict.txt')
