from datetime import datetime

from lib.game import Game
from .teeko import TeeKO
from .tmp2 import TMP2

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\starter-pack\jackbox-starter-pack-ua'


class TJSP(Game):
    def decode_all(self):
        TMP2().decode_all()
        TeeKO().decode_all()
        self.update_localization(rf'{PATH_GAME}\localization_manager.json', '../build/uk/localization_managerEN.json')
        self.update_localization(rf'{PATH_GAME}\LocalizationPause.json', '../build/uk/LocalizationPauseEN.json')
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/LocalizationEN-MAIN.json')
        self.update_localization(rf'{PATH_GAME}\games\PartyPack\Localization.json', '../build/uk/LocalizationPack.json')
        self.update_localization(rf'{PATH_GAME}\localization_manager.json', '../build/uk/localization_managerEN.json')
        self.update_localization(rf'{PATH_GAME}\games\triviadeath2\Localization.json', '../build/uk/TMP2/LocalizationEN.json')
        self.update_localization(rf'{PATH_GAME}\games\AwShirt\Localization.json', '../build/uk/TeeKO/LocalizationShirts.json')

    def release(self, start_time: datetime):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, start_time)
        self.make_archive(PATH_RELEASE)
