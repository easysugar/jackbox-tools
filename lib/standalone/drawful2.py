import os
from datetime import datetime

from lib.common import copy_file
from lib.game import Game, encode_mapping, read_json, decode_mapping, read_from_folder, write_to_folder
from paths import DRAWFUL2_PATH, DRAWFUL2_RELEASE_PATH

INSTALL_TIME = datetime(2024, 10, 28)
PATH = DRAWFUL2_PATH
PATH_LOCALIZATION = PATH + r'\Localization.json'
PATH_DECOY = PATH + r'\content\Drawful2Decoy.jet'
PATH_PROMPT = PATH + r'\content\en\Drawful2Prompt.jet'
PATH_PROMPT_DIR = PATH + r'\content\en\Drawful2Prompt'
PATH_AUDIO = PATH + r'\TalkshowExport\project\media'

# data
PATH_DATA = '../data/standalone/drawful2/'
PATH_SOURCE_DICT = PATH_DATA + 'swf/dict.txt'
PATH_TRANSLATED_DICT = PATH_DATA + 'swf/translated_dict.txt'
PATH_EDITABLE_DICT = PATH_DATA + 'swf/editable.txt'

# build
PATH_BUILD = '../build/uk/Drawful2/'
PATH_BUILD_GAME = PATH_BUILD + 'in-game/'
PATH_BUILD_LOCALIZATION = PATH_BUILD + 'localization.json'
PATH_BUILD_DECOY = PATH_BUILD_GAME + 'decoy.json'
PATH_BUILD_PROMPT = PATH_BUILD_GAME + 'prompt.json'
PATH_BUILD_SUBTITLES = PATH_BUILD + 'audio_subtitles.json'

PATH_TRANSLATED_AUDIO = r'X:\Jackbox\games\drawful2\translated-audio'
PATH_TRANSLATED_AUDIO_OTHER = r'C:\Jackbox\games\drawful2\translated-audio-other'
PATH_TRANSLATED_AUDIO_COMMENTS = r'X:\\Jackbox\games\drawful2\translated-audio-comments'


class Drawful2(Game):
    folder = '../data/standalone/drawful2/encoded/'
    folder_swf = '../data/standalone/drawful2/swf/'

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

    def decode_questions(self):
        trans = read_json(PATH_BUILD_PROMPT)
        dirs = os.listdir(PATH_PROMPT_DIR)
        for cid in dirs:
            if not cid.isdigit():
                continue
            obj = read_from_folder(cid, PATH_PROMPT_DIR)
            assert trans[cid].strip().count('\n') <= 1
            text, *comment = trans[cid].strip().split('\n')
            text = text.strip().replace('ʼ', "'")
            assert bool('JokeAudio' in obj) == bool(len(comment)), f'Mismatch joke: {cid} with comment: {comment} and joke: {obj.get("JokeAudio")}'
            obj['QuestionText']['v'] = text
            if 'AlternateSpellings' in obj:
                obj['AlternateSpellings']['v'] = text
            if 'JokeAudio' in obj and comment and comment[0]:
                obj['JokeAudio']['s'] = comment[0].strip()
            write_to_folder(cid, PATH_PROMPT_DIR, obj)

    def decode_localization(self):
        self.update_localization(PATH_LOCALIZATION, PATH_BUILD_LOCALIZATION)

    def decode_media(self):
        self._decode_swf_media(path_media=self.folder_swf + 'dict.txt', path_expanded=self.folder + 'expanded.json',
                               trans=self._read_json(PATH_BUILD_SUBTITLES),
                               path_save=self.folder_swf + 'translated_dict.txt')

    @staticmethod
    def copy_translated_audio():
        translated = set(os.listdir(PATH_TRANSLATED_AUDIO))
        original = set(os.listdir(PATH_AUDIO))
        for file in translated:
            if file in original:
                copy_file(os.path.join(PATH_TRANSLATED_AUDIO, file), os.path.join(PATH_AUDIO, file))

    @staticmethod
    def copy_translated_audio_other():
        translated = set(os.listdir(PATH_TRANSLATED_AUDIO_OTHER))
        original = set(os.listdir(PATH_AUDIO))
        for file in translated:
            assert file in original, f'File {file} should be in original'
            copy_file(os.path.join(PATH_TRANSLATED_AUDIO_OTHER, file), os.path.join(PATH_AUDIO, file))

    @staticmethod
    def copy_translated_audio_comments():
        dirs = os.listdir(PATH_PROMPT_DIR)
        for cid in dirs:
            if not cid.isdigit():
                continue
            obj = read_from_folder(cid, PATH_PROMPT_DIR)
            if obj['HasJokeAudio']['v'] == 'true':
                copy_file(os.path.join(PATH_TRANSLATED_AUDIO_COMMENTS, f'{cid}.ogg'),
                          os.path.join(PATH_PROMPT_DIR, cid, f"{obj['JokeAudio']['v']}.ogg"))

    def release(self):
        self.decode_all()
        self.copy_to_release(DRAWFUL2_PATH, DRAWFUL2_RELEASE_PATH, INSTALL_TIME)
        self.make_archive(DRAWFUL2_RELEASE_PATH, 'Drawful2-UA.zip')
