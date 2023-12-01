import json

from lib.crowdin import Crowdin
from settings.crowdin import PROJECT_LIST
from settings.report import GAMES

SAVE_PATH = 'progress.json'

if __name__ == '__main__':
    c = Crowdin()
    progress = {}
    for project_id in PROJECT_LIST.values():
        directories = c.get_directories_ids(project_id)
        for game in GAMES:
            path = GAMES[game].get('path')
            if path not in directories:
                continue
            progress[game] = c.get_directory_progress(project_id, directories[path])
    with open(SAVE_PATH, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=4)
