import functools
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

import tqdm


class Game:
    @staticmethod
    def _read(src: str):
        with open(src, 'r', encoding='utf8') as f:
            return f.read()

    @staticmethod
    def _write(dst: str, text: str):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'w', encoding='utf8') as f:
            return f.write(text)

    @staticmethod
    def _read_json(src: str):
        with open(src, 'rb') as f:
            return json.loads(f.read().decode('utf-8-sig'))

    @staticmethod
    def _write_json(dst: str, obj):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'w', encoding='utf8') as f:
            return json.dump(obj, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _encode_for_swf(text: str):
        return '^' + text.replace("'", r"\'").replace('"', r'\"') + '^'

    def replace_subtitles(self, path_original: str, path_expanded: str, path_translated: str, dst: str):
        media = self._read(path_original)
        expanded = self._read_json(path_expanded)
        translated = self._read_json(path_translated)
        text_map = {v['text']: translated[v['id']] for c in expanded for v in c['versions']
                    if v['id'] in translated}
        for old, new in text_map.items():
            old = self._encode_for_swf(old)
            new = self._encode_for_swf(new)
            assert media.count(old) == 1, f'Count of `{old}` should be equal to 1, not {media.count(old)}'
            media = media.replace(old, new)
        self._write(dst, media)

    def encode_all(self):
        for f in dir(self):
            if f.__name__.startswith('encode_') and f.__name__ != 'encode_all' and callable(getattr(self, f)):
                getattr(self, f)()

    def decode_all(self):
        for f in dir(self):
            if f.startswith('decode_') and f != 'decode_all' and callable(getattr(self, f)):
                getattr(self, f)()

    def unpack_all(self):
        for f in dir(self):
            if f.startswith('unpack_') and f != 'unpack_all' and callable(getattr(self, f)):
                getattr(self, f)()

    def update_localization(self, src: str, translation: str):
        obj = self._read_json(src)
        trans = self._read_json(translation)
        if 'en' not in trans:
            trans = {'en': trans}
        assert list(obj['table']['en']) == list(trans['en'])
        obj['table']['en'] = trans['en']
        self._write_json(src, obj)

    def copy_to_release(self, src: str, dst: str, start_ts: datetime):
        for root, dirs, files in tqdm.tqdm(list(os.walk(src, topdown=False))):
            for f in files:
                fpath = os.path.join(root, f)
                ts = datetime.fromtimestamp(os.path.getmtime(fpath))
                if ts >= start_ts:
                    _copy_file(fpath, fpath.replace(src, dst))

    def _update_media_dict(self, source: str, translation: Dict[str, str], editable: str):
        lines = editable.split('\n')
        mids = set()
        processed = set()
        for i, l in enumerate(lines):
            match = re.search(r'^\$\[(\d+)]\[en].*$', l)
            if match:
                mid = match.group(1)
                if mid not in translation:
                    continue
                assert int(mid)
                assert mid not in mids
                mids.add(mid)
                text = lines[i + 1]
                if lines[i + 2]:
                    text += r'\n' + lines[i + 2]

                if text in processed:
                    continue

                processed.add(text)
                suffix = re.search(r'(\[[\w=]+])*$', text)
                text = text.replace("'", r"\'").replace('"', r'\"')
                trans = translation[mid].replace("'", r"\'").replace('"', r'\"')
                old = '^' + text + '^'
                new = '^' + trans + ('' if not suffix else suffix.group(0)) + '^'
                source = source.replace(old, new, 1)
        return source

    # def update_editable_media(self, src: str, trans: dict, dst: str):
    #     body = self._read(src)
    #     lines = body.split('\n')
    #     mid2line = {}
    #     for i, l in enumerate(lines):
    #         match = re.search(r'^\$\[(\d+)].*$', l)
    #         if match:
    #             mid = match.group(1)
    #             assert int(mid)
    #             assert mid not in mid2line
    #             mid2line[mid] = i
    #     for mid in trans:
    #         line = lines[mid2line[mid] + 1]
    #         suffix = re.search(r'(\[[\w=]+])*$', line)
    #         lines[mid2line[mid] + 1] = trans[mid] + ('' if not suffix else suffix.group(0))
    #     self._write(dst, '\n'.join(lines))


def encode_mapping(src: str, dst: str):
    """Read JSON file from `src` and write function's result into `dst` file"""

    def decorator(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            obj = self._read_json(src)
            obj = func(self, obj, *args, **kwargs)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            self._write_json(dst, obj)

        return wrapped

    return decorator


def decode_mapping(*files):
    """Read several JSON files and write result into a new file"""

    def decorator(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            dst = files[-1]
            objs = [self._read_json(f) for f in files[:-1]]
            obj = func(self, *objs, *args, **kwargs)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            self._write_json(dst, obj)

        return wrapped

    return decorator


def _copy_file(src: str, dst: str):
    dst_folder = os.path.dirname(dst)
    Path(dst_folder).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
