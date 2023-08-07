from collections import defaultdict

from lib.game import Game, encode_mapping, decode_mapping
from settings.quiplash3 import *


class Quiplash3(Game):
    folder = '../data/tjsp/quiplash3/encoded/'

    @encode_mapping(PATH_QUESTIONS_ROUND1, folder + 'round1.json')
    def encode_quiplash_questions_round1(self, obj: dict) -> dict:
        return {c['id']: '\n'.join((c['prompt'], '\n'.join(c['safetyQuips']))) for c in obj['content']}

    @encode_mapping(PATH_QUESTIONS_ROUND2, folder + 'round2.json')
    def encode_quiplash_questions_round2(self, obj: dict) -> dict:
        return {c['id']: '\n'.join((c['prompt'], '\n'.join(c['safetyQuips']))) for c in obj['content']}

    def encode_localization(self):
        self._encode_localization(PATH_LOCALIZATION, self.folder + 'localization.json')

    @encode_mapping(folder + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        res = defaultdict(dict)
        for c in obj:
            for v in c['versions']:
                if c['type'] == 'A' and v['locale'] == 'en' and not v['text'].endswith('[Unsubtitled]'):
                    res[c['versions'][0]['text'].replace('[category=host]', '')][v['id']] = v['text'].replace('[category=host]', '')
        return res

    @encode_mapping(folder + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        res = defaultdict(dict)
        for c in obj:
            for v in c['versions']:
                if c['type'] == 'T' and v['locale'] == 'en' and not v['text'].startswith('SFX/'):
                    res[c['versions'][0]['text']][v['id']] = v['text']
        return res

    @decode_mapping(PATH_QUESTIONS_FINAL_ROUND, folder + 'final_round.json')
    def encode_final_round(self, obj):
        res = {}
        for c in obj['content']:
            row = {}
            context = c['prompt']
            if c['us'] or c['x']:
                context += '\n-------------'
                if c['us']:
                    context += '\nUSA'
                if c['x']:
                    context += '\n18+'
            row['prompt'] = {'name': c['prompt'], 'crowdinContext': context}
            row['safetyQuips'] = [
                {'quip': sq.replace('|', '\n'), 'crowdinContext': context} for sq in c['safetyQuips']
            ]
            res[c['id']] = row
        return res
