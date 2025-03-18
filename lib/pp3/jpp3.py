from datetime import datetime

from lib.game import Game
from paths import JPP3_PATH, JPP3_RELEASE_PATH
from .fakin import Fakin
from .guesspionage import Guesspionage
from .old_quiplash2 import OldQuiplash2
from .old_teeko import OldTeeKO
from .tmp import TMP


INSTALL_TIME = datetime(2024, 10, 15, 23)


class JPP3(Game):
    def decode_all(self):
        OldTeeKO().decode_all()
        OldQuiplash2().decode_all()
        Fakin().decode_all()
        Guesspionage().decode_all()
        TMP().decode_all()
        self.update_localization(rf'{JPP3_PATH}\Localization.json', '../build/uk/JPP3/localization.json')
        self.update_localization(rf'{JPP3_PATH}\games\Picker\Localization.json', '../build/uk/JPP3/localization_pack.json')

    def release(self):
        self.decode_all()
        self.copy_to_release(JPP3_PATH, JPP3_RELEASE_PATH, INSTALL_TIME)
        self.make_archive(JPP3_RELEASE_PATH, 'JPP3-ua.zip')
