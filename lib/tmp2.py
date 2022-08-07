import os
import json
import shutil

from lib.base import Base, encode_mapping
from settings.tmp2 import *


class TMP2(Base):
    @encode_mapping(PATH_QUIPLASH, PATH_ENCODED_QUIPLASH)
    def encode_quiplash(self, obj: dict):
        return {c['id']: c['prompt'].replace('[EventName=HOST/AltHost]', '') for c in obj['content']}

    @encode_mapping(PATH_DICTATION, PATH_ENCODED_DICTATION)
    def encode_dictation(self, obj: dict):
        return {c['id']: '\n'.join(c['text']) for c in obj['content']}

    @encode_mapping(PATH_SEQUEL, PATH_ENCODED_SEQUEL)
    def encode_sequel(self, obj: dict):
        return {
            c['id']: {
                'text': '\n'.join([c['text']['main'], c['text'].get('sub', '')]).strip()
            }
            for c in obj['content']
            if c['text'].get('main')
        }

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
