from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import TJNP_PATH


class LetMeFinish(Game):
    name = 'CAPTCHA'
    name_short = 'Captcha'
    pack = TJNP_PATH
    international = True
    folder = './data/tjnp/letmefinish/'
    build = './build/uk/TJNP/Letmefinish/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A' and v['locale'] == "en"
        ]
        strings, words = count_strings_and_words([
            self.read_localization(),
            audios,
            self.read_jet('ButtImages'),
            self.read_jet('ButtPrompts'),
            self.read_jet('CaptionImages'),
            self.read_jet('LineupImages'),
            self.read_jet('LineupPrompts'),
            self.read_jet('TutorialImages'),
        ], drop_keys=('themes', 'altText', 'category', 'naughtiness'))
        print(f'Total strings: {strings}\nTotal words: {words}')
