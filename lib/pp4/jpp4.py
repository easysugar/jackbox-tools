from datetime import datetime

from lib.game import Game
from .monster import Monster

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 4'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\jpp4\jackbox-pack-4'


class JPP4(Game):
    def encode_all(self):
        self._encode_localization(rf'{PATH_GAME}\Localization.json', '../data/pp4/localization.json')
        self._encode_localization(rf'{PATH_GAME}\games\PartyPack\Localization.json', '../data/pp4/localization_pack.json')
        self._encode_localization(rf'{PATH_GAME}\games\MonsterMingle\Localization.json', '../data/pp4/monster/localization.json')
        self._encode_localization(rf'{PATH_GAME}\games\SurviveTheInternet\Localization.json', '../data/pp4/internet/localization.json')
        Monster().encode_all()

    def decode_all(self):
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/JPP3/localization.json')
        self.update_localization(rf'{PATH_GAME}\games\PartyPack\Localization.json', '../build/uk/JPP4/localization_pack.json')

    def release(self, start_time: datetime):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, start_time)
