import os
import re
from collections import defaultdict

import tqdm

from lib.common import write_json, copy_file
from lib.game import Game, decode_mapping, read_from_folder, write_to_folder, normalize_text, remove_suffix

PATH = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 7\games\Quiplash3'
OLD_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\games\Quiplash3'


def transform_tags(s: str):
    return s.replace('[i]', '<i>').replace('[/i]', '</i>')


class OldQuiplash3(Game):
    folder = '../data/pp7/quiplash3/'
    tjsp_folder = '../data/tjsp/quiplash3/encoded/'
    build = '../build/uk/JPP7/Quiplash 3/'
    tjsp_build = '../build/uk/Quiplash3/'
    folder_audio_prompts = r'C:\Users\админ\Desktop\Jackbox\games\tjsp\quiplash3\audio\prompts'

    @decode_mapping(PATH + r'\Localization.json', OLD_PATH + r'\Localization.json', folder + 'localization.json')
    def encode_localization(self, obj, old_obj):
        return {k: v for k, v in obj['table']['en'].items() if k not in old_obj['table']['en']}

    def decode_localization(self):
        self.update_localization(PATH + r'\Localization.json', OLD_PATH + r'\Localization.json', self.build + 'localization.json')

    @decode_mapping(PATH + r'\content\Quiplash3Round1Question.jet', OLD_PATH + r'\content\en\Quiplash3Round1Question.jet',
                    PATH + r'\content\Quiplash3Round1Question.jet')
    def decode_quiplash_questions_round1(self, obj: dict, old_obj: dict) -> dict:
        old_obj = {c['id']: c for c in old_obj['content']}
        for c in obj['content']:
            old = old_obj[c['id']]
            o = read_from_folder(c['id'], PATH + r'\content\Quiplash3Round1Question')
            c['prompt'] = o['PromptText']['v'] = transform_tags(old['prompt'])
            c['safetyQuips'] = old['safetyQuips']
            o['SafetyQuips']['v'] = '|'.join(old['safetyQuips'])
            if o['HasJokeAudio']['v'] == 'true':
                old = read_from_folder(c['id'], OLD_PATH + r'\content\en\Quiplash3Round1Question')
                o['Keywords']['v'] = old['Keywords']['v']
                o['KeywordResponseText']['v'] = old['KeywordResponseText']['v']
            write_to_folder(c['id'], PATH + r'\content\Quiplash3Round1Question', o)
        return obj

    @decode_mapping(PATH + r'\content\Quiplash3Round2Question.jet', OLD_PATH + r'\content\en\Quiplash3Round2Question.jet',
                    PATH + r'\content\Quiplash3Round2Question.jet')
    def decode_quiplash_questions_round2(self, obj: dict, old_obj: dict) -> dict:
        old_obj = {c['id']: c for c in old_obj['content']}
        for c in obj['content']:
            old = old_obj[c['id']]
            o = read_from_folder(c['id'], PATH + r'\content\Quiplash3Round2Question')
            c['prompt'] = o['PromptText']['v'] = transform_tags(old['prompt'])
            c['safetyQuips'] = old['safetyQuips']
            o['SafetyQuips']['v'] = '|'.join(c['safetyQuips'])
            if o['HasJokeAudio']['v'] == 'true':
                old = read_from_folder(c['id'], OLD_PATH + r'\content\en\Quiplash3Round2Question')
                o['Keywords']['v'] = old['Keywords']['v']
                o['KeywordResponseText']['v'] = old['KeywordResponseText']['v']
            write_to_folder(c['id'], PATH + r'\content\Quiplash3Round2Question', o)
        return obj

    @decode_mapping(PATH + r'\content\Quiplash3FinalQuestion.jet', OLD_PATH + r'\content\en\Quiplash3FinalQuestion.jet',
                    PATH + r'\content\Quiplash3FinalQuestion.jet')
    def decode_quiplash_questions_final_round(self, obj: dict, old_obj: dict) -> dict:
        old_obj = {c['id']: c for c in old_obj['content']}
        for c in obj['content']:
            old = old_obj[c['id']]
            o = read_from_folder(c['id'], PATH + r'\content\Quiplash3FinalQuestion')
            c['prompt'] = o['PromptText']['v'] = transform_tags(old['prompt'])
            c['safetyQuips'] = old['safetyQuips']
            o['SafetyQuips']['v'] = '|'.join(c['safetyQuips'])
            write_to_folder(c['id'], PATH + r'\content\Quiplash3FinalQuestion', o)
        return obj

    @decode_mapping(folder + 'expanded.json', tjsp_folder + 'text_subtitles.json', tjsp_folder + 'audio_subtitles.json',
                    tjsp_folder + 'expanded.json', folder + 'media_mapping.json')
    def get_media_mappings(self, obj, old_text, old_audio, old_obj):
        maps = {}
        texts = defaultdict(list)
        for _ in old_text.values():
            for cid, t in _.items():
                texts[t].append(cid)
        audio = defaultdict(list)
        for _ in old_audio.values():
            for cid, a in _.items():
                audio[normalize_text(a)].append(cid)
        raw_map = {v['text']: v['id'] for c in old_obj for v in c['versions'] if v['locale'] == 'en'}
        missed_texts = {}
        missed_audio = {}
        for c in obj:
            for v in c['versions']:
                if v['tags'] != 'en' and v['tags'] != '':
                    continue
                if c['type'] == 'T':
                    if v['text'] not in texts:
                        if re.match(r'^(SFX/|MUSIC/|HOST/|quiplash3_)',
                                    v['text'].strip()):
                            continue
                        missed_texts[v['id']] = v['text']
                    else:
                        maps[v['id']] = texts[v['text']].pop(0)
                elif c['type'] == 'A':
                    t = normalize_text(v['text'])
                    if t not in audio:
                        if v['text'].endswith('[Unsubtitled]'):
                            maps[v['id']] = raw_map[v['text']]
                        else:
                            missed_audio[v['id']] = remove_suffix(v['text'])
                    else:
                        maps[v['id']] = audio[t].pop(0)
        if missed_texts:
            write_json(self.folder + 'additional_text.json', missed_texts)
        if missed_audio:
            write_json(self.folder + 'additional_audio.json', missed_audio)
        return maps

    @decode_mapping(tjsp_build + 'audio_subtitles.json', tjsp_build + 'text_subtitles.json', build + 'additional_text.json', folder + 'media_mapping.json',
                    out=False)
    def decode_media(self, tjsp_audio, tjsp_text, additional_text, maps):
        tjsp_text = {k: v for _ in tjsp_text.values() for k, v in _.items()}
        tjsp_audio = {k: v for _ in tjsp_audio.values() for k, v in _.items()}
        translations = {}  # version.id -> translated text
        for pp7_id, tjsp_id in maps.items():
            if tjsp_id in tjsp_audio:
                translations[pp7_id] = remove_suffix(tjsp_audio[tjsp_id])
            elif tjsp_id in tjsp_text:
                translations[pp7_id] = remove_suffix(tjsp_text[tjsp_id])
        for vid in additional_text:
            translations[vid] = remove_suffix(additional_text[vid])
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'expanded.json',
                               trans=translations, path_save=self.folder + 'translated_dict.txt')

    @decode_mapping(folder + 'media_mapping.json', out=False)
    def _copy_audio(self, obj):
        dst = PATH + r'\TalkshowExport\project\media'
        src = OLD_PATH + r'\TalkshowExport\project\media'
        tjsp_files = set(os.listdir(src))
        jpp7_files = set(os.listdir(dst))
        for jpp7, tjsp in obj.items():
            jpp7 = jpp7 + '.ogg'
            tjsp = tjsp + '.ogg'
            if tjsp in tjsp_files and jpp7 in jpp7_files:
                copy_file(os.path.join(src, tjsp), os.path.join(dst, jpp7))

    def _copy_audio_prompts(self):
        for folder in (PATH + r'\content\Quiplash3Round1Question',
                       PATH + r'\content\Quiplash3Round2Question',
                       PATH + r'\content\Quiplash3FinalQuestion'):
            dirs = os.listdir(folder)
            for cid in tqdm.tqdm(dirs):
                if not cid.isdigit():
                    continue
                ogg = 'prompt.ogg'
                copy_file(os.path.join(self.folder_audio_prompts, f'{cid}.ogg'), os.path.join(folder, cid, ogg))
