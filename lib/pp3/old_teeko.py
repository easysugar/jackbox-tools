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

    @decode_mapping(PATH_MENU, PATH_BUILD + 'menu.json', PATH_MENU)
    def decode_menu(self, obj, trans):
        for i, c in enumerate(obj):
            c['title'] = trans[str(i)]['title']
            c['description'] = trans[str(i)]['description']
        return obj

    @decode_mapping(PATH_LEADERBOARDS, PATH_BUILD + 'leaderboards.json', PATH_LEADERBOARDS)
    def decode_leaderboards(self, obj, trans):
        for i in obj['columns']:
            i['name'] = trans['columns'][i['id']]
        for i in obj['views']:
            i['name'] = trans['views'][i['id']]['name']
            i['description'] = trans['views'][i['id']]['description']
        return obj

    @decode_mapping(PATH_SETTINGS, PATH_BUILD + 'settings.json', PATH_SETTINGS)
    def decode_settings(self, obj, trans):
        for i in obj['items']:
            i['title'] = trans[i['source']]['title']
            i['description'] = trans[i['source']]['description']
        return obj

    def decode_from_tjsp_teeko(self):
        self.copy_suggestions()
        self.copy_slogans()
        self.copy_slogan_suggestions()
        self.copy_text_subtitles()

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

    @decode_mapping(folder + 'text_subtitles.json', teeko.PATH_DATA + 'encoded/text_subtitles.json',
                    teeko.PATH_DATA + 'translated/text_subtitles.json', PATH_DATA + 'translated/text_subtitles.json')
    def copy_text_subtitles(self, obj, tjsp, trans):
        tjsp_r = {v: k for k, v in tjsp.items()}
        id_map = {_id: tjsp_r[text] for _id, text in obj.items()}
        for i in obj:
            obj[i] = trans[id_map[i]]
        assert set(obj) == set(id_map)
        return obj

    @decode_mapping(PATH_DATA + 'translated/text_subtitles.json', PATH_TRANSLATED_DICT, out_json=False)
    def decode_media_dict(self, translations):
        source = self._read(PATH_SOURCE_DICT)
        editable = self._read(PATH_EDITABLE_DICT)
        print(translations)
        return self._update_old_media_dict(source, translations, editable)
