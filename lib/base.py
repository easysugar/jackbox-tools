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
