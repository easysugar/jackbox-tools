from lib.crowdin import Crowdin, PROJECT_LIST
from lib.drive import Drive

GAME = 'drawful2'
PROJECT = 'Jackbox UA'
AUDIO_PATH = '/Drawful2/audio_subtitles.json'

if __name__ == '__main__':
    d = Drive()
    d.copy_audio_files_to_drive(GAME)
    links = d.get_files_links(GAME)
    c = Crowdin()
    c.publish_audio_links(PROJECT_LIST[PROJECT], links, AUDIO_PATH)
