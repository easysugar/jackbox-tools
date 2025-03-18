import os

from lib.common import copy_file
from lib.game import Game, encode_mapping, decode_mapping
from settings.teeko import *


class TeeKO(Game):
    folder = '../data/tjsp/teeko/swf/'

    @encode_mapping(PATH_SLOGANS, 'data/teeko/encoded/slogans.json')
    def encode_slogans(self, obj: dict):
        return {c['id']: c['suggestion'].strip() for c in obj['content']}

    @decode_mapping(PATH_SLOGANS, PATH_BUILD_SLOGANS, PATH_SLOGANS)
    def decode_slogans(self, obj, translations):
        for c in obj['content']:
            c['suggestion'] = translations[c['id']]
        return obj

    @encode_mapping(PATH_SUGGESTIONS, 'data/teeko/encoded/suggestions.json')
    def encode_suggestions(self, obj: dict):
        return {c['id']: c['suggestion'].strip() for c in obj['content']}

    @decode_mapping(PATH_SUGGESTIONS, PATH_BUILD_SUGGESTIONS, PATH_SUGGESTIONS)
    def decode_suggestions(self, obj, translations):
        for c in obj['content']:
            c['suggestion'] = translations[c['id']]
        return obj

    @encode_mapping(PATH_SLOGAN_SUGGESTIONS, 'data/teeko/encoded/slogan_suggestions.json')
    def encode_slogan_suggestions(self, obj: dict):
        return {c['id']: c['suggestion'].strip() for c in obj['content']}

    @decode_mapping(PATH_SLOGAN_SUGGESTIONS, PATH_BUILD_SLOGAN_SUGGESTIONS, PATH_SLOGAN_SUGGESTIONS)
    def decode_slogan_suggestions(self, obj, translations):
        for c in obj['content']:
            c['suggestion'] = translations[c['id']]
        return obj

    @encode_mapping('data/teeko/encoded/expanded.json', 'data/teeko/encoded/audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'A' and v['locale'] == 'en'}

    @encode_mapping('data/teeko/encoded/expanded.json', 'data/teeko/encoded/text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T'
                and v['locale'] == 'en' and not v['text'].startswith('SFX/')}

    @decode_mapping(PATH_BUILD_AUDIO, PATH_BUILD_SUBTITLES, out=False)
    def decode_media(self, audio: dict, text: dict):
        translations = {**audio, **text}
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'expanded.json',
                               trans=translations, path_save=self.folder + 'translated_dict.txt')

    def decode_localization(self):
        self.update_localization(rf'{PATH}\Localization.json', '../build/uk/TeeKO/localization.json')

    @staticmethod
    def copy_translated_audio():
        translated = set(os.listdir(PATH_TRANSLATED_AUDIO))
        original = set(os.listdir(PATH_AUDIO))
        for file in translated:
            if file in original:
                copy_file(os.path.join(PATH_TRANSLATED_AUDIO, file), os.path.join(PATH_AUDIO, file))
