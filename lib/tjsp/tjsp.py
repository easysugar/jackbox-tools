from datetime import datetime

from paths import TJSP_PATH, TJSP_RELEASE_PATH
from .quiplash3 import Quiplash3
from .teeko import TeeKO
from .tmp2 import TMP2
from ..pack import GamePack


class TJSP(GamePack):
    path_game: TJSP_PATH
    path_release: TJSP_RELEASE_PATH
    install_date = datetime(2025, 4, 20)
    games = [TeeKO, TMP2, Quiplash3]
    release_name = 'TheJackboxPartyStarter-UA.zip'
    localizations = {
        '../build/uk/localizationManager.json': [
            'LocalizationManager.json', 'games/Picker/LocalizationManager.json', 'games/AwShirt/LocalizationManager.json',
            'games/Quiplash3/LocalizationManager.json', 'games/triviadeath2/LocalizationManager.json'
        ],
        '../build/uk/LocalizationPackPause.json': [
            'LocalizationPause.json', 'games/Picker/LocalizationPause.json', 'games/AwShirt/LocalizationPause.json',
            'games/Quiplash3/LocalizationPause.json', 'games/triviadeath2/LocalizationPause.json'
        ],
        '../build/uk/Localization.json': [
            'Localization.json', 'games/Picker/Localization.json', 'games/AwShirt/Localization.json'
        ],
    }
