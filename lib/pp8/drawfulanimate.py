import logging
import os

import pandas as pd
import tqdm

from lib.drive import Drive
from lib.game import Game, clean_text, update_localization, decode_mapping
from paths import JPP8_PATH

personal_titles_map = {
    "{{PLAYER}}...": "{{PLAYER}}...",
    "{{PLAYER}}'s...": "У {{PLAYER}}...",
    "{{PLAYER}} when...": "{{PLAYER}}, коли...",
    "{{PLAYER}}'s idea of...": "Думки {{PLAYER}} про...",
    "{{PLAYER}} being...": "{{PLAYER}} виглядає як...",
    "{{PLAYER}} if...": "{{PLAYER}}, якби...",
    "{{PLAYER}} is...": "{{PLAYER}} зараз..."
}


class DrawfulAnimate(Game):
    name = 'DrawfulAnimate'
    pack = JPP8_PATH
    international = True
    folder = './data/pp8/drawful3/'
    build = './build/uk/JPP8/Drawful3/'
    drive = '1STC5GSRkckadmf3FDc-GTjkuLJUkN1ei'
    font = r'''!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ¡¢£¤¥§¨©ª«¬­®¯°±´µ¶·¸º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿĐđıŒœŠšŸŽžƒˆ˜πЄІЇАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгдежзийклмнопрстуфхцчшщьюяєіїҐґ–—‘’‚“”„†‡•…‰‹›€™Ω√≈'''
    audio_jokes_path = r'X:\Jackbox\games\jpp8\drawful3\audio\jokes'

    def encode_prompts(self):
        obj = self.read_jet('Prompt')
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['prompt'], 'crowdinContext': self.get_context(c, ','.join(c['tags']))}
            if c['joke']:
                res[c['id']]['joke'] = c['joke']
        self.write_to_data('prompts.json', res)

    def decode_prompts(self):
        trans = self.read_from_build('prompts.json')
        obj = self.read_jet('Prompt')
        for c in obj['content']:
            c['prompt'] = trans[c['id']]['prompt']
            if c['joke']:
                c['joke'] = trans[c['id']]['joke']
                o = self.read_content(c['id'], 'Prompt')
                o['JokeAudio']['s'] = c['joke']
                self.write_content(c['id'], 'Prompt', o)
                self.copy_audio_to_content(c['id'], 'Prompt', 'joke.ogg', self.audio_jokes_path, c['id'])
        self.write_jet('Prompt', obj)

    def encode_decoy(self):
        obj = self.read_jet('Decoy')
        res = {}
        for c in obj['content']:
            res[c['id']] = c['text']
        self.write_to_data('decoy.json', res)

    def decode_decoy(self):
        trans = self.read_from_build('decoy.json')
        obj = self.read_jet('Decoy')
        for c in obj['content']:
            c['text'] = trans[str(c['id'])]
        self.write_jet('Decoy', obj)

    def encode_personal_prompts(self):
        obj = self.read_jet('PersonalPrompt')
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['prompt'],
                            'crowdinContext': self.get_context(c, ','.join(c['tags']) + '\n' + personal_titles_map[c['title']])}
            if c['joke']:
                res[c['id']]['joke'] = c['joke']
        self.write_to_data('personal_prompts.json', res)

    def decode_personal_prompts(self):
        trans = self.read_from_build('personal_prompts.json')
        obj = self.read_jet('PersonalPrompt')
        for c in obj['content']:
            c['prompt'] = trans[c['id']]['prompt']
            c['title'] = personal_titles_map.get(c['title'], c['title'])
            if not c['prompt'].startswith(c['title'].removesuffix('...')):
                logging.debug('Prompt %s mismatches title: %s', c["prompt"], c["title"])
            assert c['title'].endswith('...')
            if c['joke']:
                c['joke'] = trans[c['id']]['joke']
                o = self.read_content(c['id'], 'PersonalPrompt')
                o['JokeAudio']['s'] = c['joke']
                self.write_content(c['id'], 'PersonalPrompt', o)
                self.copy_audio_to_content(c['id'], 'PersonalPrompt', 'joke.ogg', self.audio_jokes_path, c['id'])
        self.write_jet('PersonalPrompt', obj)

    def encode_personal_decoy(self):
        obj = self.read_jet('PersonalDecoy')
        res = {}
        for c in obj['content']:
            res[c['id']] = {'prompt': c['text'], 'crowdinContext': self.get_context(c, personal_titles_map[c['title']])}
        self.write_to_data('personal_decoy.json', res)

    def decode_personal_decoy(self):
        trans = self.read_from_build('personal_decoy.json')
        obj = self.read_jet('PersonalDecoy')
        for c in obj['content']:
            c['text'] = trans[str(c['id'])]['prompt']
            c['title'] = personal_titles_map.get(c['title'], c['title'])
        self.write_jet('PersonalDecoy', obj)

    def encode_audio_subtitles(self):
        obj = self.read_from_data('media.json')
        audio = {
            v['id']: {'text': clean_text(v['text']), 'crowdinContext': c.get('crowdinContext', '')}
            for c in obj['media']
            for v in c['versions']
            if c['type'] == 'A' and 'SFX' not in v['text']
        }
        self.write_to_data('audio.json', audio)

    def decode_media(self):
        text = self.read_from_build('audio.json')
        text = {k: v['text'] for k, v in text.items()}
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'media.json',
                               trans=text, path_save=self.folder + 'translated_dict.txt')

    def decode_localization(self):
        update_localization(os.path.join(self.game_path, 'Localization.json'), os.path.join(self.build, 'Localization.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationManager.json'), os.path.join(self.build, 'LocalizationManager.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationPause.json'), os.path.join(self.build, 'LocalizationPause.json'))

        update_localization(os.path.join(JPP8_PATH, 'Localization.json'), os.path.join('./build/uk/JPP8/', 'Localization.json'))
        update_localization(os.path.join(JPP8_PATH, 'LocalizationManager.json'), os.path.join('./build/uk/JPP8/', 'LocalizationManager.json'))
        update_localization(os.path.join(JPP8_PATH, 'LocalizationPause.json'), os.path.join('./build/uk/JPP8/', 'LocalizationPause.json'))
        update_localization(os.path.join(JPP8_PATH, 'games', 'Picker', 'Localization.json'),
                            os.path.join('./build/uk/JPP8/', 'LocalizationPicker.json'))
        update_localization(os.path.join(JPP8_PATH, 'games', 'Picker', 'LocalizationManager.json'),
                            os.path.join('./build/uk/JPP8/', 'LocalizationManager.json'))
        update_localization(os.path.join(JPP8_PATH, 'games', 'Picker', 'LocalizationPause.json'),
                            os.path.join('./build/uk/JPP8/', 'LocalizationPause.json'))

    @decode_mapping(folder + 'audio.json', build + 'audio.json', out=False)
    def upload_audio(self, original, obj):
        d = Drive(self.drive)
        data = []
        for cid in tqdm.tqdm(obj):
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg,
                         'context': obj[cid]['crowdinContext'],
                         'original': original[cid]['text'].strip().replace('\n', ' '),
                         'text': obj[cid]['text'].strip().replace('\n', ' ')})
            d.upload(self.game_path + r'\TalkshowExport\project\media', ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio.tsv', sep='\t', encoding='utf8', index=False)

    @decode_mapping(build + 'prompts.json', build + 'personal_prompts.json', out=False)
    def upload_audio_jokes(self, p1: dict, p2: dict):
        d = Drive(self.drive)
        data = []
        for cid, c in tqdm.tqdm(p1.items()):
            if 'joke' not in c:
                continue
            ogg = f'joke-{cid}.ogg'
            try:
                d.upload(self.game_path + r'\content\en\DrawfulAnimatePrompt', cid, 'joke.ogg', name=ogg)
            except FileNotFoundError:
                continue
            data.append({'id': cid, 'ogg': ogg,
                         'context': c['prompt'],
                         'text': c['joke'].strip().replace('\n', ' ')})
        for cid, c in tqdm.tqdm(p2.items()):
            if 'joke' not in c:
                continue
            ogg = f'joke-{cid}.ogg'
            try:
                d.upload(self.game_path + r'\content\en\DrawfulAnimatePersonalPrompt', cid, 'joke.ogg', name=ogg)
            except FileNotFoundError:
                continue
            data.append({'id': cid, 'ogg': ogg,
                         'context': c['prompt'],
                         'text': c['joke'].strip().replace('\n', ' ')})
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio-jokes.tsv', sep='\t', encoding='utf8', index=False)
