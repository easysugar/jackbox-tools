import os

from lib.game import Game, clean_text, update_localization
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


class Drawful3(Game):
    name = 'DrawfulAnimate'
    international = True
    game = os.path.join(JPP8_PATH + r'\games\DrawfulAnimate')
    folder = '../data/pp8/drawful3/'
    build = '../build/uk/JPP8/Drawful3/'

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
            res[c['id']] = {'prompt': c['prompt'], 'crowdinContext': self.get_context(c, ','.join(c['tags']) + '\n' + personal_titles_map[c['title']])}
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
                print(f'Prompt {c["prompt"]} mismatches title: {c["title"]}')
            assert c['title'].endswith('...')
            if c['joke']:
                c['joke'] = trans[c['id']]['joke']
                o = self.read_content(c['id'], 'PersonalPrompt')
                o['JokeAudio']['s'] = c['joke']
                self.write_content(c['id'], 'PersonalPrompt', o)
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
        update_localization(os.path.join(self.game, 'Localization.json'), os.path.join(self.build, 'Localization.json'))
        update_localization(os.path.join(self.game, 'LocalizationManager.json'), os.path.join(self.build, 'LocalizationManager.json'))
        update_localization(os.path.join(self.game, 'LocalizationPause.json'), os.path.join(self.build, 'LocalizationPause.json'))
