from datetime import datetime

from lib.game import Game

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 7'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\games\jpp7\jpp7'
INSTALL_DATE = datetime(2024, 2, 5)


class JPP7(Game):
    def decode_all(self):
        OldQuiplash3().decode_all()
        self.update_localization(rf'{PATH_GAME}\Localization.json', '../build/uk/JPP7/localization.json')
        self.update_localization(rf'{PATH_GAME}\games\PartyPack\Localization.json', '../build/uk/JPP7/localization_pack.json')

    def release(self):
        self.decode_all()
        self.copy_to_release(PATH_GAME, PATH_RELEASE, INSTALL_DATE)
        self.make_archive(PATH_RELEASE, 'JPP7-UA.zip')
