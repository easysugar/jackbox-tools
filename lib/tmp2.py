import os
import json
import shutil

from lib.base import Base
from settings.tmp2 import *


class TMP2(Base):
    def encode_quiplash(self, path: str = None):
        path = path or 'data/tmp2/EncodedTMP2QuiplashContent.json'
        obj = self._read_json(PATH_QUIPLASH)
        obj = {c['id']: c['prompt'].replace('[EventName=HOST/AltHost]', '') for c in obj['content']}
        self._write_json(path, obj)

    def encode_dictation(self, path: str = None):
        path = path or 'data/tmp2/EncodedTMP2Dictation.json'
        obj = self._read_json(PATH_DICTATION)
        obj = {c['id']: '\n'.join(c['text']) for c in obj['content']}
        self._write_json(path, obj)
