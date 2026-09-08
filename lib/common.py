import json
import os
import shutil
from pathlib import Path


def copy_file(src: str, dst: str):
    """Copy file from `src` to `dst`. Create all directories that are used in `dst` path"""
    dst_folder = os.path.dirname(dst)
    Path(dst_folder).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def read_txt(src: str):
    with open(src, 'r', encoding='utf8') as f:
        return f.read()


def read_json(src: str):
    with open(src, 'rb') as f:
        return json.loads(f.read().decode('utf-8-sig'))


def read(src: str, _format: str = None):
    if not _format:
        _format = src.rsplit(os.extsep, 1)[1]
    if _format in ('json', 'jet'):
        return read_json(src)
    else:
        return read_txt(src)


def write_json(dst: str, obj: dict):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf8', newline='\n') as f:
        return json.dump(obj, f, indent=2, ensure_ascii=False)
