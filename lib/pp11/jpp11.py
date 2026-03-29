from datetime import datetime

from lib.pack import GamePack
from paths import JPP11_PATH, JPP11_RELEASE_PATH
from .. import HearSay


class JPP11(GamePack):
    path_game = JPP11_PATH
    path_release = JPP11_RELEASE_PATH
    install_date = datetime(2025, 3, 24)
    release_name = 'JPP11-UA.zip'
    games = [HearSay]
    localizations = {
    }
