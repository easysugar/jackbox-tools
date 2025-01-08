from datetime import datetime

from .split import SplitTheRoom
from lib.game import Game
from paths import JPP5_PATH, JPP5_RELEASE_PATH

PATH_GAME = JPP5_PATH
PATH_RELEASE = JPP5_RELEASE_PATH
INSTALL_TIME = datetime(2024, 10, 13, 20, 10)


class JPP5(Game):
    def encode_all(self):
        self._encode_localization(rf'{PATH_GAME}\Localization.json', '../data/pp5/localization.json')
        self._encode_localization(rf'{PATH_GAME}\games\Picker\Localization.json', '../data/pp5/localization_pack.json')

    def decode_all(self):
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/JPP5/localization.json')
        self.update_localization(rf'{PATH_GAME}\games\Picker\Localization.json', '../build/uk/JPP5/localization_pack.json')
        SplitTheRoom().decode_all()

    def release(self):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, INSTALL_TIME)
        self.make_archive(PATH_RELEASE, 'JPP5-ua.zip')
