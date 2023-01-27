from lib.common import write_json
from lib.drive import Drive

GAME = 'drawful2'
PROJECT = 'Jackbox UA'
AUDIO_PATH = '/Drawful2/audio_subtitles.json'
FOLDER_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\Drawful 2\content\en\Drawful2Prompt'

if __name__ == '__main__':
    d = Drive()
    d.copy_audio_to_drive_by_walk(GAME, FOLDER_PATH)
    links = d.get_files_links(GAME)
    write_json('../data/standalone/drawful2/audio_links.json', links)
    # c = Crowdin()
    # c.publish_audio_links(PROJECT_LIST[PROJECT], links, AUDIO_PATH)
