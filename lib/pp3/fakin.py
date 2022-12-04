import re

from lib.game import Game, decode_mapping
from settings.fakin import *


class Fakin(Game):
    @decode_mapping(PATH_MENU, 'data/pp3/fakin/encoded/menu.json')
    def encode_menu(self, obj):
        return {i: {'title': x['title'], 'description': x['description']} for i, x in enumerate(obj)}

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

    @decode_mapping(PATH_TASKS, PATH_TASKS_ENCODED)
    def encode_tasks(self, obj: dict):
        return {i['id']: {i['type']: i['category']} for i in obj['content']}

    @decode_mapping(PATH_CATEGORIES, PATH_CATEGORIES_ENCODED)
    def encode_categories(self, obj: dict):
        return {i['id']: {i['type']: i['name']} for i in obj['content']}

    @decode_mapping(PATH_INPUT, PATH_INPUT_ENCODED)
    def encode_input(self, obj: dict):
        return {i['id']: '\n'.join([i['category'], *[j['v'] for j in i['tasks']]]) for i in obj['content']}

    @decode_mapping(PATH_LEADERBOARDS, PATH_LEADERBOARDS_ENCODED)
    def encode_leaderboards(self, obj):
        return {
            'columns': {i['id']: i['name'] for i in obj['columns']},
            'views': {i['id']: {'name': i['name'], 'description': i['description']} for i in obj['views']},
        }

    @decode_mapping(PATH_SETTINGS, PATH_SETTINGS_ENCODED)
    def encode_settings(self, obj):
        return {
            i['source']: {'title': i['title'], 'description': i['description']} for i in obj['items']
        }
