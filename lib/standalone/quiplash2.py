import os

from lib.common import read_json
from lib.game import Game, encode_mapping, decode_mapping
from settings.quiplash2 import *


class NotFoundPromptTextException(Exception):
    pass


class NotFoundPromptAudioException(Exception):
    pass


class Quiplash2(Game):
    folder = '../data/standalone/quiplash2/'

    @staticmethod
    def _update_question_obj(obj: dict, text: str):
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

    def _rewrite_question(self, oid: str, translation: str):
        path = os.path.join(PATH_QUESTIONS, oid, 'data.jet')
        obj = self._read_json(path)
        self._update_question_obj(obj, translation)
        self._write_json(path, obj)

    def unpack_questions(self):
        dirs = os.listdir(PATH_QUESTIONS)
        translations = self._read_json(PATH_BUILD_QUESTIONS)
        for oid in dirs:
            if oid.isdigit():
                self._rewrite_question(oid, translations[oid])

    @encode_mapping(PATH_QUESTIONS_JSON, folder + 'EncodedOriginalQuiplashQuestions.json')
    def encode_quiplash_questions(self, obj: dict) -> dict:
        result = {}
        for c in obj['content']:
            row = c['prompt']
            cid = str(c['id'])
            path = os.path.join(PATH_QUESTIONS, cid, 'data.jet')
            x = read_json(path)
            x = {_['n']: _ for _ in x['fields']}
            response = None if 'KeywordResponseText' not in x else x['KeywordResponseText']['v'].strip()
            answers = None if 'Keywords' not in x else list(map(str.strip, x['Keywords']['v'].split('|')))
            if response:
                row += '\n' + response + '\n' + '\n'.join(answers)
            result[c.pop('id')] = row
        return result

    @encode_mapping(PATH_AUDIENCE_JSON, folder + 'TranslatedAudienceQuestions.json')
    def encode_audience_questions(self, obj: dict) -> dict:
        return {c.pop('id'): c['prompt'] for c in obj['content']}

    @decode_mapping(PATH_QUESTIONS_JSON, PATH_BUILD_QUESTIONS, PATH_QUESTIONS_JSON)
    def decode_quiplash_questions(self, obj: dict, trans: dict):
        for c in obj['content']:
            c['prompt'] = trans[str(c['id'])]
        return obj

    @decode_mapping(PATH_AUDIENCE_JSON, PATH_BUILD_AUDIENCE, PATH_AUDIENCE_JSON)
    def decode_audience_questions(self, obj: dict, trans: dict):
        for c in obj['content']:
            c['prompt'] = trans[str(c['id'])]
        return obj

    @encode_mapping(folder + 'swf/Quiplash2_International_GameMain_Expanded.json', folder + 'encoded/audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return self._encode_subtitles(obj, 'A')

    @encode_mapping(folder + 'swf/Quiplash2_International_GameMain_Expanded.json', folder + 'encoded/text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return self._encode_subtitles(obj, 'T')

    def decode_media(self):
        self._decode_swf_media(
            path_media=self.folder + 'swf/dict.txt',
            path_expanded=self.folder + 'swf/Quiplash2_International_GameMain_Expanded.json',
            trans=self._read_json(PATH_BUILD_AUDIO_SUBTITLES) | self._read_json(PATH_BUILD_TEXT_SUBTITLES),
            path_save=self.folder + 'swf/translated_dict.txt',
        )

    def release(self, start_time):
        self.update_localization(PATH_LOCALIZATION, PATH_BUILD_LOCALIZATION)
        self.decode_all()
        self.copy_to_release(PATH, PATH_RELEASE, start_time)
        self.make_archive(PATH_RELEASE)
