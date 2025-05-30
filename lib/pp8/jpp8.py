from datetime import datetime

from lib.game import Game
from paths import JPP8_PATH, JPP8_RELEASE_PATH
from .jobjob import JobJob
from .drawful3 import Drawful3

PATH_GAME = JPP8_PATH
PATH_RELEASE = JPP8_RELEASE_PATH
INSTALL_DATE = datetime(2025, 5, 20)


class JPP8(Game):
    def decode_all(self):
        JobJob().decode_all()
        Drawful3().decode_all()
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/JPP8/localization.json')
        self.update_localization(rf'{PATH_GAME}\games\Picker\Localization.json', '../build/uk/JPP8/localization_pack.json')

    def release(self):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, INSTALL_DATE)
        self.make_archive(PATH_RELEASE, 'JPP8-UA.zip')
