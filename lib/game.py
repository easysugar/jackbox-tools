import functools
import re
import zipfile
from datetime import datetime
from typing import Dict, Union

import tqdm

from .common import *


class Game:
    def __init__(self, game_path: str = None, is_international: bool = False):
        self.game_path = getattr(self, 'game', game_path)
        self.is_international = getattr(self, 'international', is_international)
        self.game_name = getattr(self, 'name', None)

    def _get_path_kind(self, kind: str) -> str:
        if self.game_name and not kind.startswith(self.game_name):
            kind = self.game_name + kind
        if self.is_international:
            return os.path.join(self.game_path, 'content', 'en', kind)
        else:
            return os.path.join(self.game_path, 'content', kind)

    def get_content_path(self, cid: str | int, kind: str):
        return os.path.join(self._get_path_kind(kind), str(cid))

    def read_content(self, cid: str | int, kind: str) -> dict:
        return read_from_folder(str(cid), self._get_path_kind(kind))

    def write_content(self, cid: str | int, kind: str, content: dict):
        write_to_folder(cid, self._get_path_kind(kind), content)

    def read_jet(self, kind: str) -> dict:
        return self._read_json(self._get_path_kind(kind) + '.jet')

    def write_jet(self, kind: str, obj: dict) -> dict:
        return self._write_json(self._get_path_kind(kind) + '.jet', obj)

    def read_from_data(self, filename: str) -> dict:
        return self._read_json(os.path.join(getattr(self, 'folder'), filename))

    def write_to_data(self, filename: str, obj: dict):
        self._write_json(os.path.join(getattr(self, 'folder'), filename), obj)

    def read_from_build(self, filename: str) -> dict:
        return self._read_json(os.path.join(getattr(self, 'build'), filename))

    def get_kind_cids(self, kind: str) -> list[str]:
        return os.listdir(self._get_path_kind(kind))

    def copy_audio_to_content(self, cid: str | int, kind: str, audio_id: str, src_folder: str, src_audio_id: str = None):
        src = os.path.join(src_folder, f'{src_audio_id or audio_id}.ogg')
        dst = os.path.join(self.get_content_path(cid, kind), f'{audio_id}.ogg')
        copy_file(src, dst)

    @staticmethod
    def get_context(content: dict, title: str = None) -> str:
        cxt = title or ''
        if content.get('x') or content.get('us'):
            if cxt:
                cxt += '\n-------------'
            if content.get('us'):
                cxt += '\nfor USA'
            if content.get('x'):
                cxt += '\n18+'
        return cxt.strip()

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
        return read_json(src)

    @staticmethod
    def _write_json(dst: str, obj):
        return write_json(dst, obj)

    # @staticmethod
    # def _encode_for_swf(text: str):
    #     return '^' + text.replace("'", r"\'").replace('"', r'\"') + '^'

    # def replace_subtitles(self, path_original: str, path_expanded: str, path_translated: str, dst: str):
    #     media = self._read(path_original)
    #     expanded = self._read_json(path_expanded)
    #     translated = self._read_json(path_translated)
    #     text_map = {v['text']: translated[v['id']] for c in expanded for v in c['versions']
    #                 if v['id'] in translated}
    #     for old, new in text_map.items():
    #         old = self._encode_for_swf(old)
    #         new = self._encode_for_swf(new)
    #         assert media.count(old) == 1, f'Count of `{old}` should be equal to 1, not {media.count(old)}'
    #         media = media.replace(old, new)
    #     self._write(dst, media)

    def encode_all(self):
        print('Encoding', self.__class__.__name__)
        for f in tqdm.tqdm(dir(self)):
            if f.startswith('encode_') and f != 'encode_all' and callable(getattr(self, f)):
                getattr(self, f)()

    def decode_all(self):
        print('Decoding', self.__class__.__name__)
        to_call = [f for f in dir(self) if (f.startswith('decode_') or f.startswith('unpack_')) and f != 'decode_all' and callable(getattr(self, f))]
        to_call.sort()  # decode first, unpack second
        for f in tqdm.tqdm(to_call):
            getattr(self, f)()

    @staticmethod
    def _encode_subtitles(obj: dict, _type='A', tags='en') -> Dict[str, str]:
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == _type and v['tags'] == tags}

    def _update_media_dict(self, source: str, translation: Dict[str, str], editable: str):
        return self._update_media_dict_template(source, translation, editable, r'^\$\[(\d+)]\[en].*$')

    def _update_old_media_dict(self, source: str, translation: Dict[str, str], editable: str):
        return self._update_media_dict_template(source, translation, editable, r'^[\$#]\[(\d+)].*$')

    def _encode_localization(self, source: str, destination: str):
        obj = self._read_json(source)
        try:
            obj = obj['table']['en']
        except KeyError:
            obj = obj['table']
        self._write_json(destination, obj)

    @staticmethod
    def _update_media_dict_template(source, translation, editable, match_pattern):
        lines = editable.split('\n')
        mids = set()
        processed = set()
        for i, l in enumerate(lines):
            match = re.search(match_pattern, l)
            if match:
                mid = match.group(1)
                if mid not in translation:
                    # print('mid not in translation', mid)
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
                text = text.replace("'", r"\'").replace('"', r'\"')
                trans = translation[mid].replace("'", r"\'").replace('"', r'\"').replace('\n', r'\n')
                old = '^' + text + '^'
                new = '^' + replace_suffix(text, trans) + '^'
                source = source.replace(old, new, 1)
        return source

    def _decode_swf_media(self, path_media: str, path_expanded: str, trans: dict, path_save: str, ignore_tags=False):
        media = self._read(path_media)
        cnt_sep = media.count('^')
        expanded = self._read_json(path_expanded)
        if isinstance(expanded, dict) and expanded.get('media'):
            expanded = expanded['media']
        orig = {str(v['id']): v['text'] for c in expanded for v in c['versions'] if 'text' in v}
        mapp = {}
        for oid in trans:
            if not trans[oid].strip():
                continue
            old = '^' + orig[oid] + '^'
            assert '^' not in trans[oid]
            if ignore_tags:
                new = '^' + trans[oid] + '^'
            else:
                new = '^' + replace_tags(orig[oid], trans[oid]) + '^'
            old, new = media_encoder(old), media_encoder(new)
            mapp[old] = new
        for old, new in mapp.items():
            assert media.count(old) == 1, "String {0} has count {1}, but should be 1".format(old, media.count(old))
            media = media.replace(old, new)
        assert media.count('^') == cnt_sep
        self._write(path_save, media)


def update_localization(src: str, *translations: str):
    obj = read_json(src)
    trans = {}
    for path in translations:
        t = read_json(path)
        t = t.get('table', t)
        t = t.get('en', t)
        trans.update(t)
    if set(obj['table']['en']) > set(trans):
        print(f'Source has untranslated fields: {", ".join(set(obj["table"]["en"]) - set(trans))}')
    obj['table']['en'].update(trans)
    write_json(src, obj)


def media_encoder(s: str):
    return s.replace('\n', r'\n').replace("'", r"\'").replace('"', r'\"')


def read_from_folder(cid: str, path_folder: str):
    path_folder = path_folder.removesuffix('.jet')
    path = os.path.join(path_folder, str(cid), 'data.jet')
    x = read_json(path)
    return {_['n']: _ for _ in x['fields']}


def write_to_folder(cid: str, path_folder: str, value: dict):
    path = os.path.join(path_folder.removesuffix('.jet'), str(cid), 'data.jet')
    x = {'fields': list(value.values())}
    write_json(path, x)


def decode_mapping(*files, out_json=True, out=True):
    """Read several JSON files and write result into a new file"""

    def decorator(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            dst = files[-1] if out else None
            objs = [self._read_json(f) for f in (files[:-1] if out else files)]
            obj = func(self, *objs, *args, **kwargs)
            obj = transform(obj)
            if dst:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                self._write_json(dst, obj) if out_json else self._write(dst, obj)

        return wrapped

    return decorator


encode_mapping = decode_mapping


def transform(obj):
    if isinstance(obj, str):
        return re.sub(r"[ʼ`']", "’", obj)
    if isinstance(obj, list):
        return [transform(_) for _ in obj]
    if isinstance(obj, tuple):
        return tuple(transform(_) for _ in obj)
    if isinstance(obj, dict):
        return {k: transform(v) for k, v in obj.items()}
    return obj


def get_suffix(s: str) -> str:
    return re.search(r'(\[[\w=/,]+]\s*)*$', s).group()


def get_prefix(s: str) -> str:
    return re.search(r'^(\[[\w=/,]+]\s*)*', s).group()


def remove_suffix(s: str):
    return s.removesuffix(get_suffix(s))


def remove_prefix(s: str):
    return s.removeprefix(get_prefix(s))


def clean_text(s: str):
    return remove_prefix(remove_suffix(s.strip()).strip()).strip()


def normalize_text(s: str):
    return remove_prefix(remove_suffix(s.strip().lower()).strip()).strip()


def replace_suffix(src: str, dst: str) -> str:
    return remove_suffix(dst) + get_suffix(src)


def replace_tags(src: str, dst: str) -> str:
    return get_prefix(src) + remove_prefix(remove_suffix(dst)) + get_suffix(src)
