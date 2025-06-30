from datetime import datetime

from paths import JPP5_PATH, JPP5_RELEASE_PATH
from .split import SplitTheRoom
from ..pack import GamePack


class JPP5(GamePack):
    path_game = JPP5_PATH
    path_release = JPP5_RELEASE_PATH
    install_date = datetime(2024, 10, 13, 20, 10)
    release_name = 'JPP5-ua.zip'
    games = [SplitTheRoom]
    localizations = {
        '../build/uk/JPP5/localization.json': ['Localization.json'],
        '../build/uk/JPP5/localization_pack.json': ['games/Picker/Localization.json'],
    }
