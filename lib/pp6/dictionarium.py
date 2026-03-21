from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP6_PATH


class Dictionarium(Game):
    name = 'Ridictionary'
    pack = JPP6_PATH
    folder = './data/pp6/dictionarium/'
    build = './build/uk/JPP6/Dictionarium/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]
        strings, words = count_strings_and_words([
            self.read_localization(),
            audios,
            self.read_jet('SingleWords'),
            self.read_jet('SingleWordsDefinitions'),
            self.read_jet('Slang'),
            self.read_jet('SlangDefinitions'),
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
