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
