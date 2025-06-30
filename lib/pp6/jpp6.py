from datetime import datetime

from paths import JPP6_PATH, JPP6_RELEASE_PATH
from ..pack import GamePack


class JPP6(GamePack):
    path_game = JPP6_PATH
    path_release = JPP6_RELEASE_PATH
    install_date = datetime(2025, 1, 1)
    release_name = 'JPP6-UA.zip'
    games = []  # OldTMP2
    localizations = {
        '../build/uk/JPP6/localization.json': ['Localization.json'],
        '../build/uk/JPP6/localization_pack.json': ['games/Picker/Localization.json'],
    }
