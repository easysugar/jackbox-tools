from datetime import datetime

from lib.game import Game
from .quiplash3 import Quiplash3
from .teeko import TeeKO
from .tmp2 import TMP2

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\games\tjsp\jackbox-starter-pack-ua'
INSTALL_TIME = datetime(2024, 7, 29, 21, 50)


class TJSP(Game):
    def decode_all(self):
        TMP2().decode_all()
        TeeKO().decode_all()
        Quiplash3().decode_all()

        self.update_localization(rf'{PATH_GAME}\LocalizationManager.json', '../build/uk/localization_managerEN.json')
        self.update_localization(rf'{PATH_GAME}\games\Picker\LocalizationManager.json', '../build/uk/localization_managerEN.json')
        self.update_localization(rf'{PATH_GAME}\games\AwShirt\LocalizationManager.json', '../build/uk/localization_managerEN.json')
        self.update_localization(rf'{PATH_GAME}\games\Quiplash3\LocalizationManager.json', '../build/uk/localization_managerEN.json')
        self.update_localization(rf'{PATH_GAME}\games\triviadeath2\LocalizationManager.json', '../build/uk/localization_managerEN.json')

        self.update_localization(rf'{PATH_GAME}\LocalizationPause.json', '../build/uk/LocalizationPauseEN.json')
        self.update_localization(rf'{PATH_GAME}\games\Picker\LocalizationPause.json', '../build/uk/LocalizationPauseEN.json')
        self.update_localization(rf'{PATH_GAME}\games\AwShirt\LocalizationPause.json', '../build/uk/LocalizationPauseEN.json')
        self.update_localization(rf'{PATH_GAME}\games\Quiplash3\LocalizationPause.json', '../build/uk/LocalizationPauseEN.json')
        self.update_localization(rf'{PATH_GAME}\games\triviadeath2\LocalizationPause.json', '../build/uk/LocalizationPauseEN.json')

        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/LocalizationEN-MAIN.json')
        self.update_localization(rf'{PATH_GAME}\games\Picker\Localization.json', '../build/uk/LocalizationPack.json')
        self.update_localization(rf'{PATH_GAME}\games\AwShirt\Localization.json', '../build/uk/TeeKO/LocalizationShirts.json')

    def release(self):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, INSTALL_TIME)
        self.make_archive(PATH_RELEASE, 'TheJackboxPartyStarter-UA.zip')
