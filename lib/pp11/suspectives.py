from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP11_PATH


class Suspectives(Game):
    name = 'DirtyDetectives'
    pack = JPP11_PATH
    international = True
    folder = './data/pp11/suspectives/'
    build = './build/uk/JPP11/Suspectives/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A' and v['locale'] == "en"
        ]
        strings, words = count_strings_and_words([
            self.read_localization(),
            audios,
            [[c['choices'], c['crime'], c['question']] for c in self.read_jet('Crime')['content']],
            [[c['evidence'], c['interrogations'], c['question'], c['reminder'], c['summary']]
             for c in self.read_jet('Input')['content']],
            [[c['evidence'], c['interrogations'], c['question'], c['reminder']]
             for c in self.read_jet('MultipleChoice')['content']],
            [[c['evidence'], c['interrogations'], c['question'], c['reminder'], c['summary'], c['choices']]
             for c in self.read_jet('Ranking')['content']],
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
