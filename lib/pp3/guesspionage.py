import os
import re

import pandas as pd
from tqdm import tqdm

from lib.common import copy_file
from lib.drive import Drive
from lib.game import Game, decode_mapping, read_from_folder, write_to_folder
from settings.guesspionage import *


class Guesspionage(Game):
    folder = '../data/pp3/pollposition/encoded/'
    folder_swf = '../data/pp3/pollposition/swf/'
    build = '../build/uk/JPP3/Guesspionage/'

    @decode_mapping(PATH_EXPANDED, folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        sfx = re.compile(r'\[category=(sfx|music)]$|^\w+\d:\n|^PP_\w+|^Radio Play short |^Radio Play |Back button pressed')
        return {
            v['id']: {"text": v['text'].replace('[category=host]', '').replace('placeholder: ', '').strip(), "crowdinContext": c.get('context')}
            for c in obj
            for v in c['versions']
            if c['type'] == 'A' and not sfx.search(v['text'])
        }

    @decode_mapping(PATH_EXPANDED, folder + 'audio_lobby.json')
    def encode_audio_subtitles(self, obj: dict):
        return {
            v['id']: v['text']
            for c in obj
            for v in c['versions']
            if c['type'] == 'A' and 'Radio' in v['text']
        }

    @decode_mapping(PATH_EXPANDED, folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T'}

    def decode_media(self):
        audio = {}
        text = self._read_json(self.build + 'text_subtitles.json')
        self._decode_swf_media(
            path_media=self.folder_swf + 'dict.txt',
            path_expanded=PATH_EXPANDED,
            trans=audio | text,
            path_save=self.folder_swf + 'translated_dict.txt',
        )

    @decode_mapping(PATH_LEADERBOARDS, folder + 'leaderboards.json')
    def encode_leaderboards(self, obj):
        return {
            'columns': {i['id']: i['name'] for i in obj['columns']},
            'views': {i['id']: {'name': i['name'], 'description': i['description']} for i in obj['views']},
        }

    @decode_mapping(PATH_LEADERBOARDS, build + 'leaderboards.json', PATH_LEADERBOARDS)
    def decode_leaderboards(self, obj, trans):
        for i in obj['columns']:
            i['name'] = trans['columns'][i['id']]
        for i in obj['views']:
            i['name'] = trans['views'][i['id']]['name']
            i['description'] = trans['views'][i['id']]['description']
        return obj

    @decode_mapping(PATH_BONUS_QUESTIONS, folder + 'bonus_questions.json')
    def encode_bonus_questions(self, obj):
        result = {}
        for c in obj['content']:
            cid = str(c['id'])
            x = read_from_folder(cid, PATH_BONUS_QUESTIONS_DIR)
            body = {x['QText']['v']: {
                "question": x['PollQ']['v'],
                'text': x['QText']['v'],
                'choices': [x['Choice%d' % i]['v'] for i in range(9)],
                'answers': [x['Val%d' % i]['v'] for i in range(9)],
                'data_mode': x['DataMode']['v'],
                'exp_results': x['ExpResults']['v'],
                'category': c['category'],
            }}
            result[cid] = body
        return result

    @decode_mapping(PATH_BONUS_QUESTIONS, build + 'in-game/bonus_questions.json', PATH_BONUS_QUESTIONS)
    def decode_bonus_questions(self, obj, trans):
        for c in obj['content']:
            cid = str(c['id'])
            x = list(trans[cid].values())[0]
            c['category'] = x['category']
            o = read_from_folder(cid, PATH_BONUS_QUESTIONS_DIR)
            o['PollQ']['v'] = x['question']
            o['QText']['v'] = x['text']
            o['DataMode']['v'] = x['data_mode']
            o['ExpResults']['v'] = x['exp_results']

            for f in sorted(o):
                if f.startswith('Choice'):
                    o[f]['v'] = x['choices'][int(f.replace('Choice', ''))]
                if f.startswith('Val'):
                    o[f]['v'] = x['answers'][int(f.replace('Val', ''))]
                    assert 0 <= int(o[f]['v']) <= 100

            write_to_folder(cid, PATH_BONUS_QUESTIONS_DIR, o)
        return obj

    @decode_mapping(PATH_QUESTIONS, folder + 'questions.json')
    def encode_questions(self, obj):
        result = {}
        unique_fields = {}
        for c in obj['content']:
            cid = str(c['id'])
            x = read_from_folder(cid, PATH_QUESTIONS_DIR)
            body = {x['QText']['v']: {
                "question": x['PollQ']['v'],
                'text': x['QText']['v'],
                'data_mode': x['DataMode']['v'],
                'exp_results': x['ExpResults']['v'],
                'answer': x['A']['v'],
                'choices': [x[i]['v'] for i in sorted(x) if i.startswith('Choice')],
                'target': x['Target']['v'],
                'category': c['category'],
            }}
            assert 0 <= int(x['A']['v']) <= 100
            result[cid] = body
            unique_fields.update({k: x[k]['v'] for k in x if 'v' in x[k]})
        print('unique fields:', unique_fields)
        return result

    @decode_mapping(PATH_QUESTIONS, build + 'in-game/questions.json', PATH_QUESTIONS)
    def decode_questions(self, obj, trans):
        for c in obj['content']:
            cid = str(c['id'])
            x = list(trans[cid].values())[0]
            c['category'] = x['category']
            o = read_from_folder(cid, PATH_QUESTIONS_DIR)
            o['PollQ']['v'] = x['question']
            o['QText']['v'] = x['text']
            o['DataMode']['v'] = x['data_mode']
            o['ExpResults']['v'] = x['exp_results']
            o['A']['v'] = x['answer']
            o['Target']['v'] = x['target']

            for f in sorted(o):
                if f.startswith('Choice'):
                    o[f]['v'] = x['choices'][int(f.replace('Choice', ''))]

            write_to_folder(cid, PATH_QUESTIONS_DIR, o)
        return obj

    def upload_audio_questions(self):
        d = Drive()
        original = self._read_json(self.folder + 'questions.json')
        dirs = os.listdir(PATH_QUESTIONS_DIR)
        exists = d.get_uploaded_files(PATH_DRIVE_QUESTIONS)
        data = []
        for cid in tqdm(dirs):
            obj = read_from_folder(cid, PATH_QUESTIONS_DIR)
            ogg = obj['Q']['v'] + '.ogg'
            data.append({
                'id': cid,
                'ogg': ogg.split('.')[0],
                'original': list(original[cid].values())[0]['text'],
                'translation': obj['QText']['v'],
            })
            if ogg not in exists:
                file = os.path.join(PATH_QUESTIONS_DIR, cid, ogg)
                d.copy_to_drive(PATH_DRIVE_QUESTIONS, file, ogg)
        links = d.get_files_links(path_drive=PATH_DRIVE_QUESTIONS)
        for i in data:
            i['link'] = links[i.pop('ogg')]
        pd.DataFrame(data).to_csv(self.folder + 'audio_questions.tsv', sep='\t', encoding='utf8', index=False)

    def decode_localization(self):
        self.update_localization(PATH_LOCALIZATION, self.build + 'localization.json')

    @staticmethod
    def _decode_translated_audio():
        translated = set(os.listdir(PATH_TRANSLATED_AUDIO))
        original = set(os.listdir(PATH_AUDIO))
        for file in tqdm(translated):
            assert file in original, f'file {file} should be in original audio folder'
            copy_file(os.path.join(PATH_TRANSLATED_AUDIO, file), os.path.join(PATH_AUDIO, file))
