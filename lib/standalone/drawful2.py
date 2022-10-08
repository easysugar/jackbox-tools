from lib.game import Game, encode_mapping
from settings.drawful2 import *


class Drawful2(Game):
    @encode_mapping('data/drawful2/encoded/expanded.json', 'data/drawful2/encoded/audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {
            v['id']: v['text'].replace('[category=host]', '').strip() for c in obj for v in c['versions']
            if c['type'] == 'A' and v['tags'] == 'en' and not v['text'].endswith('[Unsubtitled]')
        }

    @encode_mapping('data/drawful2/encoded/expanded.json', 'data/drawful2/encoded/text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T'
                and v['locale'] == 'en' and not v['text'].startswith('SFX/')}

    @encode_mapping(PATH_DECOY, 'data/drawful2/encoded/decoy.json')
    def encode_decoy(self, obj: dict):
        return {c['id']: c['text'].strip() for c in obj['content']}

    @encode_mapping(PATH_PROMPT, 'data/drawful2/encoded/prompt.json')
    def encode_prompt(self, obj: dict):
        return {c['id']: c['category'].strip() for c in obj['content']}
