import os

import pandas as pd
import tqdm

from lib.drive import Drive
from lib.game import Game, decode_mapping, read_from_folder, write_to_folder, clean_text

PATH = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 4\games\Overdrawn'
PATH_MAP = PATH + r'\content\CivicDoodleMapJokes.jet'
PATH_FINAL = PATH + r'\content\CivicDoodleFinal'
PATH_MEDIA = PATH + r'\TalkshowExport\project\media'


class Doodle(Game):
    folder = '../data/pp4/doodle/encoded/'
    folder_swf = '../data/pp4/doodle/swf/'
    build = '../build/uk/JPP4/CD/'
    drive = '1pSF8GunDpRRW2DvyQLgv7GfIQezlOhAt'

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
                'name': clean_text(v['text']),
                'crowdinContext': c.get('crowdinContext'),
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

    @decode_mapping(folder + 'audio_subtitles.json', build + 'audio_subtitles.json', out=False)
    def upload_audio(self, original, obj):
        d = Drive(self.drive)
        data = []
        for cid in tqdm.tqdm(obj):
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg,
                         'context': obj[cid]['crowdinContext'],
                         'original': original[cid]['name'].strip().replace('\n', ' '),
                         'text': obj[cid]['name'].strip().replace('\n', ' ')})
            d.upload(PATH_MEDIA, ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio.tsv', sep='\t', encoding='utf8', index=False)
