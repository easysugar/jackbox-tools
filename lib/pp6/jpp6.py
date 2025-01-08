from datetime import datetime

from lib.game import Game
from paths import JPP6_PATH, JPP6_RELEASE_PATH
from .old_tmp2 import OldTMP2

PATH_GAME = JPP6_PATH
PATH_RELEASE = JPP6_RELEASE_PATH
INSTALL_DATE = datetime(2024, 10, 26)


class JPP6(Game):
    def decode_all(self):
        OldTMP2().decode_all()
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/JPP6/localization.json')
        self.update_localization(rf'{PATH_GAME}\games\Picker\Localization.json', '../build/uk/JPP6/localization_pack.json')

    def release(self):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, INSTALL_DATE)
        self.make_archive(PATH_RELEASE, 'JPP6-UA.zip')
