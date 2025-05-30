import os

from lib.game import Game, clean_text
from paths import JPP8_PATH


class JobJob(Game):
    name = 'ApplyYourself'
    international = True
    game = os.path.join(JPP8_PATH + r'\games\JobGame')
    folder = '../data/pp8/jobjob/'

    def encode_interview_questions(self):
        obj = self.read_jet('InterviewQuestion')
        res = {}
        for c in obj['content']:
            title = f"Round: {c['round']}" + ('' if not c['round3Header'] else f"\nHeader: {c['round3Header']}")
            res[c['id']] = {'text': c['question'], 'crowdinContext': self.get_context(c, title)}
        self.write_to_data('interview_questions.json', res)

    def encode_ice_breakers(self):
        obj = self.read_jet('Icebreaker')
        res = {c['id']: c['prompt'] for c in obj['content']}
        self.write_to_data('ice_breaker.json', res)

    def encode_poster_title(self):
        obj = self.read_jet('PosterTitle')
        res = {c['id']: c['title'] for c in obj['content']}
        self.write_to_data('poster_title.json', res)

    def encode_poster_prompt(self):
        obj = self.read_jet('PosterPrompt')
        res = {c['id']: c['prompt'] for c in obj['content']}
        self.write_to_data('poster_prompt.json', res)

    def encode_boner(self):
        obj = self.read_jet('Boner')
        res = {c['id']: c['phrase'] for c in obj['content']}
        self.write_to_data('boner.json', res)

    def encode_filler_phrase(self):
        obj = self.read_jet('FillerPhrase')
        res = {c['id']: c['phrase'] for c in obj['content']}
        self.write_to_data('filler_phrase.json', res)

    def encode_final_impression(self):
        obj = self.read_jet('FinalImpression')
        res = {c['id']: f"{c['firstPrompt']}\n{c['secondPrompt']}" for c in obj['content']}
        self.write_to_data('final_impression.json', res)

    # def encode_audio_subtitles(self):
    #     obj = self.read_from_data('media.json')
    #     audio = {
    #         v['id']: {'text': clean_text(v['text']), 'crowdinContext': c.get('crowdinContext', '')}
    #         for c in obj['media']
    #         for v in c['versions']
    #         if c['type'] == 'A' and 'SFX' not in v['text']
    #     }
    #     self.write_to_data('audio.json', audio)
