import json

from lib.crowdin import Crowdin
from settings.crowdin import PROJECT_LIST, GAME_PATHS

SAVE_PATH = 'progress.json'

if __name__ == '__main__':
    c = Crowdin()
    progress = {}
    for project_id in PROJECT_LIST.values():
        directories = c.get_directories_ids(project_id)
        for game, path in GAME_PATHS.items():
            if path not in directories:
                continue
            progress[game] = c.get_directory_progress(project_id, directories[path])
    print(progress)
    with open(SAVE_PATH, 'w') as f:
        json.dump(progress, f, indent=4)
