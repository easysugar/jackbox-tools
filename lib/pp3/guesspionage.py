import re

from lib.game import Game, decode_mapping, read_from_folder
from settings.guesspionage import *


class Guesspionage(Game):
    folder = '../data/pp3/pollposition/encoded/'
    build = '../build/uk/JPP3/Guesspionage/'

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

    @decode_mapping(PATH_LEADERBOARDS, build + 'leaderboards.json', PATH_LEADERBOARDS)
    def decode_leaderboards(self, obj, trans):
        for i in obj['columns']:
            i['name'] = trans['columns'][i['id']]
        for i in obj['views']:
            i['name'] = trans['views'][i['id']]['name']
            i['description'] = trans['views'][i['id']]['description']
        return obj

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
                'category': c['category'],
            }}
            result[cid] = body
        return result

    @decode_mapping(PATH_QUESTIONS, folder + 'questions.json')
    def encode_questions(self, obj):
        result = {}
        unique_fields = {}
        for c in obj['content']:
            cid = str(c['id'])
            x = read_from_folder(cid, PATH_QUESTIONS_DIR)
            body = {x['QText']['v']: {
                "question": x['PollQ']['v'],
                'text': x['QText']['v'],
                'data_mode': x['DataMode']['v'],
                'exp_results': x['ExpResults']['v'],
                'answer': x['A']['v'],
                'choices': [x[i]['v'] for i in sorted(x) if i.startswith('Choice')],
                'target': x['Target']['v'],
                'category': c['category'],
            }}
            result[cid] = body
            unique_fields.update({k: x[k]['v'] for k in x if 'v' in x[k]})
        print('unique fields:', unique_fields)
        return result

    @decode_mapping(PATH_QUESTIONS, build + 'in-game/questions.json', PATH_QUESTIONS)
    def decode_questions(self, obj, trans):
        for i in obj['content']:
            category, *tasks = trans[str(i['id'])].strip().split('\n')
            assert len(i['tasks']) == len(tasks)
            i['category'] = category
            for j, task in zip(i['tasks'], tasks):
                j['v'] = task
        return obj

        result = {}
        unique_fields = {}
        for c in obj['content']:
            cid = str(c['id'])
            x = read_from_folder(cid, PATH_QUESTIONS_DIR)
            body = {x['QText']['v']: {
                "question": x['PollQ']['v'],
                'text': x['QText']['v'],
                'data_mode': x['DataMode']['v'],
                'exp_results': x['ExpResults']['v'],
                'answer': x['A']['v'],
                'choices': [x[i]['v'] for i in sorted(x) if i.startswith('Choice')],
                'target': x['Target']['v'],
            }}
            result[cid] = body
            unique_fields.update({k: x[k]['v'] for k in x if 'v' in x[k]})
        print('unique fields:', unique_fields)
        return result

    def decode_localization(self):
        self.update_localization(PATH_LOCALIZATION, self.build + 'localization.json')
