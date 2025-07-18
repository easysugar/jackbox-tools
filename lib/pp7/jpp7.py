from datetime import datetime

from paths import JPP7_PATH, JPP7_RELEASE_PATH
from .old_quiplash3 import OldQuiplash3
from .talks import Talks
from ..pack import GamePack


class JPP7(GamePack):
    path_game = JPP7_PATH
    path_release = JPP7_RELEASE_PATH
    install_date = datetime(2025, 1, 1)
    release_name = 'JPP7-UA.zip'
    games = [OldQuiplash3, Talks]
    localizations = {
        '../build/uk/JPP7/localization.json': ['Localization.json'],
        '../build/uk/JPP7/localization_pack.json': ['games/Picker/Localization.json'],
    }
