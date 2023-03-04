# encode

def encode_slogans(obj: dict):
    return {c['id']: c['suggestion'].strip() for c in obj['content']}


def encode_suggestions(obj: dict):
    return {c['id']: c['suggestion'].strip() for c in obj['content']}


def encode_moderated_slogans(obj: dict):
    return {c['id']: c['slogan'].strip() for c in obj['content']}


def encode_slogan_suggestions(obj: dict):
    return {c['id']: c['suggestion'].strip() for c in obj['content']}


def _encode_localization(obj: dict):
    try:
        obj = obj['table']['en']
    except KeyError:
        obj = obj['table']
    return obj


# decode

def decode_slogans(obj, translations):
    for c in obj['content']:
        c['suggestion'] = translations[c['id']]
    return obj


def decode_suggestions(obj, translations):
    for c in obj['content']:
        c['suggestion'] = translations[c['id']]
    return obj


def decode_moderated_slogans(obj, translations):
    for c in obj['content']:
        c['slogan'] = translations[c['id']]
    return obj


def decode_slogan_suggestions(obj, translations):
    for c in obj['content']:
        c['suggestion'] = translations[c['id']]
    return obj


def update_localization(obj, trans):
    if 'table' in trans:
        trans = trans['table']
    if 'en' not in trans:
        trans = {'en': trans}
    for key in obj['table']['en']:
        obj['table']['en'][key] = trans['en'][key]
    return obj
