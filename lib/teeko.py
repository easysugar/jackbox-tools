from lib.game import Game, encode_mapping, decode_mappings
from settings.teeko import *


class TeeKO(Game):
    @encode_mapping(PATH_SLOGANS, 'data/teeko/encoded/slogans.json')
    def encode_slogans(self, obj: dict):
        return {c['id']: c['suggestion'].strip() for c in obj['content']}

    @decode_mappings(PATH_SLOGANS, 'data/teeko/translated/slogans.json', PATH_SLOGANS)
    def decode_slogans(self, obj, translations):
        for c in obj['content']:
            c['suggestion'] = translations[c['id']]
        return obj

    @encode_mapping(PATH_SUGGESTIONS, 'data/teeko/encoded/suggestions.json')
    def encode_suggestions(self, obj: dict):
        return {c['id']: c['suggestion'].strip() for c in obj['content']}

    @decode_mappings(PATH_SUGGESTIONS, 'data/teeko/translated/suggestions.json', PATH_SUGGESTIONS)
    def decode_suggestions(self, obj, translations):
        for c in obj['content']:
            c['suggestion'] = translations[c['id']]
        return obj

    @encode_mapping(PATH_MODERATED_SLOGANS, 'data/teeko/encoded/moderated_slogans.json')
    def encode_moderated_slogans(self, obj: dict):
        return {c['id']: c['slogan'].strip() for c in obj['content']}

    @decode_mappings(PATH_MODERATED_SLOGANS, 'data/teeko/translated/moderated_slogans.json', PATH_MODERATED_SLOGANS)
    def decode_moderated_slogans(self, obj, translations):
        for c in obj['content']:
            c['slogan'] = translations[c['id']]
        return obj

    @encode_mapping(PATH_SLOGAN_SUGGESTIONS, 'data/teeko/encoded/slogan_suggestions.json')
    def encode_slogan_suggestions(self, obj: dict):
        return {c['id']: c['suggestion'].strip() for c in obj['content']}

    @decode_mappings(PATH_SLOGAN_SUGGESTIONS, 'data/teeko/translated/slogan_suggestions.json', PATH_SLOGAN_SUGGESTIONS)
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
