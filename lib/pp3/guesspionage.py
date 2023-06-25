import re

from lib.common import read_json
from lib.encoder import decode_swf_media
from lib.game import read_from_folder, write_to_folder


def encode_audio_subtitles(obj: dict):
    sfx = re.compile(r'\[category=(sfx|music)]$|^\w+\d:\n|^PP_\w+|^Radio Play short |^Radio Play |Back button pressed')
    return {
        v['id']: {"text": v['text'].replace('[category=host]', '').replace('placeholder: ', '').strip(), "crowdinContext": c.get('context')}
        for c in obj
        for v in c['versions']
        if c['type'] == 'A' and not sfx.search(v['text'])
    }


def encode_audio_lobby(obj: dict):
    return {
        v['id']: v['text']
        for c in obj
        for v in c['versions']
        if c['type'] == 'A' and 'Radio' in v['text']
    }


def encode_text_subtitles(obj: dict):
    return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T'}


def decode_media(obj: dict, text: str, folder: str):
    text = read_json(text)
    decode_swf_media(
        path_media=folder + 'dict.txt',
        expanded=obj,
        trans=text,
        path_save=folder + 'translated_dict.txt',
    )


def encode_bonus_questions(obj: dict, folder: str):
    result = {}
    for c in obj['content']:
        cid = str(c['id'])
        x = read_from_folder(cid, folder)
        body = {x['QText']['v']: {
            "question": x['PollQ']['v'],
            'text': x['QText']['v'],
            'choices': [x['Choice%d' % i]['v'] for i in range(9)],
            'answers': [x['Val%d' % i]['v'] for i in range(9)],
            'data_mode': x['DataMode']['v'],
            'exp_results': x['ExpResults']['v'],
            'category': c['category'],
        }}
        result[cid] = body
    return result


def decode_bonus_questions(obj: dict, trans: dict, folder: str):
    for c in obj['content']:
        cid = str(c['id'])
        x = list(trans[cid].values())[0]
        c['category'] = x['category']
        o = read_from_folder(cid, folder)
        o['PollQ']['v'] = x['question']
        o['QText']['v'] = x['text']
        o['DataMode']['v'] = x['data_mode']
        o['ExpResults']['v'] = x['exp_results']

        for f in sorted(o):
            if f.startswith('Choice'):
                o[f]['v'] = x['choices'][int(f.replace('Choice', ''))]
            if f.startswith('Val'):
                o[f]['v'] = x['answers'][int(f.replace('Val', ''))]
                assert 0 <= int(o[f]['v']) <= 100

        write_to_folder(cid, folder, o)
    return obj


def encode_questions(obj: dict, folder: str):
    result = {}
    for c in obj['content']:
        cid = str(c['id'])
        x = read_from_folder(cid, folder)
        body = {x['QText']['v']: {
            "question": x['PollQ']['v'],
            'text': x['QText']['v'],
            'data_mode': x['DataMode']['v'],
            'exp_results': x['ExpResults']['v'],
            'answer': x['A']['v'],
            'choices': [x[i]['v'] for i in sorted(x) if i.startswith('Choice')],
            'target': x['Target']['v'],
            'category': c['category'],
        }}
        assert 0 <= int(x['A']['v']) <= 100
        result[cid] = body
    return result


def decode_questions(obj: dict, trans: dict, folder: str):
    for c in obj['content']:
        cid = str(c['id'])
        x = list(trans[cid].values())[0]
        c['category'] = x['category']
        o = read_from_folder(cid, folder)
        o['PollQ']['v'] = x['question']
        o['QText']['v'] = x['text']
        o['DataMode']['v'] = x['data_mode']
        o['ExpResults']['v'] = x['exp_results']
        o['A']['v'] = x['answer']
        o['Target']['v'] = x['target']

        for f in sorted(o):
            if f.startswith('Choice'):
                o[f]['v'] = x['choices'][int(f.replace('Choice', ''))]

        write_to_folder(cid, folder, o)
    return obj
