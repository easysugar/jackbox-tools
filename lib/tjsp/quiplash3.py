from lib.game import Game, encode_mapping
from settings.quiplash3 import *


class Quiplash3(Game):
    folder = '../data/tjsp/quiplash3/encoded/'

    @encode_mapping(PATH_QUESTIONS_ROUND1, folder + 'round1.json')
    def encode_quiplash_questions_round1(self, obj: dict) -> dict:
        return {c['id']: '\n'.join((c['prompt'], '\n'.join(c['safetyQuips']))) for c in obj['content']}

    @encode_mapping(PATH_QUESTIONS_ROUND2, folder + 'round2.json')
    def encode_quiplash_questions_round2(self, obj: dict) -> dict:
        return {c['id']: '\n'.join((c['prompt'], '\n'.join(c['safetyQuips']))) for c in obj['content']}

    def encode_localization(self):
        self._encode_localization(PATH_LOCALIZATION, self.folder + 'localization.json')
