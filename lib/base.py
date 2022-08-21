import functools
import json


class Base:
    @staticmethod
    def _read_json(src: str):
        with open(src, 'r', encoding='utf8') as f:
            return json.load(f)

    @staticmethod
    def _write_json(dst: str, obj):
        with open(dst, 'w', encoding='utf8') as f:
            return json.dump(obj, f, indent=2, ensure_ascii=False)


def encode_mapping(src: str, dst: str):
    """Read JSON file from `src` and write function's result into `dst` file"""
    def decorator(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            obj = self._read_json(src)
            obj = func(self, obj, *args, **kwargs)
            self._write_json(dst, obj)
        return wrapped
    return decorator


def decode_mappings(original: str, translated: str, dst: str):
    """Read encoded file, translated mappings and write result into a new file"""
    def decorator(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            or_obj = self._read_json(original)
            tr_obj = self._read_json(translated)
            obj = func(self, or_obj, tr_obj, *args, **kwargs)
            self._write_json(dst, obj)
        return wrapped
    return decorator
