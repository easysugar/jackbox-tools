from lib.game import Game, decode_mapping
from settings import teeko
from settings.old_teeko import *


class OldTeeKO(Game):
    folder = PATH_ENCODED

    @decode_mapping(PATH_MENU, folder + 'menu.json')
    def encode_menu(self, obj):
        return {i: {'title': x['title'], 'description': x['description']} for i, x in enumerate(obj)}

    @decode_mapping(PATH_LEADERBOARDS, folder + 'leaderboards.json')
    def encode_leaderboards(self, obj):
        return {
            'columns': {i['id']: i['name'] for i in obj['columns']},
            'views': {i['id']: {'name': i['name'], 'description': i['description']} for i in obj['views']},
        }

    @decode_mapping(PATH_SETTINGS, folder + 'settings.json')
    def encode_settings(self, obj):
        return {
            i['source']: {'title': i['title'], 'description': i['description']} for i in obj['items']
        }

    def decode_from_tjsp_teeko(self):
        self.copy_suggestions()
        self.copy_slogans()
        self.copy_slogan_suggestions()

    @staticmethod
    def _copy_template(old, new):
        mapp = {c['id']: c['suggestion'] for c in new['content']}
        for c in old['content']:
            c['suggestion'] = mapp[str(c['id'])]
        return old

    @decode_mapping(PATH_SUGGESTIONS, teeko.PATH_SUGGESTIONS, PATH_SUGGESTIONS)
    def copy_suggestions(self, old, new):
        return self._copy_template(old, new)

    @decode_mapping(PATH_SLOGANS, teeko.PATH_SLOGANS, PATH_SLOGANS)
    def copy_slogans(self, old, new):
        return self._copy_template(old, new)

    @decode_mapping(PATH_SLOGAN_SUGGESTIONS, teeko.PATH_SLOGAN_SUGGESTIONS, PATH_SLOGAN_SUGGESTIONS)
    def copy_slogan_suggestions(self, old, new):
        return self._copy_template(old, new)

    @decode_mapping(PATH_EXPANDED, folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T'}
