from datetime import datetime

from lib.game import Game
from .bracket import Bracketeering
from .doodle import Doodle
from .fibbage3 import Fibbage3
from .internet import Internet
from .monster import Monster

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 4'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\games\jpp4\jackbox-pack-4'
INSTALL_TIME = datetime(2024, 7, 29, 20, 10)


class JPP4(Game):
    def encode_all(self):
        self._encode_localization(rf'{PATH_GAME}\Localization.json', '../data/pp4/localization.json')
        self._encode_localization(rf'{PATH_GAME}\games\Picker\Localization.json', '../data/pp4/localization_pack.json')
        self._encode_localization(rf'{PATH_GAME}\games\MonsterMingle\Localization.json', '../data/pp4/monster/localization.json')
        self._encode_localization(rf'{PATH_GAME}\games\SurviveTheInternet\Localization.json', '../data/pp4/internet/localization.json')
        Monster().encode_all()
        Internet().encode_all()
        Doodle().encode_all()
        Bracketeering().encode_all()

    def decode_all(self):
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/JPP4/localization.json')
        self.update_localization(rf'{PATH_GAME}\games\Picker\Localization.json', '../build/uk/JPP4/localization_pack.json')
        Monster().decode_all()
        Internet().decode_all()
        Doodle().decode_all()
        Bracketeering().decode_all()
        Fibbage3().decode_all()

    def release(self):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, INSTALL_TIME)
        self.make_archive(PATH_RELEASE, 'JPP4-ua.zip')
