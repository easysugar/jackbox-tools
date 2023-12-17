import os

import Levenshtein

from lib.common import copy_file
from lib.game import Game, decode_mapping, read_from_folder, write_to_folder
from settings import quiplash2
from settings.old_quiplash2 import *


class OldQuiplash2(Game):
    folder = PATH_ENCODED
    folder_swf = PATH_DATA + 'swf/'

    @decode_mapping(PATH_MENU, folder + 'menu.json')
    def encode_menu(self, obj):
        return {i: {'title': x['title'], 'description': x['description']} for i, x in enumerate(obj)}

    @decode_mapping(PATH_MENU, PATH_BUILD + 'menu.json', PATH_MENU)
    def decode_menu(self, obj, trans):
        for i, c in enumerate(obj):
            c['title'] = trans[str(i)]['title']
            c['description'] = trans[str(i)]['description']
        return obj

    @decode_mapping(PATH_LEADERBOARDS, folder + 'leaderboards.json')
    def encode_leaderboards(self, obj):
        return {
            'columns': {i['id']: i['name'] for i in obj['columns']},
            'views': {i['id']: {'name': i['name'], 'description': i['description']} for i in obj['views']},
        }

    @decode_mapping(PATH_LEADERBOARDS, PATH_BUILD + 'leaderboards.json', PATH_LEADERBOARDS)
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

    @decode_mapping(PATH_SETTINGS, PATH_BUILD + 'settings.json', PATH_SETTINGS)
    def decode_settings(self, obj, trans):
        for i in obj['items']:
            i['title'] = trans[i['source']]['title']
            i['description'] = trans[i['source']]['description']
        return obj

    @decode_mapping(PATH_QUESTIONS_JSON, quiplash2.PATH_QUESTIONS_JSON, folder + 'extra_questions.json')
    def encode_extra_questions(self, old, new):
        new = {c['id'] for c in new['content']}
        res = {}
        for c in old['content']:
            if c['id'] not in new:
                res[c['id']] = c['prompt']
        return res

    def decode_from_standalone_quiplash2(self):
        self.copy_questions()
        self.copy_audience()
        self.copy_safety_quips()
        self.copy_word_lash()
        self.copy_word_lash_word()
        self.copy_acro_lash()
        self.copy_comic_lash()
        # media
        self.copy_text_subtitles()
        self.decode_media()
        self.copy_translated_audio()

    @staticmethod
    def _copy_template(old, new):
        mapp = {str(c['id']): c['prompt'] for c in new['content']}
        for c in old['content']:
            if str(c['id']) not in mapp:
                print(c['id'], c['prompt'])
                # continue
            c['prompt'] = mapp[str(c['id'])]
        return old

    @decode_mapping(PATH_AUDIENCE_JSON, quiplash2.PATH_AUDIENCE_JSON, PATH_AUDIENCE_JSON)
    def copy_audience(self, old, new):
        return self._copy_template(old, new)

    @decode_mapping(PATH_SAFETY_QUIPS, quiplash2.PATH_LOCALIZATION, PATH_SAFETY_QUIPS)
    def copy_safety_quips(self, old, localization):
        mapp = {int(k.replace('SAFETY_QUIP_', '')): v for k, v in localization['table']['en'].items() if k.startswith('SAFETY_QUIP_')}
        for c in old['content']:
            assert c['id'] in mapp
            c['value'] = mapp[c['id']]
        return old

    @decode_mapping(PATH_WORD_LASH, quiplash2.PATH_LOCALIZATION, PATH_WORD_LASH)
    def copy_word_lash(self, old, localization):
        mapp = {int(k.replace('WORDLASH_', '')): v for k, v in localization['table']['en'].items() if k.startswith('WORDLASH_')}
        for c in old['content']:
            assert c['id'] in mapp
            c['quip'] = mapp[c['id']]
        return old

    @decode_mapping(PATH_WORD_LASH_WORD, quiplash2.PATH_LOCALIZATION, PATH_WORD_LASH_WORD)
    def copy_word_lash_word(self, old, localization):
        mapp = {int(k.replace('WORDLASHWORD_', '')): v for k, v in localization['table']['en'].items() if k.startswith('WORDLASHWORD_')}
        for c in old['content']:
            assert c['id'] in mapp
            c['prompt'] = mapp[c['id']]
        return old

    @decode_mapping(PATH_ACRO_LASH, quiplash2.PATH_LOCALIZATION, PATH_ACRO_LASH)
    def copy_acro_lash(self, old, localization):
        mapp = {int(k.replace('ACROLASH_', '')): v for k, v in localization['table']['en'].items() if k.startswith('ACROLASH_')}
        for c in old['content']:
            assert c['id'] in mapp
            c['prompt'] = mapp[c['id']]
        return old

    @decode_mapping(PATH_COMIC_LASH, quiplash2.PATH_LOCALIZATION, PATH_COMIC_LASH)
    def copy_comic_lash(self, old, localization):
        value = localization['table']['en']['COMPLETE_COMIC']
        for c in old['content']:
            c['prompt'] = value
        return old

    @staticmethod
    def _update_question_obj(obj: dict, text: str):
        text = text.replace('ʼ', "'")
        fields = obj['fields']
        for f in fields:
            if f['n'] == 'PromptText':
                f['v'] = text
            if f['n'] == 'PromptAudio':
                f['s'] = text
        assert 'PromptText' in {f['n'] for f in fields}
        assert 'PromptAudio' in {f['n'] for f in fields}

    @decode_mapping(PATH_QUESTIONS_JSON, PATH_BUILD_EXTRA_QUESTIONS, quiplash2.PATH_QUESTIONS_JSON, PATH_QUESTIONS_JSON)
    def copy_questions(self, dst, extra, src):
        prompts = {str(c['id']): c['prompt'] for c in src['content']}
        prompts.update({str(cid): prompt for cid, prompt in extra.items()})
        for c in dst['content']:
            cid = str(c['id'])
            text = prompts[cid].strip()
            o = read_from_folder(cid, PATH_QUESTIONS_JSON)
            o2 = read_from_folder(cid, quiplash2.PATH_QUESTIONS_JSON) if cid not in extra else None
            if o.get('KeywordResponseText', {}).get('v') and cid not in extra:
                o['KeywordResponseText']['v'] = o2['KeywordResponseText']['v']
                o['Keywords']['v'] = o2['Keywords']['v']
                o['KeywordResponseAudio']['s'] = o2['KeywordResponseAudio']['s']
                copy_file(
                    os.path.join(quiplash2.PATH_QUESTIONS_JSON.removesuffix('.jet'), cid, o2['KeywordResponseAudio']['v'] + '.ogg'),
                    os.path.join(PATH_QUESTIONS_JSON.removesuffix('.jet'), cid, o['KeywordResponseAudio']['v'] + '.ogg'),
                )
            o['PromptText']['v'] = text
            o['PromptAudio']['s'] = text
            if cid in extra:
                copy_file(
                    os.path.join(quiplash2.PATH_AUDIO_PROMPTS, o['PromptAudio']['v'] + '.ogg'),
                    os.path.join(PATH_QUESTIONS_JSON.removesuffix('.jet'), cid, o['PromptAudio']['v'] + '.ogg'),
                )
            else:
                copy_file(
                    os.path.join(quiplash2.PATH_QUESTIONS_JSON.removesuffix('.jet'), cid, o2['PromptAudio']['v'] + '.ogg'),
                    os.path.join(PATH_QUESTIONS_JSON.removesuffix('.jet'), cid, o['PromptAudio']['v'] + '.ogg'),
                )
            write_to_folder(cid, PATH_QUESTIONS_JSON, o)
            c['prompt'] = text
        return dst

    @decode_mapping(folder_swf + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return self._encode_subtitles(obj, 'T', tags='')

    @decode_mapping(folder + 'text_subtitles.json', '../data/standalone/quiplash2/encoded/text_subtitles.json',
                    quiplash2.PATH_BUILD_TEXT_SUBTITLES, PATH_DATA + 'translated/text_subtitles.json')
    def copy_text_subtitles(self, obj, ext_orig, ext_trans):
        ext_map = {v: k for k, v in ext_orig.items()}
        id_map = {_id: ext_map[text] for _id, text in obj.items()}
        for i in obj:
            obj[i] = ext_trans[id_map[i]]
        assert set(obj) == set(id_map)
        return obj

    def decode_media(self):
        self._decode_swf_media(
            path_media=self.folder_swf + 'dict.txt',
            path_expanded=self.folder_swf + 'expanded.json',
            trans=self._read_json(PATH_DATA + 'translated/text_subtitles.json'),
            path_save=self.folder_swf + 'translated_dict.txt',
        )

    @decode_mapping(folder_swf + 'expanded.json', '../data/standalone/quiplash2/encoded/audio_subtitles.json', folder + 'audio_mapping.json')
    def get_games_audio_mapping(self, obj, ext):
        audio = {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'A' and 'sfx' not in v['text'].lower()}
        assert None not in audio
        res = {i: None for i in ext}
        maps = {" is": "'s", '.': '', ' ': '', ',': '', ':': '', '?': '', '!': '', '-': '', "’": '', "'": '',
                '1': 'one', '2': 'two', '3': 'three', '\n': '', 'okay': 'ok'}

        def use_maps(string):
            for m in maps:
                string = string.replace(m, maps[m])
            return string

        for i, t1 in ext.items():
            for j, t2 in audio.items():
                norm1 = use_maps(t1.lower())
                norm2 = use_maps(t2.lower())
                if norm1 == norm2 and j not in res.values():
                    res[i] = j
                    break

        for min_ratio in [.9, .8, .7]:
            for i in res:
                if res[i] is not None:
                    continue
                t1 = ext[i]
                for j, t2 in audio.items():
                    if j in res.values():
                        continue
                    if (ratio := Levenshtein.ratio(t1.lower(), t2.lower())) >= min_ratio:
                        res[i] = j
        del res["341812"]
        res["342067"] = "113594"
        return res

    def copy_translated_audio(self):
        obj = self._read_json(self.folder + 'audio_mapping.json')
        standalone_files = set(os.listdir(quiplash2.PATH_AUDIO))
        jpp3_files = set(os.listdir(PATH_AUDIO))
        for stnd, jpp3 in obj.items():
            stnd = stnd + '.ogg'
            jpp3 = jpp3 + '.ogg'
            if stnd in standalone_files and jpp3 in jpp3_files:
                copy_file(os.path.join(quiplash2.PATH_AUDIO, stnd), os.path.join(PATH_AUDIO, jpp3))
