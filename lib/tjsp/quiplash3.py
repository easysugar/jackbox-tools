from collections import defaultdict

from lib.game import Game, encode_mapping, decode_mapping, read_from_folder, write_to_folder
from settings.quiplash3 import *


class Quiplash3(Game):
    folder = '../data/tjsp/quiplash3/encoded/'
    build = '../build/uk/Quiplash3/'

    @encode_mapping(PATH_QUESTIONS_ROUND1, PATH_QUESTIONS_ROUND2, folder + 'triggers.json')
    def encode_quiplash_questions_triggers(self, obj1: dict, obj2: dict) -> dict:
        res = {}
        for c in obj1['content'] + obj2['content']:
            cid = str(c['id'])
            try:
                o = read_from_folder(cid, PATH_QUESTIONS_ROUND1_DIR)
            except FileNotFoundError:
                o = read_from_folder(cid, PATH_QUESTIONS_ROUND2_DIR)
            if o['HasJokeAudio']['v'] == 'true':
                keywords = []
                for w in o['Keywords']['v'].split('|'):
                    w = w.replace('<ARTICLE>', '').replace('<PRONOUN>', '').replace('<VERB>', '').strip()
                    if w and w not in keywords:
                        keywords.append(w)
                res[cid] = {
                    'keywords': {'text': '\n'.join(keywords), 'crowdinContext': o['PromptText']['v']},
                    'response': {'text': o['KeywordResponseText']['v'], 'crowdinContext': o['PromptText']['v']},
                }
        return res

    @encode_mapping(PATH_QUESTIONS_ROUND1, folder + 'round1.json')
    def encode_quiplash_questions_round1(self, obj: dict) -> dict:
        return {c['id']: '\n'.join((c['prompt'], '\n'.join(c['safetyQuips']))) for c in obj['content']}

    @encode_mapping(PATH_QUESTIONS_ROUND1, build + 'round1.json', build + 'triggers.json', PATH_QUESTIONS_ROUND1)
    def decode_quiplash_questions_round1(self, obj: dict, trans: dict, triggers: dict) -> dict:
        for c in obj['content']:
            prompt, *quips = trans[c['id']].strip().split('\n')
            assert len(quips) > 0
            o = read_from_folder(c['id'], PATH_QUESTIONS_ROUND1_DIR)
            assert o['PromptAudio']['s'] and o['PromptText']['v'] and o['SafetyQuips']['v']
            c['prompt'] = o['PromptAudio']['s'] = o['PromptText']['v'] = prompt
            c['safetyQuips'] = quips
            o['SafetyQuips']['v'] = '|'.join(quips)
            if o['HasJokeAudio']['v'] == 'true':
                o['Keywords']['v'] = '|'.join([t.strip() for t in triggers[c['id']]['keywords']['text'].split('\n') if t.strip()])
                o['KeywordResponseText']['v'] = triggers[c['id']]['response']['text']
                o['KeywordResponseAudio']['v'] = o['KeywordResponseText']['v']
            write_to_folder(c['id'], PATH_QUESTIONS_ROUND1_DIR, o)
        return obj

    @encode_mapping(PATH_QUESTIONS_ROUND2, folder + 'round2.json')
    def encode_quiplash_questions_round2(self, obj: dict) -> dict:
        return {c['id']: '\n'.join((c['prompt'], '\n'.join(c['safetyQuips']))) for c in obj['content']}

    @encode_mapping(PATH_QUESTIONS_ROUND2, build + 'round2.json', build + 'triggers.json', PATH_QUESTIONS_ROUND2)
    def decode_quiplash_questions_round2(self, obj: dict, trans: dict, triggers: dict) -> dict:
        for c in obj['content']:
            prompt, *quips = trans[c['id']].strip().split('\n')
            assert len(quips) > 0
            o = read_from_folder(c['id'], PATH_QUESTIONS_ROUND2_DIR)
            assert o['PromptAudio']['s'] and o['PromptText']['v'] and o['SafetyQuips']['v']
            c['prompt'] = o['PromptAudio']['s'] = o['PromptText']['v'] = prompt
            c['safetyQuips'] = quips
            o['SafetyQuips']['v'] = '|'.join(quips)
            if o['HasJokeAudio']['v'] == 'true':
                o['Keywords']['v'] = '|'.join([t.strip() for t in triggers[c['id']]['keywords']['text'].split('\n') if t.strip()])
                o['KeywordResponseText']['v'] = triggers[c['id']]['response']['text']
                o['KeywordResponseAudio']['v'] = o['KeywordResponseText']['v']
            write_to_folder(c['id'], PATH_QUESTIONS_ROUND2_DIR, o)
        return obj

    def encode_localization(self):
        self._encode_localization(PATH_LOCALIZATION, self.folder + 'localization.json')

    def decode_localization(self):
        self.update_localization(PATH_LOCALIZATION, self.build + 'localization.json')

    @encode_mapping(folder + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        res = defaultdict(dict)
        for c in obj:
            for v in c['versions']:
                if c['type'] == 'A' and v['locale'] == 'en' and not v['text'].endswith('[Unsubtitled]'):
                    res[c['versions'][0]['text'].replace('[category=host]', '')][v['id']] = v['text'].replace('[category=host]', '')
        return res

    @encode_mapping(folder + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        res = defaultdict(dict)
        for c in obj:
            for v in c['versions']:
                if c['type'] == 'T' and v['locale'] == 'en' and not v['text'].startswith('SFX/'):
                    res[c['versions'][0]['text']][v['id']] = v['text']
        return res

    def decode_media(self):
        text = self._read_json(self.build + 'text_subtitles.json')
        text = {vid: text for _, vmap in text.items() for vid, text in vmap.items()}
        audio = self._read_json(self.build + 'audio_subtitles.json')
        audio = {vid: text for _, vmap in audio.items() for vid, text in vmap.items()}
        self._decode_swf_media(
            path_media=self.folder + '../swf/dict.txt',
            path_expanded=self.folder + '../expanded.json',
            trans=text | audio,
            path_save=self.folder + '../swf/translated_dict.txt',
        )

    @decode_mapping(PATH_QUESTIONS_FINAL_ROUND, folder + 'final_round.json')
    def encode_final_round(self, obj):
        res = {}
        for c in obj['content']:
            row = {}
            context = c['prompt']
            if c['us'] or c['x']:
                context += '\n-------------'
                if c['us']:
                    context += '\nUSA'
                if c['x']:
                    context += '\n18+'
            row['prompt'] = {'name': c['prompt'], 'crowdinContext': context}
            row['safetyQuips'] = [
                {'quip': sq.replace('|', '\n'), 'crowdinContext': context} for sq in c['safetyQuips']
            ]
            res[c['id']] = row
        return res

    @decode_mapping(PATH_QUESTIONS_FINAL_ROUND, build + 'final_round.json', PATH_QUESTIONS_FINAL_ROUND)
    def decode_final_round(self, obj, trans):
        for c in obj['content']:
            prompt = trans[c['id']]['prompt']['name']
            quips = [_['quip'].replace('\n', '|') for _ in trans[c['id']]['safetyQuips']]
            o = read_from_folder(c['id'], PATH_QUESTIONS_FINAL_ROUND_DIR)
            assert o['PromptAudio']['s'] and o['PromptText']['v'] and o['SafetyQuips']['v']
            c['prompt'] = o['PromptAudio']['s'] = o['PromptText']['v'] = prompt
            c['safetyQuips'] = quips
            o['SafetyQuips']['v'] = '|'.join(quips)
            write_to_folder(c['id'], PATH_QUESTIONS_FINAL_ROUND_DIR, o)
        return obj
