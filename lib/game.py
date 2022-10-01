import functools
import json
import os


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
