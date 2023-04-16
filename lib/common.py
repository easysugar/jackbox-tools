import json
import os
import shutil
from pathlib import Path


def copy_file(src: str, dst: str):
    """Copy file from `src` to `dst`. Create all directories that are used in `dst` path"""
    dst_folder = os.path.dirname(dst)
    Path(dst_folder).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def read_json(src: str):
    with open(src, 'rb') as f:
        return json.loads(f.read().decode('utf-8-sig'))


def write_json(dst: str, obj: dict):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf8', newline='\n') as f:
        return json.dump(obj, f, indent=2, ensure_ascii=False)


def read_from_folder(cid: str, path_folder: str):
    path = os.path.join(path_folder, cid, 'data.jet')
    x = read_json(path)
    return {_['n']: _ for _ in x['fields']}


def write_to_folder(cid: str, path_folder: str, value: dict):
    path = os.path.join(path_folder, cid, 'data.jet')
    x = {'fields': list(value.values())}
    write_json(path, x)
