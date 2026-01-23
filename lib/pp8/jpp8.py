from datetime import datetime

from lib.pack import GamePack
from paths import JPP8_PATH, JPP8_RELEASE_PATH
from .drawfulanimate import DrawfulAnimate
from .jobjob import JobJob
from .pollmine import PollMine
from .weaponsdrawn import WeaponsDrawn
from .wheel import Wheel


class JPP8(GamePack):
    path_game = JPP8_PATH
    path_release = JPP8_RELEASE_PATH
    install_date = datetime(2025, 5, 20)
    release_name = 'JPP8-UA.zip'
    games = [JobJob, DrawfulAnimate, PollMine, WeaponsDrawn, Wheel]
    localizations = {
        '../build/uk/JPP8/localization.json': ['Localization.json'],
        '../build/uk/JPP8/localization_pack.json': ['games/Picker/Localization.json'],
    }
