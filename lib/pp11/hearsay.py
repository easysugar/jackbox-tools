from lib.game import Game
from lib.utils import count_strings_and_words
from paths import JPP11_PATH


class HearSay(Game):
    name = 'MicGame'
    pack = JPP11_PATH
    international = True
    folder = '../data/pp11/hearsay/'
    build = '../build/uk/JPP11/HearSay/'

    def count_words_to_translate(self):
        strings, words = count_strings_and_words([
            self.read_localization(),
            [[p['prompt'] for p in c['soundsToRecord']] for c in self.read_jet('MicGamePrompt')['content']]
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
