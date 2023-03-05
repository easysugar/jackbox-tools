from collections import defaultdict


def encode_localization(obj: dict):
    try:
        obj = obj['table']['en']
    except KeyError:
        obj = obj['table']
    return obj


def decode_localization(obj, trans):
    if 'table' in trans:
        trans = trans['table']
    if 'en' not in trans:
        trans = {'en': trans}
    for key in obj['table']['en']:
        obj['table']['en'][key] = trans['en'][key]
    return obj


def encode_slogans(obj: dict):
    return {c['id']: c['suggestion'].strip() for c in obj['content']}


def decode_slogans(obj, translations):
    for c in obj['content']:
        c['suggestion'] = translations[c['id']]
    return obj


def encode_suggestions(obj: dict):
    return {c['id']: c['suggestion'].strip() for c in obj['content']}


def decode_suggestions(obj, translations):
    for c in obj['content']:
        c['suggestion'] = translations[c['id']]
    return obj


def encode_moderated_slogans(obj: dict):
    return {c['id']: c['slogan'].strip() for c in obj['content']}


def decode_moderated_slogans(obj, translations):
    for c in obj['content']:
        c['slogan'] = translations[c['id']]
    return obj


def encode_slogan_suggestions(obj: dict):
    return {c['id']: c['suggestion'].strip() for c in obj['content']}


def decode_slogan_suggestions(obj, translations):
    for c in obj['content']:
        c['suggestion'] = translations[c['id']]
    return obj


def encode_dictation(obj: dict):
    return {c['id']: '\n'.join(c['text']) for c in obj['content']}


def decode_dictation(obj: dict, translations: dict):
    for c in obj['content']:
        c['text'] = translations[c['id']].strip().split('\n')
    return obj


def encode_sequel(obj: dict):
    return {
        c['id']: {
            'text': '\n'.join([c['text']['main'], c['text'].get('sub', '')]).strip()
        }
        for c in obj['content']
        if c['text'].get('main')
    }


def decode_sequel(obj, translations):
    for c in obj['content']:
        if c['text'].get('main'):
            t = translations[c['id']]['text'].strip().split('\n')
            c['text']['main'] = t[0]
            if len(t) > 1:
                c['text']['sub'] = t[1]
    return obj


def _encode_tmp_question_template(obj: dict, host=False):
    assert len({c['id'] for c in obj['content']}) == len(obj['content'])
    result = {}
    for c in obj['content']:
        assert c['id'] not in result
        assert c['text'] is not None
        assert len(c['choices']) == 4
        assert not c['pic']
        corrects = [i['correct'] for i in c['choices']]
        assert corrects.count(True) == 1
        answer = corrects.index(True) + 1
        result[c['id']] = '{}\n{}\n{}'.format(
            c['text'].replace('[EventName=HOST/AltHost]', '') if host else c['text'],
            '\n'.join([i['text'] for i in c['choices']]),
            answer
        )
    return result


def encode_tmp_question(obj: dict):
    return _encode_tmp_question_template(obj, host=False)


def encode_tmp_question_host(obj: dict):
    return _encode_tmp_question_template(obj, host=True)


def _decode_tmp_question_template(obj, trans, host=False):
    prefix = '' if not host else '[EventName=HOST/AltHost]'
    for c in obj['content']:
        text, *choices, answer = trans[c['id']].strip().split('\n')
        answer = int(answer)
        assert answer in (1, 2, 3, 4)
        assert len(choices) == 4, f'there are should be 4 choices, not {len(choices)}. Context: {text}'
        c['text'] = prefix + text.strip()
        for i in range(4):
            c['choices'][i]['text'] = choices[i].strip()
            c['choices'][i]['correct'] = i + 1 == answer
    return obj


def decode_tmp_question(obj, trans):
    return _decode_tmp_question_template(obj, trans, host=False)


def decode_tmp_question_host(obj, trans):
    return _decode_tmp_question_template(obj, trans, host=True)


def encode_final_round(obj: dict):
    res = {}
    for q in obj['content']:
        assert set(q) == {'choices', 'id', 'isValid', 'text', 'us', 'x'}
        assert q['isValid'] == ''
        text = q['text']
        corrects = defaultdict(set)
        for c in q['choices']:
            assert set(c) == {'correct', 'difficulty', 'text'}
            assert c['correct'] in (True, False)
            assert c['difficulty'] in (-1, 0, 1)
            assert c['text'].strip()
            t = c['text'].strip()
            corrects[c['correct']].add(t)
        for c, answers in corrects.items():
            text += '\n' + '-+'[c] + '\n' + '\n'.join(answers)
        res[q['id']] = text
    return res


def decode_final_round(obj, trans):
    for c in obj['content']:
        text, *answers = trans[c['id']].strip().split('\n')
        c['text'] = text.strip()
        assert len(answers) > 1
        corrects = defaultdict(set)
        sign = None
        for a in answers:
            if a in ('+', '-'):
                sign = a
            else:
                assert sign is not None
                corrects[sign].add(a)
        c['choices'] = [{'text': a.strip(), 'correct': s == '+', 'difficulty': 0} for s, alist in corrects.items() for a in alist]
        # random.shuffle(c['choices'])
    return obj


def decode_question_bomb(obj, trans):
    res = _decode_tmp_question_template(obj, trans, True)
    colors = {
        'жовтий': 'yellow',
        'синій': 'blue',
        'зелений': 'green',
        'білий': 'white',
        'червоний': 'red',
        'оранжевий': 'orange',
        'фіолетовий': 'purple',
        'чорний': 'black',
        'блакитний': 'blue',
    }
    for i in res['content']:
        for c in i['choices']:
            c['controllerClass'] = colors[c['text']]
    return res


def encode_quiplash(obj: dict):
    return {c['id']: c['prompt'].replace('[EventName=HOST/AltHost]', '') for c in obj['content']}


def decode_quiplash(obj, translations):
    for c in obj['content']:
        c['prompt'] = '[EventName=HOST/AltHost]' + translations[c['id']]
    return obj


def encode_mirror(obj):
    return {c['id']: c['password'] for c in obj['content']}


def decode_mirror(obj, translations):
    for c in obj['content']:
        c['password'] = translations[c['id']]
    return obj


def encode_mind_meld(obj):
    separator = ', '
    result = {}
    for c in obj['content']:
        answers = []
        for a in c['answers']:
            assert a['answer'] not in a['alt']
            alts = []
            for ans in [a['answer']] + a['alt']:
                if ans != '':
                    assert separator.strip() not in ans
                    alts.append(ans)
            answers.append(separator.join(alts))
        result[c['id']] = c['text'] + '\n' + '\n'.join(answers)
    return result


def decode_mind_meld(obj, trans):
    separator = ', '
    for c in obj['content']:
        t = trans[c['id']]
        prompt, *answers = t.strip().split('\n')
        c['text'] = prompt
        c['answers'] = []
        for a in answers:
            atext, *alt = a.strip().split(separator)
            c['answers'].append({
                'answer': atext,
                'alt': [''] if not alt else list(alt),
            })
    return obj
