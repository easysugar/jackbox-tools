import re
from typing import Any, Tuple, Optional


def count_strings_and_words(obj: Any, drop_keys: Optional[tuple] = None) -> Tuple[int, int]:
    if isinstance(obj, str) and not obj.isdigit() and obj and not obj.isspace():
        return 1, len(re.findall(r'\S+', obj))
    if isinstance(obj, list):
        strings, words = 0, 0
        for item in obj:
            x, y = count_strings_and_words(item, drop_keys)
            strings += x
            words += y
        return strings, words
    if isinstance(obj, dict):
        if drop_keys:
            obj = {key: value for key, value in obj.items() if key not in drop_keys}
        return count_strings_and_words(list(obj.values()), drop_keys)
    return 0, 0
