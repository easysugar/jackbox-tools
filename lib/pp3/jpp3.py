from datetime import datetime

from paths import JPP3_PATH, JPP3_RELEASE_PATH
from .fakin import Fakin
from .guesspionage import Guesspionage
from .old_quiplash2 import OldQuiplash2
from .old_teeko import OldTeeKO
from .tmp import TMP
from ..pack import GamePack


class JPP3(GamePack):
    path_game = JPP3_PATH
    path_release = JPP3_RELEASE_PATH
    install_date = datetime(2024, 10, 15, 23)
    release_name = 'JPP3-UA.zip'
    games = [Fakin, OldQuiplash2, OldTeeKO, TMP, Guesspionage]
    localizations = {
        './build/uk/JPP3/localization.json': ['Localization.json'],
        './build/uk/JPP8/localization_pack.json': ['games/Picker/Localization.json'],
    }
