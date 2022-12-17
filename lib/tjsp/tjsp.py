from datetime import datetime

from lib import TMP2, TeeKO
from lib.game import Game

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\starter-pack\jackbox-starter-pack-ua'


class TJSP(Game):
    def decode_all(self):
        t = TMP2()
        t.decode_all()
        t = TeeKO()
        t.decode_all()
        t.update_localization(rf'{PATH_GAME}\localization_manager.json', '../build/uk/localization_managerEN.json')
        t.update_localization(rf'{PATH_GAME}\LocalizationPause.json', '../build/uk/LocalizationPauseEN.json')
        t.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/LocalizationEN-MAIN.json')
        t.update_localization(rf'{PATH_GAME}\games\PartyPack\Localization.json', '../build/uk/LocalizationPack.json')
        t.update_localization(rf'{PATH_GAME}\localization_manager.json', '../build/uk/localization_managerEN.json')
        t.update_localization(rf'{PATH_GAME}\games\triviadeath2\Localization.json', '../build/uk/TMP2/LocalizationEN.json')
        t.update_localization(rf'{PATH_GAME}\games\AwShirt\Localization.json', '../build/uk/TeeKO/LocalizationShirts.json')

    def release(self, start_time: datetime):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, start_time)
