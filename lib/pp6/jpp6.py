from datetime import datetime

from lib.game import Game
from .old_tmp2 import OldTMP2

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 6'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\games\jpp6\jackbox-pack-6'


class JPP6(Game):
    def decode_all(self):
        OldTMP2().decode_all()
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/JPP3/localization.json')
        self.update_localization(rf'{PATH_GAME}\games\PartyPack\Localization.json', '../build/uk/JPP3/localization_pack.json')

    def release(self, start_time: datetime):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, start_time)
        self.make_archive(PATH_RELEASE)
