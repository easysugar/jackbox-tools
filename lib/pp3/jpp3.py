from datetime import datetime

from lib.game import Game
from .fakin import Fakin
from .guesspionage import Guesspionage
from .old_quiplash2 import OldQuiplash2
from .old_teeko import OldTeeKO
from .tmp import TMP

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 3'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\games\jpp3\jackbox-pack-3'


class JPP3(Game):
    def decode_all(self):
        OldTeeKO().decode_all()
        OldQuiplash2().decode_all()
        Fakin().decode_all()
        Guesspionage().decode_all()
        TMP().decode_all()
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/JPP3/localization.json')
        self.update_localization(rf'{PATH_GAME}\games\PartyPack\Localization.json', '../build/uk/JPP3/localization_pack.json')

    def release(self, start_time: datetime):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, start_time)
        self.make_archive(PATH_RELEASE)
