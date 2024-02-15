import os

import pandas as pd
import tqdm

from lib.common import read_json, copy_file
from lib.drive import Drive
from lib.game import Game, encode_mapping, decode_mapping, write_to_folder, read_from_folder
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

    @decode_mapping(PATH_QUESTIONS_JSON, PATH_BUILD_QUESTIONS, PATH_QUESTIONS_JSON)
    def decode_quiplash_questions(self, obj: dict, trans: dict):
        for c in obj['content']:
            cid = str(c['id'])
            text = trans[cid].strip()
            if '\n' in text:
                text, response, *answers = text.split('\n')
            else:
                response, answers = None, []

            o = read_from_folder(cid, PATH_QUESTIONS)
            if o.get('KeywordResponseText', {}).get('v'):
                assert response is not None, f"Prompt {cid} should have a response: {o['KeywordResponseText']}"
                o['KeywordResponseText']['v'] = response.strip()
                o['Keywords']['v'] = '|'.join([x.strip() for x in answers])
                o['KeywordResponseAudio']['s'] = response.strip()
            else:
                assert response is None, f"Prompt {cid} shouldn't have a response: {response}"
            o['PromptText']['v'] = text
            o['PromptAudio']['s'] = text
            write_to_folder(cid, PATH_QUESTIONS, o)
            c['prompt'] = text
        return obj

    @decode_mapping(PATH_QUESTIONS_JSON, PATH_BUILD_QUESTIONS, PATH_QUESTIONS_JSON)
    def _decode_quiplash_questions_only_with_triggers(self, obj: dict, trans: dict):
        with_triggers = set()
        for c in obj['content']:
            cid = str(c['id'])
            text = trans[cid].strip()
            if '\n' in text:
                text, response, *answers = text.split('\n')
            else:
                response, answers = None, []

            o = read_from_folder(cid, PATH_QUESTIONS)
            if o.get('KeywordResponseText', {}).get('v'):
                assert response is not None, f"Prompt {cid} should have a response: {o['KeywordResponseText']}"
                o['KeywordResponseText']['v'] = response.strip()
                o['Keywords']['v'] = '|'.join([x.strip() for x in answers])
                o['KeywordResponseAudio']['s'] = response.strip()
            else:
                continue
            with_triggers.add(cid)
        obj['content'] = [c for c in obj['content'] if str(c['id']) in with_triggers]
        return obj

    @encode_mapping(PATH_AUDIENCE_JSON, folder + 'TranslatedAudienceQuestions.json')
    def encode_audience_questions(self, obj: dict) -> dict:
        return {c.pop('id'): c['prompt'] for c in obj['content']}

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

    def upload_audio_prompts(self):
        d = Drive()
        original = self._read_json(self.folder + 'EncodedOriginalQuiplashQuestions.json')
        dirs = os.listdir(PATH_QUESTIONS)
        exists = d.get_uploaded_files(PATH_DRIVE_PROMPTS)
        data = []
        for cid in tqdm.tqdm(dirs):
            if not cid.isdigit():
                continue
            obj = read_from_folder(cid, PATH_QUESTIONS)
            ogg = obj['PromptAudio']['v'] + '.ogg'
            data.append({
                'id': f'{cid}',
                'ogg': ogg.split('.')[0],
                'original': original[cid].strip().split('\n')[0],
                'translation': obj['PromptAudio']['s'],
            })
            if ogg not in exists:
                file = os.path.join(PATH_QUESTIONS, cid, ogg)
                d.copy_to_drive(PATH_DRIVE_PROMPTS, file, ogg)
        links = d.get_files_links(path_drive=PATH_DRIVE_PROMPTS)
        for i in data:
            i['link'] = links[i['ogg']]
        pd.DataFrame(data).to_csv(self.folder + 'audio_prompts.tsv', sep='\t', encoding='utf8', index=False)

    def upload_audio_triggers(self):
        d = Drive()
        original = self._read_json(self.folder + 'EncodedOriginalQuiplashQuestions.json')
        dirs = os.listdir(PATH_QUESTIONS)
        exists = d.get_uploaded_files(PATH_DRIVE_TRIGGERS)
        data = []
        for cid in tqdm.tqdm(dirs):
            if not cid.isdigit():
                continue
            obj = read_from_folder(cid, PATH_QUESTIONS)
            if obj['HasJokeAudio']['v'] == 'true':
                ogg = obj['KeywordResponseAudio']['v'] + '.ogg'
                if ogg not in exists:
                    file = os.path.join(PATH_QUESTIONS, cid, ogg)
                    d.copy_to_drive(PATH_DRIVE_TRIGGERS, file, ogg)
                data.append({
                    'id': f'{cid}',
                    'ogg': ogg.split('.')[0],
                    'original': original[cid].strip().split('\n')[1],
                    'translation': obj['KeywordResponseAudio']['s'],
                    'prompt': obj['PromptText']['v'],
                    'trigger': obj['Keywords']['v'].split('|')[0],
                })
        links = d.get_files_links(path_drive=PATH_DRIVE_TRIGGERS)
        for i in data:
            i['link'] = links[i['ogg']]
        pd.DataFrame(data).to_csv(self.folder + 'audio_triggers.tsv', sep='\t', encoding='utf8', index=False)

    @staticmethod
    def _decode_audio_tasks():
        dirs = os.listdir(PATH_QUESTIONS)
        for cid in tqdm.tqdm(dirs):
            if not cid.isdigit():
                continue
            obj = read_from_folder(cid, PATH_QUESTIONS)
            ogg = obj['PromptAudio']['v'] + '.ogg'
            copy_file(os.path.join(PATH_AUDIO_PROMPTS, ogg), os.path.join(PATH_QUESTIONS, cid, ogg))

    @staticmethod
    def _decode_audio_triggers():
        dirs = os.listdir(PATH_QUESTIONS)
        for cid in tqdm.tqdm(dirs):
            if not cid.isdigit():
                continue
            obj = read_from_folder(cid, PATH_QUESTIONS)
            if obj['HasJokeAudio']['v'] == 'true':
                ogg = obj['KeywordResponseAudio']['v'] + '.ogg'
                print('ogg', ogg)
                copy_file(os.path.join(PATH_AUDIO_TRIGGERS, ogg), os.path.join(PATH_QUESTIONS, cid, ogg))

    def release(self, start_time):
        self.update_localization(PATH_LOCALIZATION, PATH_BUILD_LOCALIZATION)
        self.decode_all()
        self.copy_to_release(PATH, PATH_RELEASE, start_time)
        self.make_archive(PATH_RELEASE, 'Quiplash2-UA.zip')
