import functools
import re
from typing import Any, Tuple


def count_strings_and_words(obj: Any) -> Tuple[int, int]:
    if isinstance(obj, str) and not obj.isdigit() and obj and not obj.isspace():
        return 1, len(re.findall(r'\S+', obj))
    if isinstance(obj, list):
        return functools.reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), map(count_strings_and_words, obj), (0, 0))
    if isinstance(obj, dict):
        return count_strings_and_words(list(obj.values()))
    return 0, 0
