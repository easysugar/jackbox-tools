from datetime import datetime

from lib.pack import GamePack
from paths import JPP8_PATH, JPP8_RELEASE_PATH
from .drawful3 import Drawful3
from .jobjob import JobJob
from .. import PollMine


class JPP8(GamePack):
    path_game = JPP8_PATH
    path_release = JPP8_RELEASE_PATH
    install_date = datetime(2025, 5, 20)
    release_name = 'JPP8-UA.zip'
    games = [JobJob, Drawful3, PollMine]
    localizations = {
        '../build/uk/JPP8/localization.json': ['Localization.json'],
        '../build/uk/JPP8/localization_pack.json': ['games/Picker/Localization.json'],
    }
