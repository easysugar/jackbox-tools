import os

from lib.game import Game, encode_mapping, read_json, decode_mapping, read_from_folder, write_to_folder
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

    @decode_mapping(PATH_DECOY, PATH_BUILD_DECOY, PATH_DECOY)
    def decode_decoy(self, obj, trans):
        for c in obj['content']:
            c['text'] = trans[str(c['id'])]
        return obj

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

    @decode_mapping(PATH_PROMPT, PATH_BUILD_PROMPT, PATH_PROMPT)
    def decode_prompt(self, obj, trans):
        for c in obj['content']:
            cid = str(c['id'])
            assert trans[cid].count('\n') <= 1, f"Incorrect cid: {cid}"
            c['category'] = trans[cid].split('\n')[0].strip()
        return obj

    def unpack_question(self):
        trans = read_json(PATH_BUILD_PROMPT)
        dirs = os.listdir(PATH_PROMPT_DIR)
        for cid in dirs:
            if not cid.isdigit():
                continue
            obj = read_from_folder(cid, PATH_PROMPT_DIR)
            assert trans[cid].strip().count('\n') <= 1
            text, *comment = trans[cid].strip().split('\n')
            text = text.strip().replace('??', "'")
            obj['QuestionText']['v'] = text
            if 'AlternateSpellings' in obj:
                obj['AlternateSpellings']['v'] = text
            if 'JokeAudio' in obj and comment and comment[0]:
                obj['JokeAudio']['s'] = comment[0].strip()
            write_to_folder(cid, PATH_PROMPT_DIR, obj)

    def decode_localization(self):
        self.update_localization(PATH_LOCALIZATION, PATH_BUILD_LOCALIZATION)

    @decode_mapping(PATH_BUILD_SUBTITLES, PATH_TRANSLATED_DICT, out_json=False)
    def decode_media_dict(self, audio):
        source = self._read(PATH_SOURCE_DICT)
        editable = self._read(PATH_EDITABLE_DICT)
        translations = {**audio}
        return self._update_media_dict(source, translations, editable)
