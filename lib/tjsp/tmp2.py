import os
import random
import re
from collections import defaultdict

import pandas as pd
import tqdm

from lib.common import read_json
from lib.drive import Drive
from lib.game import Game, encode_mapping, decode_mapping, copy_file, read_from_folder, write_to_folder
from settings.tmp2 import *

subtitles_technical_regex = r'\w+/\w+|[a-z]+\d?|\{\{.*|(intro|TD|GAMEPLAY_)\w+|(MUSIC|SFX|HOST)/.*'
random.seed(34)


class TMP2(Game):
    folder = '../data/tjsp/tmp2/'

    # DICTATION

    @encode_mapping(PATH_DICTATION, PATH_ENCODED_DICTATION)
    def encode_dictation(self, obj: dict):
        return {c['id']: '\n'.join(c['text']) for c in obj['content']}

    @decode_mapping(PATH_DICTATION, PATH_BUILD_DICTATION, PATH_DICTATION)
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

    @decode_mapping(PATH_SEQUEL, PATH_BUILD_SEQUEL, PATH_SEQUEL)
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
            cid = str(c['id'])
            path = os.path.join(PATH_QUESTION_DIR, cid, 'data.jet')
            x = read_json(path)
            x = {_['n']: _ for _ in x['fields']}
            intro = None
            if x.get('HasIntro', {}).get('v') == 'true' and x['Intro'].get('s'):
                intro = x['Intro']['s'].strip()
            assert corrects.count(True) == 1
            answer = corrects.index(True) + 1
            result[c['id']] = '{}\n{}\n{}'.format(
                c['text'],
                '\n'.join([i['text'] for i in c['choices']]),
                answer,
            )
            if intro:
                result[c['id']] = intro + '\n' + result[c['id']]
        return result

    @decode_mapping(PATH_QUESTION, PATH_BUILD_QUESTION, PATH_QUESTION)
    def decode_question(self, obj: dict, trans: dict):
        for c in obj['content']:
            cid = str(c['id'])
            if len(trans[c['id']].strip().split('\n')) == 7:
                intro, text, *choices, answer = trans[c['id']].strip().split('\n')
            else:
                text, *choices, answer = trans[c['id']].strip().split('\n')
                intro = None
            answer = int(answer)
            assert answer in (1, 2, 3, 4)
            assert len(choices) == 4, f'there are should be 4 choices, not {len(choices)}. Context: {text}'
            c['text'] = text.strip()
            for i in range(4):
                c['choices'][i]['text'] = choices[i].strip()
                c['choices'][i]['correct'] = i + 1 == answer
            # write question intro
            o = read_from_folder(cid, PATH_QUESTION_DIR)
            if o.get('HasIntro', {}).get('v') == 'true' and o['Intro'].get('s'):
                assert intro is not None, f'Intro should be here: {o["Intro"]["s"]} ({cid})'
                o['Intro']['s'] = intro
            else:
                assert intro is None, f'Intro is not supposed to be here: {intro} {cid}'
            write_to_folder(cid, PATH_QUESTION_DIR, o)
        return obj

    # @decode_mapping(PATH_QUESTION, PATH_BUILD_QUESTION, PATH_QUESTION)
    # def decode_question(self, obj, trans):
    #     return self._decode_question_template(obj, trans)

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

    def _rewrite_final_question(self, translations: dict, oid: int, path: str):
        obj = self._read_json(path)
        text = translations[oid]
        text = text.replace('ʼ', "'")
        fields = obj['fields']
        assert len([f for f in fields if f['v'] == 'question']) == 1
        for f in fields:
            if f['v'] == 'question':
                f['s'] = text
        self._write_json(path, obj)

    def _unpack_template(self, file, directory, callback, field='text'):
        obj = self._read_json(file)
        translations = {int(i['id']): i[field] for i in obj['content']}
        dirs = os.listdir(directory)
        for folder in dirs:
            if folder.isdigit():
                callback(translations, int(folder), os.path.join(directory, folder, 'data.jet'))

    def unpack_question(self):
        return self._unpack_template(PATH_QUESTION, PATH_QUESTION_DIR, self._rewrite_question)

    def unpack_final_round(self):
        return self._unpack_template(PATH_FINAL_ROUND, PATH_FINAL_ROUND_DIR, self._rewrite_final_question)

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

    @decode_mapping(PATH_FINAL_ROUND, PATH_BUILD_FINAL_ROUND, PATH_FINAL_ROUND)
    def decode_final_round(self, obj, trans):
        for c in obj['content']:
            text, *answers = trans[c['id']].strip().split('\n')
            c['text'] = text.strip()
            assert len(answers) > 1
            corrects = defaultdict(set)
            sign = None
            for a in answers:
                if a in ('+', '-'):
                    sign = a
                else:
                    assert sign is not None
                    corrects[sign].add(a)
            c['choices'] = [{'text': a.strip(), 'correct': s == '+', 'difficulty': 0} for s, alist in corrects.items() for a in alist]
            random.shuffle(c['choices'])
        return obj

    @staticmethod
    def _encode_question_template(obj: dict, host=False, question_folder: str = None):
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
            if question_folder:
                o = read_from_folder(c['id'], question_folder)
                if intro := o.get('Intro', {}).get('s'):
                    result[c['id']] = intro + '\n' + result[c['id']]
        return result

    @staticmethod
    def _decode_question_template(obj, trans, host=False, question_folder: str = None):
        prefix = '' if not host else '[EventName=HOST/AltHost]'
        for c in obj['content']:
            cid = c['id']
            if len(trans[c['id']].strip().split('\n')) == 6:
                text, *choices, answer = trans[c['id']].strip().split('\n')
                intro = None
            else:
                intro, text, *choices, answer = trans[c['id']].strip().split('\n')
            answer = int(answer)
            assert answer in (1, 2, 3, 4)
            assert len(choices) == 4, f'there are should be 4 choices, not {len(choices)}. Context: {text}'
            c['text'] = prefix + text.strip()
            for i in range(4):
                c['choices'][i]['text'] = choices[i].strip()
                c['choices'][i]['correct'] = i + 1 == answer

            if intro:
                assert question_folder is not None, f'Question {cid} has intro "{intro}", but question_folder is not provided.'
                o = read_from_folder(cid, question_folder)
                if o.get('HasIntro', {}).get('v') == 'true' and o['Intro'].get('s'):
                    assert intro is not None, f'Intro should be here: {o["Intro"]["s"]} ({cid})'
                    o['Intro']['s'] = '[EventName=HOST/AltHost]' + intro
                else:
                    assert intro is None, f'Intro is not supposed to be here: {intro} {cid}'
                write_to_folder(cid, question_folder, o)
        return obj

    # HAT

    @encode_mapping(PATH_QUESTION_HAT, 'data/tmp2/EncodedQuestionHat.json')
    def encode_question_hat(self, obj):
        return self._encode_question_template(obj)

    @decode_mapping(PATH_QUESTION_HAT, PATH_BUILD_QUESTION_HAT, PATH_QUESTION_HAT)
    def decode_question_hat(self, obj, trans):
        return self._decode_question_template(obj, trans)

    def unpack_question_hat(self):
        return self._unpack_template(PATH_QUESTION_HAT, PATH_QUESTION_HAT_DIR, self._rewrite_question)

    # WIG

    @encode_mapping(PATH_QUESTION_WIG, 'data/tmp2/EncodedQuestionWig.json')
    def encode_question_wig(self, obj):
        return self._encode_question_template(obj)

    @decode_mapping(PATH_QUESTION_WIG, PATH_BUILD_QUESTION_WIG, PATH_QUESTION_WIG)
    def decode_question_wig(self, obj, trans):
        return self._decode_question_template(obj, trans)

    def unpack_question_wig(self):
        return self._unpack_template(PATH_QUESTION_WIG, PATH_QUESTION_WIG_DIR, self._rewrite_question)

    # GHOST

    @encode_mapping(PATH_QUESTION_GHOST, 'data/tmp2/encoded/question_ghost.json')
    def encode_question_ghost(self, obj):
        return self._encode_question_template(obj, True)

    @decode_mapping(PATH_QUESTION_GHOST, PATH_BUILD_QUESTION_GHOST, PATH_QUESTION_GHOST)
    def decode_question_ghost(self, obj, trans):
        return self._decode_question_template(obj, trans, True)

    def unpack_question_ghost(self):
        return self._unpack_template(PATH_QUESTION_GHOST, PATH_QUESTION_GHOST_DIR, self._rewrite_question)

    # BOMB

    @encode_mapping(PATH_QUESTION_BOMB, 'data/tmp2/encoded/question_bomb.json')
    def encode_question_bomb(self, obj):
        return self._encode_question_template(obj, True)

    @decode_mapping(PATH_QUESTION_BOMB, PATH_BUILD_QUESTION_BOMB, PATH_QUESTION_BOMB)
    def decode_question_bomb(self, obj, trans):
        res = self._decode_question_template(obj, trans, True)
        colors = {
            'жовтий': 'yellow',
            'синій': 'blue',
            'зелений': 'green',
            'білий': 'white',
            'червоний': 'red',
            'оранжевий': 'orange',
            'фіолетовий': 'purple',
            'чорний': 'black',
            'блакитний': 'blue',
        }
        for i in res['content']:
            for c in i['choices']:
                c['controllerClass'] = colors[c['text']]
        return res

    def unpack_question_bomb(self):
        return self._unpack_template(PATH_QUESTION_BOMB, PATH_QUESTION_BOMB_DIR, self._rewrite_question)

    # KNIFE

    @encode_mapping(PATH_QUESTION_KNIFE, '../data/tmp2/encoded/question_knife.json')
    def encode_question_knife(self, obj):
        return self._encode_question_template(obj, True, PATH_QUESTION_KNIFE_DIR)

    @decode_mapping(PATH_QUESTION_KNIFE, PATH_BUILD_QUESTION_KNIFE, PATH_QUESTION_KNIFE)
    def decode_question_knife(self, obj, trans):
        return self._decode_question_template(obj, trans, True, PATH_QUESTION_KNIFE_DIR)

    def unpack_question_knife(self):
        return self._unpack_template(PATH_QUESTION_KNIFE, PATH_QUESTION_KNIFE_DIR, self._rewrite_question)

    # MADNESS

    @encode_mapping(PATH_QUESTION_MADNESS, 'data/tmp2/encoded/question_madness.json')
    def encode_question_madness(self, obj):
        return self._encode_question_template(obj, True)

    @decode_mapping(PATH_QUESTION_MADNESS, PATH_BUILD_QUESTION_MADNESS, PATH_QUESTION_MADNESS)
    def decode_question_madness(self, obj, trans):
        return self._decode_question_template(obj, trans, True)

    def unpack_question_madness(self):
        return self._unpack_template(PATH_QUESTION_MADNESS, PATH_QUESTION_MADNESS_DIR, self._rewrite_question)

    # QUIPLASH

    @encode_mapping(PATH_QUIPLASH, PATH_ENCODED_QUIPLASH)
    def encode_quiplash(self, obj: dict):
        return {c['id']: c['prompt'].replace('[EventName=HOST/AltHost]', '') for c in obj['content']}

    @decode_mapping(PATH_QUIPLASH, PATH_BUILD_QUIPLASH, PATH_QUIPLASH)
    def decode_quiplash(self, obj, translations):
        for c in obj['content']:
            c['prompt'] = '[EventName=HOST/AltHost]' + translations[c['id']]
        return obj

    def _rewrite_quiplash(self, translations: dict, oid: int, path: str):
        obj = self._read_json(path)
        text = '[EventName=HOST/AltHost]' + translations[oid]
        text = text.replace('ʼ', "'")
        fields = obj['fields']
        assert len([f for f in fields if f['n'] == 'PromptAudio']) == 1
        assert len([f for f in fields if f['n'] == 'PromptText']) == 1
        assert [f for f in fields if f['n'] == 'PromptAudio'][0]['s'] == [f for f in fields if f['n'] == 'PromptText'][0]['v']
        for f in fields:
            if f['n'] == 'PromptAudio':
                f['s'] = text
            if f['n'] == 'PromptText':
                f['v'] = text
        self._write_json(path, obj)

    def unpack_quiplash(self):
        return self._unpack_template(PATH_QUIPLASH, PATH_QUIPLASH_DIR, self._rewrite_quiplash, field='prompt')

    # MIRROR

    @encode_mapping(PATH_MIRROR_TUTORIAL, 'data/tmp2/encoded/mirror_tutorial.json')
    def encode_mirror_tutorial(self, obj):
        return {c['id']: c['password'] for c in obj['content']}

    @decode_mapping(PATH_MIRROR_TUTORIAL, PATH_BUILD_MIRROR_TUTORIAL, PATH_MIRROR_TUTORIAL)
    def decode_mirror_tutorial(self, obj, translations):
        for c in obj['content']:
            c['password'] = translations[c['id']]
        return obj

    @encode_mapping(PATH_MIRROR, 'data/tmp2/encoded/mirror.json')
    def encode_mirror(self, obj):
        return {c['id']: c['password'] for c in obj['content']}

    @decode_mapping(PATH_MIRROR, PATH_BUILD_MIRROR, PATH_MIRROR)
    def decode_mirror(self, obj, translations):
        for c in obj['content']:
            c['password'] = translations[c['id']]
        return obj

    # MIND MELD

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

    @decode_mapping(PATH_MIND_MELD, PATH_BUILD_MIND_MELD, PATH_MIND_MELD)
    def decode_mind_meld(self, obj, trans):
        separator = ', '
        for c in obj['content']:
            t = trans[c['id']]
            prompt, *answers = t.strip().split('\n')
            c['text'] = prompt
            c['answers'] = []
            for a in answers:
                atext, *alt = a.strip().split(separator)
                c['answers'].append({
                    'answer': atext,
                    'alt': [atext] if not alt else list(alt),
                })
        return obj

    @staticmethod
    def decode_rules_wordlist():
        copy_file(PATH_BUILD_WORDLIST_RULES, PATH_WORDLIST_RULES)

    def decode_media(self):
        audio = self._read_json(PATH_BUILD_AUDIO)
        text = self._read_json(PATH_BUILD_SUBTITLES)
        text = {k: text for v in text.values() for k, text in v.items()}
        translations = {**audio, **text}
        self._decode_swf_media(
            path_media=PATH_SOURCE_DICT,
            path_expanded=PATH_EXPANDED,
            trans=translations,
            path_save=PATH_TRANSLATED_DICT,
        )

    def decode_localization(self):
        self.update_localization(rf'{PATH}\Localization.json', '../build/uk/TMP2/LocalizationEN.json')

    def upload_audio_main(self):
        d = Drive()
        original = self._read_json(self.folder + 'encoded/EncodedAudio.json')
        expanded = self._read_json(self.folder + 'encoded/expanded.json')
        context = {v['id']: c['crowdinContext'] for c in expanded for v in c['versions'] if c.get('crowdinContext')}
        skip = {v['id'] for c in expanded for v in c['versions'] if 'AltHost' in v['text']}
        tags = {v['id']: v['tags'] for c in expanded for v in c['versions']}
        obj = self._read_json(PATH_BUILD_AUDIO)
        exists = d.get_uploaded_files(PATH_DRIVE_MAIN)
        data = []
        for cid in tqdm.tqdm(sorted(original)):
            ogg = f'{cid}.ogg'
            if cid in skip:
                continue
            data.append({
                'id': cid,
                'tag': tags[cid],
                'context': context.get(cid),
                'original': original[cid].strip().replace('\n', ' '),
                'translation': obj[cid].strip().replace('\n', ' '),
            })
            if ogg not in exists:
                file = os.path.join(PATH_MEDIA, ogg)
                d.copy_to_drive(PATH_DRIVE_MAIN, file, ogg)
        links = d.get_files_links(path_drive=PATH_DRIVE_MAIN)
        for i in data:
            i['link'] = links[i['id']]
        pd.DataFrame(data).to_csv(self.folder + 'audio_main.tsv', sep='\t', encoding='utf8', index=False)

    def upload_audio_madness(self):
        d = Drive(PATH_DRIVE_MADNESS)
        expanded = self._read_json(self.folder + 'encoded/expanded.json')
        cids = {str(v['id']) for c in expanded for v in c['versions'] if 'weird doctor' in v['text'].lower() and v['locale'] == 'en'}
        data = []
        obj = self._read_json(PATH_BUILD_AUDIO)
        for cid in tqdm.tqdm(cids):
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg, 'text': obj[cid].strip().replace('\n', ' ')})
            d.upload(PATH_MEDIA, ogg)

        questions = self._read_json(PATH_BUILD_QUESTION_MADNESS)
        for cid, q in questions.items():
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg, 'text': q.strip().split('\n')[0]})
            d.upload(PATH_QUESTION_MADNESS_DIR, cid, 'questionAudio.ogg', name=ogg)

        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio_weird_doctor.tsv', sep='\t', encoding='utf8', index=False)

    def upload_audio_bomb(self):
        d = Drive(PATH_DRIVE_BOMB)
        expanded = self._read_json(self.folder + 'encoded/expanded.json')
        cids = {str(v['id']) for c in expanded for v in c['versions'] if 'cop:' in v['text'].lower() and v['locale'] == 'en'}
        data = []
        obj = self._read_json(PATH_BUILD_AUDIO)
        for cid in tqdm.tqdm(cids):
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg, 'text': obj[cid].strip().replace('\n', ' ')})
            d.upload(PATH_MEDIA, ogg)

        questions = self._read_json(PATH_BUILD_QUESTION_BOMB)
        for cid, q in questions.items():
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg, 'text': q.strip().split('\n')[0]})
            d.upload(PATH_QUESTION_BOMB_DIR, cid, 'questionAudio.ogg', name=ogg)

        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio_cop_bomb.tsv', sep='\t', encoding='utf8', index=False)
