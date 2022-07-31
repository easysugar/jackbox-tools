import os
import json
import shutil

from settings.quiplash import *

from lib.base import Base


class NotFoundPromptTextException(Exception):
    pass


class NotFoundPromptAudioException(Exception):
    pass


class Quiplash(Base):
    def __init__(self):
        self.translations = {}
        self._read_questions_json()

    def _read_questions_json(self):
        obj = self._read_json(PATH_QUESTIONS_JSON)
        self.translations = {i['id']: i['prompt'] for i in obj['content']}

    def _update_question_obj(self, oid: int, obj: dict):
        text = self.translations[oid]
        text = text.replace('ʼ', "'")
        fields = obj['fields']
        for f in fields:
            if f['n'] == 'PromptText':
                f['v'] = text
            if f['n'] == 'PromptAudio':
                f['s'] = text
        if 'PromptText' not in {f['n'] for f in fields}:
            raise NotFoundPromptTextException
        if 'PromptAudio' not in {f['n'] for f in fields}:
            raise NotFoundPromptAudioException

    def _rewrite_question(self, oid: int, path: str):
        obj = self._read_json(path)
        self._update_question_obj(oid, obj)
        self._write_json(path, obj)

    def unpack(self):
        dirs = os.listdir(PATH_QUESTIONS)
        for folder in dirs:
            if folder.isdigit():
                self._rewrite_question(int(folder), os.path.join(PATH_QUESTIONS, folder, 'data.jet'))

    def copy_to_release(self):
        dirs = os.listdir(PATH_QUESTIONS)
        for folder in dirs:
            if not folder.isdigit():
                continue
            dst_folder = os.path.join(PATH_RELEASE, 'content', 'QuiplashQuestion', folder)
            if not os.path.isdir(dst_folder):
                os.mkdir(dst_folder)
            shutil.copyfile(os.path.join(PATH_QUESTIONS, folder, 'data.jet'), os.path.join(dst_folder, 'data.jet'))

    def encode_quiplash_questions(self, src: str, dst: str):
        obj = self._read_json(src)
        obj = {c.pop('id'): c['prompt'] for c in obj['content']}
        self._write_json(dst, obj)
