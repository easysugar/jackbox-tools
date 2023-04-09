import os
import re

from lib.common import read_json
from lib.game import Game, decode_mapping, read_from_folder, write_to_folder
from settings.fakin import *


class Fakin(Game):
    folder = '../data/pp3/fakin/encoded/'
    folder_swf = '../data/pp3/fakin/swf/'
    build = '../build/uk/JPP3/FakinIt/'

    @decode_mapping(PATH_EXPANDED, PATH_AUDIO_SUBTITLES)
    def encode_audio_subtitles(self, obj: dict):
        sfx = re.compile(
            r'\nThis\b|TIMER loop|SFX\b|\bThis sfx\b|\bMUSIC LOOP\b|\bmusic loop\b|\bThis music\b|Player Login|Lobby Loop|CATEGORY V|^Version')  # ^INSTRUCTIONS Loop|^CATEGORY|^(ICON|TIMER loop|LOBBY|FINAL ROUND|INSTRUCTIONS): |
        return {
            v['id']: {"text": v['text'].replace('[RECORD]', '').replace('[FACE]', '').replace('[NUMBER]', '').replace('[POINT]', '')
            .replace('[RECORD BELOW]', '').strip(), "crowdinContext": c.get('context')}
            for c in obj
            for v in c['versions']
            if c['type'] == 'A' and not sfx.search(v['text'])
        }

    @decode_mapping(folder_swf + 'FakinIt_Expanded.json', folder_swf + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return self._encode_subtitles(obj, 'T', tags='')

    @decode_mapping(PATH_MENU, folder + 'menu.json')
    def encode_menu(self, obj):
        return {i: {'title': x['title'], 'description': x['description']} for i, x in enumerate(obj)}

    @decode_mapping(PATH_MENU, build + 'menu.json', PATH_MENU)
    def decode_menu(self, obj, trans):
        for i, x in enumerate(obj):
            x['title'] = trans[str(i)]['title']
            x['description'] = trans[str(i)]['description']
        return obj

    @decode_mapping(PATH_TASKS, folder + 'tasks.json')
    def encode_tasks(self, obj: dict):
        return {i['id']: {i['type']: i['category']} for i in obj['content']}

    @decode_mapping(PATH_TASKS, build + 'in-game/tasks.json', PATH_TASKS)
    def decode_tasks(self, obj, trans):
        for i in obj['content']:
            i['category'] = trans[str(i['id'])][i['type']]
        return obj

    @decode_mapping(PATH_CATEGORIES, folder + 'categories.json')
    def encode_categories(self, obj: dict):
        return {i['id']: {i['type']: i['name']} for i in obj['content']}

    @decode_mapping(PATH_CATEGORIES, build + 'in-game/categories.json', PATH_CATEGORIES)
    def decode_categories(self, obj, trans):
        for i in obj['content']:
            i['name'] = trans[str(i['id'])][i['type']]
        return obj

    @decode_mapping(PATH_INPUT, folder + 'input.json')
    def encode_input(self, obj: dict):
        return {i['id']: '\n'.join([i['category'], *[j['v'] for j in i['tasks']]]) for i in obj['content']}

    @decode_mapping(PATH_INPUT, build + 'in-game/input.json', PATH_INPUT)
    def decode_input(self, obj, trans):
        for i in obj['content']:
            category, *tasks = trans[str(i['id'])].strip().split('\n')
            assert len(i['tasks']) == len(tasks)
            i['category'] = category
            for j, task in zip(i['tasks'], tasks):
                j['v'] = task
        return obj

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

    @decode_mapping(PATH_SETTINGS, folder + 'settings.json')
    def encode_settings(self, obj):
        return {
            i['source']: {'title': i['title'], 'description': i['description']} for i in obj['items']
        }

    @decode_mapping(PATH_SETTINGS, build + 'settings.json', PATH_SETTINGS)
    def decode_settings(self, obj, trans):
        for i in obj['items']:
            i['title'] = trans[i['source']]['title']
            i['description'] = trans[i['source']]['description']
        return obj

    @staticmethod
    def unpack_tasks():
        trans = read_json(PATH_TASKS)
        trans = {str(x['id']): x['category'] for x in trans['content']}
        dirs = os.listdir(PATH_TASKS_DIR)
        for cid in dirs:
            if not cid.isdigit():
                continue
            obj = read_from_folder(cid, PATH_TASKS_DIR)
            text = trans[cid].strip().replace('ʼ', "'")
            assert obj['TaskText']['v']
            obj['TaskText']['v'] = text
            write_to_folder(cid, PATH_TASKS_DIR, obj)

    @staticmethod
    def unpack_input():
        trans = read_json(PATH_INPUT)
        trans = {str(x['id']): x for x in trans['content']}
        dirs = os.listdir(PATH_INPUT_DIR)
        for cid in dirs:
            if not cid.isdigit():
                continue
            obj = read_from_folder(cid, PATH_INPUT_DIR)
            text = trans[cid]['category']
            assert obj['TaskText']['v']
            obj['TaskText']['v'] = text
            for task in trans[cid]['tasks']:
                assert obj['TextTaskText%d' % task['id']]['v']
                obj['TextTaskText%d' % task['id']]['v'] = task['v']
            write_to_folder(cid, PATH_INPUT_DIR, obj)

    def decode_media(self):
        audio = {k: v['text'] for k, v in self._read_json(self.build + 'audio_subtitles.json').items()}
        text = self._read_json(self.build + 'text_subtitles.json')
        self._decode_swf_media(
            path_media=self.folder_swf + 'dict.txt',
            path_expanded=self.folder_swf + 'FakinIt_Expanded.json',
            trans=audio | text,
            path_save=self.folder_swf + 'translated_dict.txt',
        )
