import os
import random

import pandas as pd

from lib.audio import gather_audio_files
from lib.game import Game, clean_text, update_localization
from paths import JPP8_PATH


class JobJob(Game):
    name = 'JobGame'
    name_short = 'ApplyYourself'
    pack = JPP8_PATH
    international = True
    folder = './data/pp8/jobjob/'
    build = './build/uk/JPP8/JobJob/'
    font = r'''!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿŒœŸˆ˜πЄІЇАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгдежзийклмнопрстуфхцчшщьюяєіїҐґ–—‘’‚“”„•…‹›⁄€™√∞∩≈'''
    N_WORDS_POSTER = 7

    def decode_localization(self):
        update_localization(os.path.join(self.game_path, 'Localization.json'), os.path.join(self.build, 'Localization.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationManager.json'), os.path.join('../build/uk/JPP8/', 'LocalizationManager.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationPause.json'), os.path.join('../build/uk/JPP8/', 'LocalizationPause.json'))

    def encode_interview_questions(self):
        obj = self.read_jet('InterviewQuestion')
        res = {}
        for c in obj['content']:
            title = f"Round: {c['round']}" + ('' if not c['round3Header'] else f"\nHeader: {c['round3Header']}")
            res[c['id']] = {'text': c['question'], 'crowdinContext': self.get_context(c, title)}
        self.write_to_data('interview_questions.json', res)

    def decode_interview_questions(self):
        trans = self.read_from_build('interview_questions.json')
        obj = self.read_jet('InterviewQuestion')
        for c in obj['content']:
            c['question'] = trans[c['id']]['text']
            o = self.read_content(c['id'], 'InterviewQuestion')
            o['QuestionAudio']['s'] = o['QuestionText']['v'] = c['question']
            self.write_content(c['id'], 'InterviewQuestion', o)
        self.write_jet('InterviewQuestion', obj)

    def encode_ice_breakers(self):
        obj = self.read_jet('Icebreaker')
        res = {c['id']: c['prompt'] for c in obj['content']}
        self.write_to_data('ice_breaker.json', res)

    def decode_ice_breakers(self):
        trans = self.read_from_build('ice_breaker.json')
        obj = self.read_jet('Icebreaker')
        for c in obj['content']:
            c['prompt'] = trans[c['id']]
        self.write_jet('Icebreaker', obj)

    def encode_poster_title(self):
        obj = self.read_jet('PosterTitle')
        res = {c['id']: c['title'] for c in obj['content']}
        self.write_to_data('poster_title.json', res)

    def decode_poster_title(self):
        trans = self.read_from_build('poster_title.json')
        obj = self.read_jet('PosterTitle')
        for c in obj['content']:
            c['title'] = trans[c['id']]
        self.write_jet('PosterTitle', obj)

    def encode_poster_prompt(self):
        obj = self.read_jet('PosterPrompt')
        res = {c['id']: c['prompt'] for c in obj['content']}
        self.write_to_data('poster_prompt.json', res)

    def decode_poster_prompt(self):
        trans = self.read_from_build('poster_prompt.json')
        obj = self.read_jet('PosterPrompt')
        for c in obj['content']:
            c['prompt'] = trans[c['id']]
        self.write_jet('PosterPrompt', obj)

    def encode_boner(self):
        obj = self.read_jet('Boner')
        res = {c['id']: c['phrase'] for c in obj['content']}
        self.write_to_data('boner.json', res)

    def decode_boner(self):
        trans = self.read_from_build('boner.json')
        obj = self.read_jet('Boner')
        for c in obj['content']:
            c['phrase'] = trans[c['id']]
        self.write_jet('Boner', obj)

    def encode_filler_phrase(self):
        obj = self.read_jet('FillerPhrase')
        res = {c['id']: c['phrase'] for c in obj['content']}
        self.write_to_data('filler_phrase.json', res)

    def decode_filler_phrase(self):
        trans = self.read_from_build('filler_phrase.json')
        obj = self.read_jet('FillerPhrase')
        words = list(set(self._read(os.path.join(self.folder, 'post_words.txt')).strip().splitlines()))
        left = words.copy()
        for c in obj['content']:
            c['phrase'] = trans[c['id']]
            poster_words = set()
            for _ in range(self.N_WORDS_POSTER):
                word = random.choice(left)
                poster_words.add(word)
                left.remove(word)
                if not left:
                    left = words.copy()
            c['poster'] = ' '.join(poster_words)
        self.write_jet('FillerPhrase', obj)

    def encode_final_impression(self):
        obj = self.read_jet('FinalImpression')
        res = {c['id']: f"{c['firstPrompt']}\n{c['secondPrompt']}" for c in obj['content']}
        self.write_to_data('final_impression.json', res)

    def decode_final_impression(self):
        trans = self.read_from_build('final_impression.json')
        obj = self.read_jet('FinalImpression')
        for c in obj['content']:
            assert len(trans[c['id']].split('\n')) == 2
            c['firstPrompt'], c['secondPrompt'] = tuple(trans[c['id']].split('\n'))
        self.write_jet('FinalImpression', obj)

    def encode_audio_subtitles(self):
        obj = self.read_from_data('JobGame.json')
        audio = {
            v['id']: {'text': clean_text(v['text']), 'crowdinContext': c.get('crowdinContext', '')}
            for c in obj['media']
            for v in c['versions']
            if c['type'] == 'A'
        }
        self.write_to_data('audio.json', audio)

    def decode_media(self):
        text = self.read_from_build('audio.json')
        text = {k: v['text'] for k, v in text.items()}
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'JobGame.json',
                               trans=text, path_save=self.folder + 'translated_dict.txt')

    def upload_audio(self):
        original = self.read_from_data('audio.json')
        obj = self.read_from_build('audio.json')
        data = []
        for cid in obj:
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg,
                         'context': obj[cid]['crowdinContext'],
                         'original': original[cid]['text'].strip().replace('\n', ' '),
                         'text': obj[cid]['text'].strip().replace('\n', ' ')})
        data.sort(key=lambda x: (x.get('context'), x['id']))
        fax = [_ for _ in data if '(говорить факс)' in _['context']]
        bubbles = [_ for _ in data if '(говорить факс)' not in _['context']]
        gather_audio_files(self.media_path, [_['ogg'] for _ in fax], os.path.join(self.folder, 'jobjob_main_fax_audio.wav'))
        pd.DataFrame(fax).to_csv(self.folder + 'audio_fax.tsv', sep='\t', encoding='utf8', index=False)
        gather_audio_files(self.media_path, [_['ogg'] for _ in bubbles], os.path.join(self.folder, 'jobjob_main_bubbles_audio.wav'))
        pd.DataFrame(bubbles).to_csv(self.folder + 'audio_bubbles.tsv', sep='\t', encoding='utf8', index=False)
