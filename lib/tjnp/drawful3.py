from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import TJNP_PATH


class Drawful3(Game):
    name = 'Drawful3'
    pack = TJNP_PATH
    international = True
    folder = '../data/tjnp/drawful3/'
    build = '../build/uk/TJNP/Drawful3/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A' and v['locale'] == "en"
        ]
        strings, words = count_strings_and_words([
            self.read_localization(),
            audios,
            self.read_jet('Prompts'),
            self.read_jet('Decoys'),
        ], drop_keys=('themes',))
        print(f'Total strings: {strings}\nTotal words: {words}')
