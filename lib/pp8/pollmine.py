import os
from collections import Counter

from lib.game import Game, update_localization, clean_text
from paths import JPP8_PATH


class PollMine(Game):
    name = 'SurveyBomb'
    pack = JPP8_PATH
    folder = '../data/pp8/pollmine/'
    build = '../build/uk/JPP8/PollMine/'

    def decode_localization(self):
        update_localization(os.path.join(self.game_path, 'Localization.json'), os.path.join(self.build, 'Localization.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationManager.json'), os.path.join('../build/uk/JPP8/', 'LocalizationManager.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationPause.json'), os.path.join('../build/uk/JPP8/', 'LocalizationPause.json'))

    def encode_team_names(self):
        obj = self.read_jet('TeamNames')
        res = {i: c['name'] for i, c in enumerate(obj['content'])}
        self.write_to_data('team_names.json', res)

    def decode_team_names(self):
        trans = self.read_from_build('team_names.json')
        obj = self.read_jet('TeamNames')
        for i, c in enumerate(obj['content']):
            c['name'] = trans[str(i)]
        self.write_jet('TeamNames', obj)

    def encode_questions(self):
        obj = self.read_jet('Questions')
        res = {}
        for c in obj['content']:
            cid = c['id']
            cxt = {'crowdinContext': self.get_context(c, c['question'])}
            item = {
                'question': {'text': c['question'], **cxt},
                'question_short': {'text': c['questionShort'], **cxt},
                'choices': [
                    {'text': i, **cxt}
                    for i in c['choices']
                ],
            }
            if c['intro']:
                item['intro'] = {'text': c['intro'], **cxt}
            if c['outro']:
                item['outro'] = {'text': c['outro'], **cxt}
            res[cid] = item
        self.write_to_data('questions.json', res)

    def decode_questions(self):
        trans = self.read_from_build('questions.json')
        obj = self.read_jet('Questions')
        for c in obj['content']:
            i = c['id']
            c['question'] = trans[i]['question']['text']
            c['questionShort'] = trans[i]['question_short']['text']
            c['choices'] = [ch['text'] for ch in trans[i]['choices']]
            assert len(c['choices']) == len(
                set(c['choices'])), f"Duplicates choices for {c['question']}: {Counter(c['choices']) - Counter(set(c['choices']))}"
            if c['intro']:
                c['intro'] = trans[i]['intro']['text']
            o = self.read_content(i, 'Questions')
            o['QuestionAudio']['s'] = trans[i]['question']['text']
            self.write_content(i, 'Questions', o)
        self.write_jet('Questions', obj)

    def encode_tutorial(self):
        obj = self.read_jet('TutorialChoices')
        res = {}
        for cid, c in enumerate(obj['content']):
            cxt = {'crowdinContext': self.get_context(c, c['prompt'])}
            item = {
                'prompt': {'text': c['prompt'], **cxt},
                'choices': [
                    {'text': i, **cxt}
                    for i in c['choices']
                ],
            }
            res[cid] = item
        self.write_to_data('tutorial.json', res)

    def decode_tutorial(self):
        trans = self.read_from_build('tutorial.json')
        obj = self.read_jet('TutorialChoices')
        for i, c in enumerate(obj['content']):
            t = trans[str(i)]
            c['prompt'] = t['prompt']['text']
            c['choices'] = [ch['text'] for ch in t['choices']]
        self.write_jet('TutorialChoices', obj)

    def encode_audio_subtitles(self):
        obj = self.read_from_data('SurveyBomb.json')
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
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'SurveyBomb.json',
                               trans=text, path_save=self.folder + 'translated_dict.txt')
