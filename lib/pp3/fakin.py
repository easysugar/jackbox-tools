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

    # @encode_mapping(PATH_EXPANDED, 'data/pp3/pollposition/encoded/audio_subtitles.json')
    # def encode_audio_subtitles(self, obj: dict):
    #     sfx = re.compile(r'\[category=(sfx|music)]$|^\w+\d:\n|^PP_\w+|^Radio Play short |^Radio Play |Back button pressed')
    #     return {
    #         v['id']: {"text": v['text'].replace('[category=host]', '').replace('placeholder: ', '').strip(), "crowdinContext": c.get('context')}
    #         for c in obj
    #         for v in c['versions']
    #         if c['type'] == 'A' and not sfx.search(v['text'])
    #     }
