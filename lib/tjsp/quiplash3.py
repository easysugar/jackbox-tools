from collections import defaultdict

import pandas as pd
import tqdm

from lib.drive import Drive
from lib.game import Game, encode_mapping, decode_mapping, read_from_folder, write_to_folder, clean_text

PATH = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\games\Quiplash3'
PATH_QUESTIONS_ROUND1 = PATH + r'\content\en\Quiplash3Round1Question.jet'
PATH_QUESTIONS_ROUND1_DIR = PATH + r'\content\en\Quiplash3Round1Question'
PATH_QUESTIONS_ROUND2 = PATH + r'\content\en\Quiplash3Round2Question.jet'
PATH_QUESTIONS_ROUND2_DIR = PATH + r'\content\en\Quiplash3Round2Question'
PATH_QUESTIONS_FINAL_ROUND = PATH + r'\content\en\Quiplash3FinalQuestion.jet'
PATH_QUESTIONS_FINAL_ROUND_DIR = PATH + r'\content\en\Quiplash3FinalQuestion'
PATH_LOCALIZATION = PATH + r'\Localization.json'
PATH_MEDIA = PATH + r'\TalkshowExport\project\media'


class Quiplash3(Game):
    folder = '../data/tjsp/quiplash3/encoded/'
    build = '../build/uk/Quiplash3/'
    drive = '14zdrmnUShAr4EFHQw4oL3IIipAoiQ4y8'

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
                keywords = [t.strip() for t in triggers[c['id']]['keywords']['text'].split('\n') if t.strip()]
                keywords += [' ' + k for k in keywords] + [k + ' ' for k in keywords]
                keywords += ['<ARTICLE> ' + k for k in keywords]
                o['Keywords']['v'] = '|'.join(keywords)
                o['KeywordResponseAudio']['s'] = o['KeywordResponseText']['v'] = triggers[c['id']]['response']['text']
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
                keywords = [t.strip() for t in triggers[c['id']]['keywords']['text'].split('\n') if t.strip()]
                keywords += [' ' + k for k in keywords] + [k + ' ' for k in keywords]
                keywords += ['<ARTICLE> ' + k for k in keywords]
                o['Keywords']['v'] = '|'.join(keywords)
                o['KeywordResponseAudio']['s'] = o['KeywordResponseText']['v'] = triggers[c['id']]['response']['text']
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

    @decode_mapping(folder + 'audio_subtitles.json', build + 'audio_subtitles.json', out=False)
    def upload_audio(self, original, obj):
        d = Drive(self.drive)
        data = []
        original = {cid: t for k, v in original.items() for cid, t in v.items()}
        obj = {cid: t for k, v in obj.items() for cid, t in v.items()}
        for cid in tqdm.tqdm(obj):
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg, 'text': obj[cid].strip().replace('\n', ' '),
                         # 'context': obj[cid]['crowdinContext'],
                         'original': original[cid].strip().replace('\n', ' ')})
            d.upload(PATH_MEDIA, ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio.tsv', sep='\t', encoding='utf8', index=False)

    @decode_mapping(folder + 'expanded.json', build + 'text_subtitles.json', out=False)
    def upload_audio_awakening(self, expanded, text):
        original = {}
        obj = {}
        for c in expanded:
            if c['id'] == '150161':
                for v in c['versions']:
                    if v['locale'] == 'en':
                        original[v['id']] = clean_text(v['text'])
                        obj[v['id']] = text['Awakenings'][str(int(v['id'])-500875+500350)]
        data = []
        d = Drive(self.drive)
        for cid in tqdm.tqdm(obj):
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg, 'text': obj[cid].strip().replace('\n', ' '),
                         'original': original[cid].strip().replace('\n', ' ')})
            d.upload(PATH_MEDIA, ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio_awakening.tsv', sep='\t', encoding='utf8', index=False)

