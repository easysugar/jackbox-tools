import os

from lib.game import Game, decode_mapping, read_from_folder, write_to_folder
from settings.doodle import *


class Doodle(Game):
    folder = '../data/pp4/doodle/encoded/'
    folder_swf = '../data/pp4/doodle/swf/'
    build = '../build/uk/JPP4/CD/'

    @decode_mapping(PATH_MAP, folder + 'map.json')
    def encode_map(self, obj):
        return {c['id']: {i: {'name': c[f'LocationName{i}'], 'crowdinContext': c[f'LocationType{i}']} for i in range(4)} for c in obj['content']}

    @decode_mapping(PATH_MAP, build + 'map.json', PATH_MAP)
    def decode_map(self, obj, trans):
        for c in obj['content']:
            t = trans[str(c['id'])]
            for i in range(4):
                c[f'LocationName{i}'] = t[str(i)]['name']
        return obj

    @decode_mapping(folder + 'final.json')
    def encode_final(self):
        ids = os.listdir(PATH_FINAL)
        res = {}
        for cid in ids:
            obj = read_from_folder(cid, PATH_FINAL)
            res[cid] = {'name': obj['DisplayText']['v'], 'crowdinContext': 'Category: ' + obj['Category']['v']}
        return res

    def decode_final(self):
        trans = self._read_json(self.build + 'final.json')
        ids = os.listdir(PATH_FINAL)
        for cid in ids:
            obj = read_from_folder(cid, PATH_FINAL)
            obj['DisplayText']['v'] = trans[f'{cid}']['name']
            write_to_folder(cid, PATH_FINAL, obj)

    @decode_mapping(folder_swf + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T' and v['tags'] != v['text']}

    @decode_mapping(folder_swf + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {
            v['id']: {
                'name': v['text'].replace('[category=host]', '').strip(),
                # 'crowdinContext': re.findall('\\[(.*?)]', v['text'].replace('[category=host]', '')),
            }
            for c in obj for v in c['versions'] if c['type'] == 'A' and '[category=host]' in v['text']
        }

    def decode_media(self):
        text = self._read_json(self.build + 'text_subtitles.json')
        self._decode_swf_media(
            path_media=self.folder_swf + 'dict.txt',
            path_expanded=self.folder_swf + 'expanded.json',
            trans=text,
            path_save=self.folder_swf + 'translated_dict.txt',
        )

    def decode_localization(self):
        self.update_localization(PATH + r'\Localization.json', self.build + 'localization.json')
