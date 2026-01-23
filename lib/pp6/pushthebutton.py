from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP6_PATH


class PushTheButton(Game):
    name = 'PushTheButton'
    pack = JPP6_PATH
    folder = '../data/pp6/button/'
    build = '../build/uk/JPP6/Button/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]
        prompts = []
        for kind in ['MoralityTests', 'DrawingTests', 'RatingTests', 'WritingTests']:
            for c in self.read_jet(kind)['content']:
                o = self.read_content(c['id'], kind)
                prompts.append(o['HumanPromptText']['v'])
                prompts += [o[f'AlienPromptText{i}']['v'] for i in range(10) if f'AlienPromptText{i}' in o]
        strings, words = count_strings_and_words([
            self.read_localization(),
            audios,
            prompts
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
