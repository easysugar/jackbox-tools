import pandas as pd

from lib.common import read_json, write_json
from lib.drive import Drive

GAME = 'fakin'
PROJECT = 'general'
PATH = '/JPP3/FakinIt/audio_subtitles.json'
PATH_IN_BUILD = '../build/uk' + PATH
PATH_LINKS_MAP = '../data/pp3/fakin/audio_links.json'
PATH_ENCODED = '../data/pp3/fakin/swf/audio_subtitles.json'
PATH_SAVE = f'../data/pp3/fakin/{GAME}.tsv'


def _get_data_drawful2(links, obj):
    return [
        {
            'id': sid,
            'prompt': value.split('\n', 1)[0],
            'comment': value.split('\n', 1)[1],
            'link': links.get(str(sid)) or '',
        }
        for sid, value in obj.items() if '\n' in value
    ]


def _get_data_default(links, obj, original):
    return [
        {
            'id': sid,
            'original': original[sid].replace('\n', ' ') if isinstance(original[sid], str) else original[sid]['text'].replace('\n', ' '),
            'context': '' if isinstance(original[sid], str) else (original[sid]['crowdinContext'] or '').replace('\n', ' '),
            'text': value.replace('\n', ' ') if isinstance(value, str) else value['text'].replace('\n', ' '),
            'link': links.get(str(sid)) or '',
        }
        for sid, value in obj.items()
    ]


def get_prompts_from_file():
    obj = read_json(PATH_IN_BUILD)
    links = read_json(PATH_LINKS_MAP)
    if GAME == 'drawful2':
        data = _get_data_drawful2(links, obj)
    else:
        original = read_json(PATH_ENCODED)
        data = _get_data_default(links, obj, original)
    print('Table size:', len(data))
    df = pd.DataFrame(data)
    df.to_csv(PATH_SAVE, sep='\t', encoding='utf8')


def upload_audio_subtitles():
    d = Drive()
    d.copy_audio_subtitles_to_drive(GAME)
    links = d.get_files_links(GAME)
    write_json(PATH_LINKS_MAP, links)


if __name__ == '__main__':
    # upload_audio_subtitles()
    get_prompts_from_file()
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
