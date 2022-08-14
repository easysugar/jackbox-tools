import os
import json
import shutil

from lib.base import Base, encode_mapping
from settings.tmp2 import *


class TMP2(Base):
    @encode_mapping(PATH_QUIPLASH, PATH_ENCODED_QUIPLASH)
    def encode_quiplash(self, obj: dict):
        return {c['id']: c['prompt'].replace('[EventName=HOST/AltHost]', '') for c in obj['content']}

    def decode_quiplash(self, translated_path: str, save_path: str):
        obj = self._read_json(PATH_QUIPLASH)
        translations = self._read_json(translated_path)
        for c in obj['content']:
            c['prompt'] = '[EventName=HOST/AltHost]' + translations[c['id']]
        self._write_json(save_path, obj)

    @encode_mapping(PATH_DICTATION, PATH_ENCODED_DICTATION)
    def encode_dictation(self, obj: dict):
        return {c['id']: '\n'.join(c['text']) for c in obj['content']}

    def decode_dictation(self, translated_path: str, save_path: str):
        obj = self._read_json(PATH_DICTATION)
        translations = self._read_json(translated_path)
        for c in obj['content']:
            c['text'] = translations[c['id']].strip().split('\n')
        self._write_json(save_path, obj)

    @encode_mapping(PATH_SEQUEL, PATH_ENCODED_SEQUEL)
    def encode_sequel(self, obj: dict):
        return {
            c['id']: {
                'text': '\n'.join([c['text']['main'], c['text'].get('sub', '')]).strip()
            }
            for c in obj['content']
            if c['text'].get('main')
        }

    def decode_sequel(self, translated_path: str, save_path: str):
        obj = self._read_json(PATH_SEQUEL)
        translations = self._read_json(translated_path)
        for c in obj['content']:
            if c['text'].get('main'):
                t = translations[c['id']]['text'].strip().split('\n')
                c['text']['main'] = t[0]
                if len(t) > 1:
                    c['text']['sub'] = t[1]
        self._write_json(save_path, obj)

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
