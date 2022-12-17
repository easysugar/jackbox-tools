from datetime import datetime

from lib import OldTeeKO
from lib.game import Game

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 3'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\jpp3\jackbox-pack-3'


class JPP3(Game):
    def decode_all(self):
        OldTeeKO().decode_all()
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/JPP3/localization.json')
        self.update_localization(rf'{PATH_GAME}\games\PartyPack\Localization.json', '../build/uk/JPP3/localization_pack.json')

    def release(self, start_time: datetime):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, start_time)
