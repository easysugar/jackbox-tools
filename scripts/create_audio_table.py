import pandas as pd

from lib.common import read_json

GAME = 'drawful2-prompts'
PROJECT = 'general'
PATH = '/Drawful2/in-game/prompt.json'
PATH_IN_BUILD = '../build/uk' + PATH
PATH_LINKS_MAP = '../data/standalone/drawful2/audio_links.json'


def get_prompts_from_file():
    obj = read_json(PATH_IN_BUILD)
    links = read_json(PATH_LINKS_MAP)
    data = [
        {
            'id': sid,
            'prompt': value.split('\n', 1)[0],
            'comment': value.split('\n', 1)[1],
            'link': links.get(str(sid)) or '',
        }
        for sid, value in obj.items()
        if '\n' in value
    ]
    print('Table size:', len(data))
    df = pd.DataFrame(data)
    df.to_csv(f'{GAME}.tsv', sep='\t', encoding='utf8')


if __name__ == '__main__':
    get_prompts_from_file()

    # d = Drive()
    # links = d.get_files_links(GAME)
    # c = Crowdin()
    # pid = PROJECT_LIST[PROJECT]
    # sids = c.get_strings_ids_map(pid, file_path=PATH)
    # print('found sids')
    # sources = c.get_strings_texts(pid, list(sids.values()))
    # print('found sources')
    # trans = c.get_approved_translations(pid, list(sources))
    # print('found trans')
    # data = [
    #     {
    #         'id': sid,
    #         'prompt': trans[sids[sid]].split('\n', 1)[0],
    #         'comment': trans[sids[sid]].split('\n', 1)[1],
    #         # 'links': links[sid],
    #     }
    #     for sid in sids
    #     if '\n' in trans[sids[sid]]
    # ]
    # print('Table size:', len(data))
    # df = pd.DataFrame(data)
    # df.to_csv(f'{GAME}.tsv', sep='\t', encoding='utf8')
