import logging

from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP11_PATH


class LegendsOfTrivia(Game):
    name = 'TriviaRPG'
    pack = JPP11_PATH
    international = True
    folder = '../data/pp11/legends/'
    build = '../build/uk/JPP11/LegendsOfTrivia/'

    def count_words_to_translate(self):
        audios = [
            clean_text(v['text']) for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A' and v['locale'] == "en"
        ]
        strings, words = count_strings_and_words([
            self.read_localization(),
            audios,
            self.read_jet('DeathSave'),
            self.read_jet('Flurry'),
            self.read_jet('ImageTrivia'),
            self.read_jet('ListIt'),
            self.read_jet('MultipleChoice'),
            self.read_jet('MultipleChoiceOgre'),
            self.read_jet('MultipleChoiceTutorial'),
            self.read_jet('MultiSelection'),
            self.read_jet('ReverseMultipleChoice'),
            self.read_jet('Riddle'),
        ], ('theme', 'altText'))
        logging.debug('Total strings: %s\nTotal words: %s', strings, words)
