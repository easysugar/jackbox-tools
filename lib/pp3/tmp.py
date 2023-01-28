from lib.game import Game, encode_mapping
from settings.tmp import *


class TMP(Game):
    folder = '../data/pp3/tmp/encoded/'

    @encode_mapping(PATH_QUESTION, folder + 'questions.json')
    def encode_question(self, obj: dict):
        assert len({c['id'] for c in obj['content']}) == len(obj['content'])
        result = {}
        for c in obj['content']:
            if c['pic'] == True:
                continue
            assert c['id'] not in result
            assert c['text'] is not None
            assert len(c['choices']) == 4
            corrects = [i.get('correct', False) for i in c['choices']]
            assert corrects.count(True) == 1
            answer = corrects.index(True) + 1
            result[c['id']] = '{}\n{}\n{}'.format(
                c['text'],
                '\n'.join([i['text'] for i in c['choices']]),
                answer
            )
        return result

    @encode_mapping(PATH_LEADERBOARDS, folder + 'leaderboards.json')
    def encode_leaderboards(self, obj):
        return {
            'columns': {i['id']: i['name'] for i in obj['columns']},
            'views': {i['id']: {'name': i['name'], 'description': i['description']} for i in obj['views']},
        }

    @encode_mapping(PATH_SETTINGS, folder + 'settings.json')
    def encode_settings(self, obj):
        return {
            i['source']: {'title': i['title'], 'description': i['description']} for i in obj['items']
        }
