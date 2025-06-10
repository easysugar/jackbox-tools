from datetime import datetime

from lib.game import Game
from paths import JPP4_PATH, JPP4_RELEASE_PATH
from .bracket import Bracketeering
from .doodle import Doodle
from .fibbage3 import Fibbage3
from .internet import Internet
from .monster import Monster
from ..pack import GamePack


class JPP4(GamePack):
    path_game = JPP4_PATH
    path_release = JPP4_RELEASE_PATH
    install_date = datetime(2024, 10, 13, 20, 10)
    games = [Monster, Internet, Doodle, Bracketeering, Fibbage3]
    release_name = 'JPP4-ua.zip'
    localizations = {
        '../build/uk/JPP4/localization.json': ['Localization.json'],
        '../build/uk/JPP4/localization_pack.json': ['games/Picker/Localization.json'],
    }
