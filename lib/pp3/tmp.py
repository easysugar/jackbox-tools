import re
from collections import defaultdict

from lib.game import Game, encode_mapping
from settings.tmp import *


class TMP(Game):
    folder = '../data/pp3/tmp/encoded/'
    folder_swf = '../data/pp3/tmp/swf/'

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

    @encode_mapping(PATH_FINAL_ROUND, folder + 'final_questions.json')
    def encode_final_round(self, obj: dict):
        res = {}
        for q in obj['content']:
            text = q['text']
            corrects = defaultdict(set)
            for c in q['choices']:
                assert set(c) == {'correct', 'easy', 'text'}
                assert c['correct'] in (True, False)
                assert c['easy'] in (True, False)
                assert c['text'].strip()
                t = c['text'].strip()
                # assert t not in (corrects[True] | corrects[False]), f'answer {t} duplicated in {q["id"]}'
                corrects[c['correct']].add(t)
            for c, answers in corrects.items():
                text += '\n' + '-+'[c] + '\n' + '\n'.join(answers)
            res[q['id']] = text
        return res

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

    @encode_mapping(folder_swf + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj):
        return {v['id']: {'text': v['text'], 'crowdinContext': c.get('crowdinContext', '') + ' [' + v['tags'] + ']'}
                for c in obj
                for v in c['versions']
                if c['type'] == 'T' and not re.fullmatch(r'[a-z]+\d*[a-z]?', v['text'])}
