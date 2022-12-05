from datetime import datetime

from lib.crowdin import Crowdin
from settings.crowdin import PROJECT_LIST, GAME_PATHS

PROJECT = 'Jackbox Starter Pack'
GAME = 'tmp2'

if __name__ == '__main__':
    c = Crowdin(datetime(2022, 1, 1))
    contributors = c.get_top_contributors_usernames([PROJECT_LIST[PROJECT]], GAME_PATHS[GAME])
    print(*[x['name'] for x in contributors], sep='\n')
