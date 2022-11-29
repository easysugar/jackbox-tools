import json
from datetime import datetime

from lib.crowdin import Crowdin

DATE = datetime(2022, 10, 31)
SAVE_PATH = 'contributors.json'

if __name__ == '__main__':
    c = Crowdin(DATE)
    contributors = c.get_top_contributors_usernames()
    with open(SAVE_PATH, 'w') as f:
        json.dump(contributors, f, indent=4)
