from lib.game import Game
from lib.utils import count_strings_and_words
from paths import JPP11_PATH


class HearSay(Game):
    name = 'MicGame'
    pack = JPP11_PATH
    international = True
    folder = './data/pp11/hearsay/'
    build = './build/uk/JPP11/HearSay/'

    def count_words_to_translate(self):
        strings, words = count_strings_and_words([
            self.read_localization(),
            [[p['prompt'] for p in c['soundsToRecord']] for c in self.read_jet('MicGamePrompt')['content']]
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')

    def encode_prompt(self):
        obj = self.read_jet('Prompt')
        directions = set()
        res = {}
        for c in obj['content']:
            directions |= {s['direction'] for s in c['soundsToRecord'] if s.get('direction')}
            res[c['id']] = [
                {
                    'text': s['prompt'],
                    **self.get_crowdin_context(c, c['videoTitle'], c['appearance'], s.get('direction')),
                }
                for s in c['soundsToRecord']
            ]
        assert len(directions) == 1
        res['direction'] = list(directions)[0]
        self.write_to_data('prompt.json', res)

    def decode_prompt(self):
        trans = self.read_from_build('prompt.json')
        obj = self.read_jet('Prompt')
        for c in obj['content']:
            for i, s in enumerate(c['soundsToRecord']):
                s['prompt'] = trans[c['id']][i]['text']
                if s.get('direction'):
                    s['direction'] = trans['direction']
        self.write_jet('Prompt', obj)

    def decode_localization(self):
        self.write_localization(self.read_from_build('Localization.json')['table']['en'])
