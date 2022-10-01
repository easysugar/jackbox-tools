import os
import re
from collections import defaultdict

from lib.game import Game, encode_mapping, decode_mapping
from settings.tmp2 import *

subtitles_technical_regex = r'\w+/\w+|[a-z]+\d?|\{\{.*|(intro|TD|GAMEPLAY_)\w+|(MUSIC|SFX|HOST)/.*'


class TMP2(Game):
    @encode_mapping(PATH_QUIPLASH, PATH_ENCODED_QUIPLASH)
    def encode_quiplash(self, obj: dict):
        return {c['id']: c['prompt'].replace('[EventName=HOST/AltHost]', '') for c in obj['content']}

    @decode_mapping(PATH_QUIPLASH, 'build/uk/TMP2/in-game/EncodedTMP2QuiplashContent.json', 'data/tmp2/decoded/quiplash.json')
    def decode_quiplash(self, obj, translations):
        for c in obj['content']:
            c['prompt'] = '[EventName=HOST/AltHost]' + translations[c['id']]
        return obj

    @encode_mapping(PATH_DICTATION, PATH_ENCODED_DICTATION)
    def encode_dictation(self, obj: dict):
        return {c['id']: '\n'.join(c['text']) for c in obj['content']}

    @decode_mapping(PATH_DICTATION, 'build/uk/TMP2/in-game/EncodedTMP2Dictation.json', 'data/tmp2/decoded/dictation.json')
    def decode_dictation(self, obj, translations):
        for c in obj['content']:
            c['text'] = translations[c['id']].strip().split('\n')
        return obj

    @encode_mapping(PATH_SEQUEL, PATH_ENCODED_SEQUEL)
    def encode_sequel(self, obj: dict):
        return {
            c['id']: {
                'text': '\n'.join([c['text']['main'], c['text'].get('sub', '')]).strip()
            }
            for c in obj['content']
            if c['text'].get('main')
        }

    @decode_mapping(PATH_SEQUEL, 'build/uk/TMP2/in-game/EncodedTDSequel.json', 'data/tmp2/decoded/sequel.json')
    def decode_sequel(self, obj, translations):
        for c in obj['content']:
            if c['text'].get('main'):
                t = translations[c['id']]['text'].strip().split('\n')
                c['text']['main'] = t[0]
                if len(t) > 1:
                    c['text']['sub'] = t[1]
        return obj

    @encode_mapping(PATH_QUESTION, PATH_ENCODED_QUESTION)
    def encode_question(self, obj: dict):
        assert len({c['id'] for c in obj['content']}) == len(obj['content'])
        result = {}
        for c in obj['content']:
            assert c['id'] not in result
            assert c['text'] is not None
            assert len(c['choices']) == 4
            corrects = [i['correct'] for i in c['choices']]
            assert corrects.count(True) == 1
            answer = corrects.index(True) + 1
            result[c['id']] = '{}\n{}\n{}'.format(
                c['text'],
                '\n'.join([i['text'] for i in c['choices']]),
                answer
            )
        return result

    def _rewrite_question(self, translations: dict, oid: int, path: str):
        obj = self._read_json(path)
        text = translations[oid]
        text = text.replace('ʼ', "'")
        fields = obj['fields']
        assert len([f for f in fields if f['v'] == 'questionAudio']) == 1
        for f in fields:
            if f['v'] == 'questionAudio':
                f['s'] = text
        self._write_json(path, obj)

    def unpack_question(self):
        obj = self._read_json(PATH_QUESTION)
        translations = {int(i['id']): i['text'] for i in obj['content']}
        dirs = os.listdir(PATH_QUESTION_DIR)
        for folder in dirs:
            if folder.isdigit():
                self._rewrite_question(translations, int(folder), os.path.join(PATH_QUESTION_DIR, folder, 'data.jet'))

    @encode_mapping('data/tmp2/encoded/expanded.json', 'data/tmp2/encoded/text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        result = defaultdict(dict)
        for c in obj:
            # use only text subtitles
            if c['type'] != 'T':
                continue
            # get fr text for comparing
            fr_versions = defaultdict(set)
            for v in c['versions']:
                if v['locale'] == 'fr':
                    fr_versions[v['tags']].add(v['text'])

            for v in c['versions']:
                if v['locale'] == 'en':
                    if v['tags'] not in fr_versions:
                        # print('[NOT FOUND]', v['tags'], ':', v['text'])
                        assert re.fullmatch(subtitles_technical_regex, v['text'].strip())  # technical text
                    elif v['text'] not in fr_versions[v['tags']]:
                        assert v['id'] not in result[v['tags']]
                        result[v['tags']][v['id']] = v['text']
                    else:
                        # print('[DUPLICATED]', v['tags'], ':', v['text'])
                        assert re.fullmatch(subtitles_technical_regex, v['text'].strip())  # technical text
        return result

    @encode_mapping(PATH_FINAL_ROUND, 'data/tmp2/encoded/final_questions.json')
    def encode_final_round(self, obj: dict):
        res = {}
        for q in obj['content']:
            assert set(q) == {'choices', 'id', 'isValid', 'text', 'us', 'x'}
            assert q['isValid'] == ''
            text = q['text']
            corrects = defaultdict(set)
            for c in q['choices']:
                assert set(c) == {'correct', 'difficulty', 'text'}
                assert c['correct'] in (True, False)
                assert c['difficulty'] in (-1, 0, 1)
                assert c['text'].strip()
                t = c['text'].strip()
                # assert t not in (corrects[True] | corrects[False]), f'answer {t} duplicated in {q["id"]}'
                corrects[c['correct']].add(t)
            for c, answers in corrects.items():
                text += '\n' + '-+'[c] + '\n' + '\n'.join(answers)
            res[q['id']] = text
        return res

    def encode_question_template(self, obj: dict, host=False):
        assert len({c['id'] for c in obj['content']}) == len(obj['content'])
        result = {}
        for c in obj['content']:
            assert c['id'] not in result
            assert c['text'] is not None
            assert len(c['choices']) == 4
            assert not c['pic']
            corrects = [i['correct'] for i in c['choices']]
            assert corrects.count(True) == 1
            answer = corrects.index(True) + 1
            result[c['id']] = '{}\n{}\n{}'.format(
                c['text'].replace('[EventName=HOST/AltHost]', '') if host else c['text'],
                '\n'.join([i['text'] for i in c['choices']]),
                answer
            )
        return result

    @encode_mapping(PATH_QUESTION_HAT, 'data/tmp2/EncodedQuestionHat.json')
    def encode_question_hat(self, obj):
        return self.encode_question_template(obj)

    @encode_mapping(PATH_QUESTION_WIG, 'data/tmp2/EncodedQuestionWig.json')
    def encode_question_wig(self, obj):
        return self.encode_question_template(obj)

    @encode_mapping(PATH_QUESTION_GHOST, 'data/tmp2/encoded/question_ghost.json')
    def encode_question_ghost(self, obj):
        return self.encode_question_template(obj, True)

    @encode_mapping(PATH_QUESTION_BOMB, 'data/tmp2/encoded/question_bomb.json')
    def encode_question_bomb(self, obj):
        return self.encode_question_template(obj, True)

    @encode_mapping(PATH_QUESTION_KNIFE, 'data/tmp2/encoded/question_knife.json')
    def encode_question_knife(self, obj):
        return self.encode_question_template(obj, True)

    @encode_mapping(PATH_QUESTION_MADNESS, 'data/tmp2/encoded/question_madness.json')
    def encode_question_madness(self, obj):
        return self.encode_question_template(obj, True)

    @encode_mapping(PATH_MIRROR_TUTORIAL, 'data/tmp2/encoded/mirror_tutorial.json')
    def encode_mirror_tutorial(self, obj):
        return {c['id']: c['password'] for c in obj['content']}

    @encode_mapping(PATH_MIRROR, 'data/tmp2/encoded/mirror.json')
    def encode_mirror(self, obj):
        return {c['id']: c['password'] for c in obj['content']}

    @encode_mapping(PATH_MIND_MELD, 'data/tmp2/encoded/mind_meld.json')
    def encode_mind_meld(self, obj):
        separator = ', '
        result = {}
        for c in obj['content']:
            answers = []
            for a in c['answers']:
                assert a['answer'] not in a['alt']
                alts = []
                for ans in [a['answer']] + a['alt']:
                    if ans != '':
                        assert separator.strip() not in ans
                        alts.append(ans)
                answers.append(separator.join(alts))
            result[c['id']] = c['text'] + '\n' + '\n'.join(answers)
        return result
