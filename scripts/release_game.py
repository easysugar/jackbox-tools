from datetime import datetime

from lib import TMP2

GAME = 'tmp2'
PROJECT = 'Jackbox UA'
AUDIO_PATH = '/Drawful2/audio_subtitles.json'
PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter'
PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\starter-pack\jackbox-starter-pack-ua'
START_TIME = datetime(2022, 7, 25)

if __name__ == '__main__':
    t = TMP2()
    t.decode_all()
    t.update_localization(r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\localization_manager.json',
                          '../build/uk/localization_managerEN.json')
    t.update_localization(r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\LocalizationPause.json',
                          '../build/uk/LocalizationPauseEN.json')
    t.update_localization(r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\Localization.json',
                          '../build/uk/LocalizationEN-MAIN.json')
    t.update_localization(r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\games\PartyPack\Localization.json',
                          '../build/uk/LocalizationPack.json')

    t.copy_to_release(PATH_GAME, PATH_RELEASE, START_TIME)
