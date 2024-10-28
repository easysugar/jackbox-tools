import re
from collections import defaultdict

from lib.game import Game, encode_mapping, decode_mapping, read_from_folder, write_to_folder
from paths import JPP3_PATH

PATH = JPP3_PATH + r'\games\TriviaDeath'
PATH_LEADERBOARDS = PATH + r'\leaderboards.jet'
PATH_SETTINGS = PATH + r'\settings.jet'
PATH_QUESTION = PATH + r'\content\TDQuestion.jet'
PATH_FINAL_ROUND = PATH + r'\content\TDFinalRound.jet'
PATH_WORST_RESPONSE = PATH + r'\content\TDWorstResponse.jet'
PATH_WORST_DRAWING = PATH + r'\content\TDWorstDrawing.jet'


class TMP(Game):
    folder = '../data/pp3/tmp/encoded/'
    folder_swf = '../data/pp3/tmp/swf/'
    build = '../build/uk/JPP3/TMP/'

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

    @decode_mapping(PATH_QUESTION, build + 'questions.json', PATH_QUESTION)
    def decode_question(self, obj: dict, trans: dict):
        for c in obj['content']:
            cid = str(c['id'])
            if cid not in trans:
                continue
            text, *choices, answer = trans[cid].strip().split('\n')
            answer = int(answer)
            assert answer in (1, 2, 3, 4), f"incorrect answer {answer}, context: {text}"
            assert len(choices) == 4, f'there are should be 4 choices, not {len(choices)}. Context: {text}'
            c['text'] = text.strip()
            for i in range(4):
                c['choices'][i]['text'] = choices[i].strip()
                c['choices'][i]['correct'] = i + 1 == answer
        return obj

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

    @decode_mapping(PATH_FINAL_ROUND, build + 'final_questions.json', PATH_FINAL_ROUND)
    def decode_final_round(self, obj: dict, trans: dict):
        for c in obj['content']:
            cid = str(c['id'])
            text, *answers = trans[cid].strip().split('\n')
            c['text'] = text.strip()
            assert len(answers) > 1
            corrects = defaultdict(set)
            sign = None
            for a in answers:
                a = a.strip()
                if a in ('+', '-'):
                    sign = a
                else:
                    assert sign is not None, f'incorrect sign {sign}, text {text}'
                    corrects[sign].add(a)
            c['choices'] = [{'text': a.strip(), 'correct': s == '+', 'easy': 0} for s, alist in corrects.items() for a in alist]
        return obj

    @encode_mapping(PATH_LEADERBOARDS, folder + 'leaderboards.json')
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

    @encode_mapping(PATH_SETTINGS, folder + 'settings.json')
    def encode_settings(self, obj):
        return {
            i['source']: {'title': i['title'], 'description': i['description']} for i in obj['items']
        }

    @decode_mapping(PATH_SETTINGS, build + 'settings.json', PATH_SETTINGS)
    def decode_settings(self, obj, trans):
        for i in obj['items']:
            i['title'] = trans[i['source']]['title']
            i['description'] = trans[i['source']]['description']
        return obj

    @encode_mapping(folder_swf + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj):
        return {v['id']: {'text': v['text'], 'crowdinContext': c.get('crowdinContext', '') + ' [' + v['tags'] + ']'}
                for c in obj
                for v in c['versions']
                if c['type'] == 'T' and not re.fullmatch(r'[a-z]+\d*[a-z]?', v['text'])}

    @encode_mapping(folder_swf + 'expanded.json', folder + 'audio.json')
    def encode_audio_subtitles(self, obj):
        return {
            v['id']: {'text': v['text'], 'crowdinContext': c.get('crowdinContext', '')}
            for c in obj for v in c['versions']
            if c['type'] == 'A'
               and c['versions']
               and 'SFX' not in c['versions'][0]['text']
               and 'Music Loops' not in c['versions'][0]['text']
               and ' Background' not in c['versions'][0]['text']
               and '\n' not in c['versions'][0]['text'].strip()
               and 'TEMP' not in c['versions'][0]['text']
               and 'Die' not in c['versions'][0]['tags']
        }

    def decode_media(self):
        audio = {}
        text = self._read_json(self.build + 'text_subtitles.json')
        text = {k: v['text'] for k, v in text.items()}
        self._decode_swf_media(path_media=self.folder_swf + 'dict.txt', path_expanded=self.folder_swf + 'expanded.json',
                               trans=audio | text, path_save=self.folder_swf + 'translated_dict.txt', ignore_tags=True)

    @decode_mapping(PATH_WORST_RESPONSE, folder + 'worst_response.json')
    def encode_worst_response(self, obj):
        result = {}
        for c in obj['content']:
            cid = str(c['id'])
            o = read_from_folder(cid, PATH_WORST_RESPONSE)
            result[cid] = o['QuestionText']['v']
        return result

    @decode_mapping(PATH_WORST_RESPONSE, build + 'worst_response.json', PATH_WORST_RESPONSE)
    def decode_worst_response(self, obj, trans):
        for c in obj['content']:
            cid = str(c['id'])
            o = read_from_folder(cid, PATH_WORST_RESPONSE)
            o['QuestionText']['v'] = trans[cid]
            o['Category']['v'] = trans[cid]
            write_to_folder(cid, PATH_WORST_RESPONSE, o)
        return obj

    @decode_mapping(PATH_WORST_DRAWING, folder + 'worst_drawing.json')
    def encode_worst_drawing(self, obj):
        result = {}
        for c in obj['content']:
            cid = str(c['id'])
            result[cid] = c['category']
        return result

    @decode_mapping(PATH_WORST_DRAWING, build + 'worst_drawing.json', PATH_WORST_DRAWING)
    def decode_worst_drawing(self, obj, trans):
        for c in obj['content']:
            cid = str(c['id'])
            c['category'] = trans[cid]
            o = read_from_folder(cid, PATH_WORST_DRAWING)
            o['QuestionText']['v'] = trans[cid]
            write_to_folder(cid, PATH_WORST_DRAWING, o)
        return obj
