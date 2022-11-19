import re

from lib.game import Game, decode_mapping, read_from_folder
from settings.guesspionage import *


class Guesspionage(Game):
    folder = '../data/pp3/pollposition/encoded/'

    @decode_mapping(PATH_EXPANDED, folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        sfx = re.compile(r'\[category=(sfx|music)]$|^\w+\d:\n|^PP_\w+|^Radio Play short |^Radio Play |Back button pressed')
        return {
            v['id']: {"text": v['text'].replace('[category=host]', '').replace('placeholder: ', '').strip(), "crowdinContext": c.get('context')}
            for c in obj
            for v in c['versions']
            if c['type'] == 'A' and not sfx.search(v['text'])
        }

    @decode_mapping(PATH_LEADERBOARDS, folder + 'leaderboards.json')
    def encode_leaderboards(self, obj):
        return {
            'columns': {i['id']: i['name'] for i in obj['columns']},
            'views': {i['id']: {'name': i['name'], 'description': i['description']} for i in obj['views']},
        }

    @decode_mapping(PATH_BONUS_QUESTIONS, folder + 'bonus_questions.json')
    def encode_bonus_questions(self, obj):
        result = {}
        for c in obj['content']:
            cid = str(c['id'])
            x = read_from_folder(cid, PATH_BONUS_QUESTIONS_DIR)
            body = {x['QText']['v']: {
                "question": x['PollQ']['v'],
                'text': x['QText']['v'],
                'choices': [x['Choice%d' % i]['v'] for i in range(9)],
                'data_mode': x['DataMode']['v'],
                'exp_results': x['ExpResults']['v'],
            }}
            result[cid] = body
        return result
