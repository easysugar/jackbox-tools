import os
import json
import shutil

from lib.base import Base, encode_mapping
from settings.teeko import *


class TeeKO(Base):
    @encode_mapping(PATH_SLOGANS, 'data/teeko/slogans.json')
    def encode_slogans(self, obj: dict):
        return {c['id']: c['suggestion'].strip() for c in obj['content']}

    @encode_mapping(PATH_SUGGESTIONS, 'data/teeko/suggestions.json')
    def encode_suggestions(self, obj: dict):
        return {c['id']: c['suggestion'].strip() for c in obj['content']}

    @encode_mapping(PATH_MODERATED_SLOGANS, 'data/teeko/moderated_slogans.json')
    def encode_moderated_slogans(self, obj: dict):
        return {c['id']: c['slogan'].strip() for c in obj['content']}

    @encode_mapping(PATH_SLOGAN_SUGGESTIONS, 'data/teeko/slogan_suggestions.json')
    def encode_slogan_suggestions(self, obj: dict):
        return {c['id']: c['suggestion'].strip() for c in obj['content']}

    @encode_mapping('data/teeko/AwShirt_StarterPack_GameMain_Expanded.json', 'data/teeko/audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'A' and v['locale'] == 'en'}
