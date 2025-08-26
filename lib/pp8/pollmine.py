import os

from lib.game import Game
from paths import JPP8_PATH


class PollMine(Game):
    name = 'SurveyBomb'
    game = os.path.join(JPP8_PATH + r'\games\SurveyBomb')
    folder = '../data/pp8/pollmine/'

    def encode_team_names(self):
        obj = self.read_jet('TeamNames')
        res = {i: c['name'] for i, c in enumerate(obj['content'])}
        self.write_to_data('team_names.json', res)

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
                res['intro'] = {'text': c['intro'], **cxt}
            if c['outro']:
                res['outro'] = {'text': c['outro'], **cxt}
            res[cid] = item
        self.write_to_data('questions.json', res)

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
