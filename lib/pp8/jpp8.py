from datetime import datetime

from lib.pack import GamePack
from paths import JPP8_PATH, JPP8_RELEASE_PATH
from .drawfulanimate import DrawfulAnimate
from .jobjob import JobJob
from .pollmine import PollMine
from .thewheelofenormousproportions import TheWheelOfEnormousProportions
from .weaponsdrawn import WeaponsDrawn


class JPP8(GamePack):
    path_game = JPP8_PATH
    path_release = JPP8_RELEASE_PATH
    install_date = datetime(2025, 5, 20)
    release_name = 'JPP8-UA.zip'
    games = [JobJob, DrawfulAnimate, PollMine, WeaponsDrawn, TheWheelOfEnormousProportions]
    localizations = {
        './build/uk/JPP8/localization.json': ['Localization.json'],
        './build/uk/JPP8/localizationPicker.json': ['games/Picker/Localization.json'],
    }
