from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP11_PATH


class Doominate(Game):
    name = 'YouRuinedIt'
    pack = JPP11_PATH
    international = True
    folder = './data/pp11/doominate/'
    build = './build/uk/JPP11/Doominate/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A' and v['locale'] == "en"
        ]
        strings, words = count_strings_and_words([
            self.read_localization(),
            audios,
            self.read_jet('YouRuinedItFavoriteThings'),
            self.read_jet('YouRuinedItPunchlines'),
            self.read_jet('YouRuinedItUnruins'),
            [[c['punchlines'], c['setup']] for c in self.read_jet('YouRuinedItSetups')['content']],
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')
