import os

from lib.game import Game, encode_mapping, read_json
from settings.drawful2 import *


class Drawful2(Game):
    folder = 'data/standalone/drawful2/encoded/'

    @encode_mapping(folder + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {
            v['id']: v['text'].replace('[category=host]', '').strip() for c in obj for v in c['versions']
            if c['type'] == 'A' and v['tags'] == 'en' and not v['text'].endswith('[Unsubtitled]')
        }

    @encode_mapping(folder + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T'
                and v['locale'] == 'en' and not v['text'].startswith('SFX/')}

    @encode_mapping(PATH_DECOY, folder + 'decoy.json')
    def encode_decoy(self, obj: dict):
        return {c['id']: c['text'].strip() for c in obj['content']}

    @encode_mapping(PATH_PROMPT, folder + 'prompt.json')
    def encode_prompt(self, obj: dict):
        result = {}
        for c in obj['content']:
            cid = str(c['id'])
            path = os.path.join(PATH_PROMPT_DIR, cid, 'data.jet')
            x = read_json(path)
            x = {_['n']: _ for _ in x['fields']}
            text = x['QuestionText']['v'].strip()
            # alternate = [_.strip() for _ in x['AlternateSpellings']['v'].split('|')]
            audio = None if 'JokeAudio' not in x else x['JokeAudio']['s'].strip()
            body = text
            if audio:
                assert '\n' not in audio
                body += '\n' + audio
            result[cid] = body
        return result
