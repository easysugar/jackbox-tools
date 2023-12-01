import json

from lib.crowdin import Crowdin

SAVE_PATH = 'contributors.json'

if __name__ == '__main__':
    c = Crowdin()
    contributors = c.get_top_members_report()
    print(*[x['username'] for x in contributors], sep='\n')
    with open(SAVE_PATH, 'w', encoding='utf-8') as f:
        json.dump(contributors, f, indent=4, ensure_ascii=False)
