import pandas as pd

from lib.crowdin import Crowdin, PROJECT_LIST
from lib.drive import Drive

GAME = 'teeko'
PROJECT = 'Jackbox Starter Pack'
PATH = '/TeeKO/audio_subtitles.json'

if __name__ == '__main__':
    d = Drive()
    links = d.get_files_links(GAME)
    c = Crowdin()
    pid = PROJECT_LIST[PROJECT]
    sids = c.get_strings_ids_map(pid, file_path=PATH)
    sources = c.get_strings_texts(pid, list(sids.values()))
    trans = c.get_approved_translations(pid, list(sources))
    data = [
        {
            'id': sid,
            'text': sources[sids[sid]].replace('\n', ' '),
            'translation': trans[sids[sid]].replace('\n', ' '),
            'links': links[sid],
        }
        for sid in sids
    ]
    print('Table size:', len(data))
    df = pd.DataFrame(data)
    df.to_csv(f'{GAME}.tsv', sep='\t', encoding='utf8')
