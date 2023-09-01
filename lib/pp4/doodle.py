import os

from lib.game import Game, decode_mapping, read_from_folder
from settings.doodle import *


class Doodle(Game):
    folder = '../data/pp4/doodle/encoded/'
    folder_swf = '../data/pp4/doodle/swf/'

    @decode_mapping(PATH_MAP, folder + 'map.json')
    def encode_map(self, obj):
        return {c['id']: {i: {'name': c[f'LocationName{i}'], 'crowdinContext': c[f'LocationType{i}']} for i in range(4)} for c in obj['content']}

    @decode_mapping(folder + 'final.json')
    def encode_final(self):
        ids = os.listdir(PATH_FINAL)
        res = {}
        for cid in ids:
            obj = read_from_folder(cid, PATH_FINAL)
            res[cid] = {'name': obj['DisplayText']['v'], 'crowdinContext': 'Category: ' + obj['Category']['v']}
        return res

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
