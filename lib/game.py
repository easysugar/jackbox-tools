import functools
import re
import zipfile
from datetime import datetime
from typing import Dict

import tqdm

from .common import *


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

    def update_localization(self, src: str, translation: str):
        obj = self._read_json(src)
        trans = self._read_json(translation)
        if 'table' in trans:
            trans = trans['table']
        if 'en' not in trans:
            trans = {'en': trans}
        assert set(obj['table']['en']) <= set(trans['en']), f'Source has untranslated fields: {", ".join(set(obj["table"]["en"])-set(trans["en"]))}'
        obj['table']['en'] = trans['en']
        self._write_json(src, obj)

    def copy_to_release(self, src: str, dst: str, start_ts: datetime):
        print('Coping to release')
        for root, dirs, files in tqdm.tqdm(list(os.walk(src, topdown=False))):
            for f in files:
                fpath = os.path.join(root, f)
                if 'копія' in fpath:
                    continue
                ts = datetime.fromtimestamp(os.path.getmtime(fpath))
                if ts >= start_ts or os.path.getctime(fpath) - os.path.getmtime(fpath) > 600:  # or ts <= start_ts - timedelta(days=1) or (os.path.getmtime(fpath) - os.path.getctime(fpath) > 60):
                    copy_file(fpath, fpath.replace(src, dst))

    @staticmethod
    def make_archive(src: str, archive_name: str = 'release.zip'):
        zip_path = os.path.join(src, '.releases', archive_name)
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        zip_process = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
        for folder_path, _, filenames in tqdm.tqdm(os.walk(src)):
            if any([f.startswith('.') for f in folder_path.split(os.sep)]):
                continue
            for filename in filenames:
                filepath = os.path.join(src, folder_path, filename)
                if not filename.startswith('.'):
                    zip_process.write(filepath, os.path.relpath(filepath, src))
        zip_process.close()
        print("Created archive")

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
                suffix = re.search(r'(\[[\w=]+])*$', text)
                text = text.replace("'", r"\'").replace('"', r'\"')
                trans = translation[mid].replace("'", r"\'").replace('"', r'\"').replace('\n', r'\n')
                old = '^' + text + '^'
                new = '^' + trans + ('' if not suffix else suffix.group(0)) + '^'
                source = source.replace(old, new, 1)
        return source

    def _decode_swf_media(self, path_media: str, path_expanded: str, trans: dict, path_save: str, ignore_suffix=False):
        media = self._read(path_media)
        cnt_sep = media.count('^')
        expanded = self._read_json(path_expanded)
        orig = {v['id']: v['text'] for c in expanded for v in c['versions'] if 'text' in v}
        mapp = {}
        for oid in trans:
            if not trans[oid].strip():
                continue
            old = '^' + orig[oid] + '^'
            suffix = '' if ignore_suffix else re.search(r'(\[.+])*$', orig[oid])
            assert '^' not in trans[oid]
            new = '^' + trans[oid] + ('' if not suffix else suffix.group()) + '^'
            old, new = media_encoder(old), media_encoder(new)
            mapp[old] = new
        for old, new in mapp.items():
            assert media.count(old) == 1, "String {0} has count {1}, but should be 1".format(old, media.count(old))
            media = media.replace(old, new)
        assert media.count('^') == cnt_sep
        self._write(path_save, media)


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
    return re.search(r'(\[[\w=/]+] ?)*$', s).group()


def get_prefix(s: str) -> str:
    return re.search(r'^(\[[\w=/]+])*', s).group()


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
