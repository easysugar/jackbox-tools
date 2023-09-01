import json
from datetime import datetime

from lib.crowdin import Crowdin

DATE = datetime(2023, 8, 1)
SAVE_PATH = 'contributors.json'

if __name__ == '__main__':
    c = Crowdin(DATE)
    contributors = c.get_top_members_report()
    print(*[x['username'] for x in contributors], sep='\n')
    with open(SAVE_PATH, 'w') as f:
        json.dump(contributors, f, indent=4, ensure_ascii=False)
