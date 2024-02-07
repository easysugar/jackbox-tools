import re
from collections import defaultdict

from lib.common import write_json
from lib.game import Game, decode_mapping, remove_suffix, normalize_text

PATH = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 6\games\TriviaDeath2'
OLD_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\games\triviadeath2'


def transform_tags(s: str):
    return s.replace('[i]', '<i>').replace('[/i]', '</i>')


class OldTMP2(Game):
    folder = '../data/pp6/tmp2/'
    old_folder = '../data/tjsp/tmp2/encoded/'
    build = '../build/uk/JPP6/TMP2/'

    @decode_mapping(PATH + r'\Localization.json', OLD_PATH + r'\Localization.json', folder + 'localization.json')
    def encode_localization(self, obj, old_obj):
        return {k: v for k, v in obj['table']['en'].items() if k not in old_obj['table']['en']}

    @decode_mapping(PATH + r'\Localization.json', OLD_PATH + r'\Localization.json', build + 'Localization.json', PATH + r'\Localization.json')
    def decode_localization(self, obj, old_obj, trans):
        l = obj['table']['en']
        l2 = old_obj['table']['en']
        for k in l:
            if l[k]:
                l[k] = l2.get(k) or trans[k]
        return obj

    @decode_mapping(PATH + r'\content\TDQuestion.jet', OLD_PATH + r'\content\en\TDQuestion.jet', folder + 'questions.json')
    def encode_question(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        res = {}
        for c in obj['content']:
            if c['id'] not in old:
                corrects = [i.get('correct') for i in c['choices']]
                answer = corrects.index(True) + 1
                res[c['id']] = '{}\n{}\n{}'.format(c['text'], '\n'.join([i['text'] for i in c['choices']]), answer)
        return res

    @decode_mapping(PATH + r'\content\TDQuestion.jet', OLD_PATH + r'\content\en\TDQuestion.jet',
                    build + 'questions.json', PATH + r'\content\TDQuestion.jet')
    def decode_question(self, obj, old, add):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            try:
                o = old[c['id']]
                c['text'] = o['text']
                c['choices'] = [{'controllerClass': '', 'text': _['text']} | ({'correct': True} if _['correct'] else {}) for _ in o['choices']]
            except KeyError:
                c['text'], *choices, answer = add[str(c['id'])].split('\n')
                c['choices'] = [{'controllerClass': '', 'text': _} for _ in choices]
                c['choices'][int(answer) - 1]['correct'] = True
        return obj

    @decode_mapping(PATH + r'\content\QuiplashContent.jet', OLD_PATH + r'\content\en\QuiplashContent.jet', PATH + r'\content\QuiplashContent.jet')
    def decode_quiplash(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            o = old[c['id']]
            c['prompt'] = o['prompt']
        return obj

    @decode_mapping(PATH + r'\content\TDFinalRound.jet', OLD_PATH + r'\content\en\TDFinalRound.jet', PATH + r'\content\TDFinalRound.jet')
    def decode_final_round(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            o = old[c['id']]
            c['text'] = o['text']
            c['choices'] = o['choices']
        return obj

    @decode_mapping(PATH + r'\content\TDMindMeld.jet', OLD_PATH + r'\content\en\TDMindMeld.jet', PATH + r'\content\TDMindMeld.jet')
    def decode_mind_meld(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            o = old[c['id']]
            c['text'] = o['text']
            c['answers'] = o['answers']
        return obj

    @decode_mapping(PATH + r'\content\TDMirror.jet', OLD_PATH + r'\content\en\TDMirror.jet', PATH + r'\content\TDMirror.jet')
    def decode_mirror(self, obj, old):
        for c, o in zip(obj['content'], old['content']):
            c['password'] = o['password']
            c['lines'] = o['lines']
        while len(obj['content']) > len(old['content']):
            obj['content'].pop()
        return obj

    @decode_mapping(PATH + r'\content\TDMirrorTutorial.jet', OLD_PATH + r'\content\en\TDMirrorTutorial.jet', PATH + r'\content\TDMirrorTutorial.jet')
    def decode_mirror_tutorial(self, obj, old):
        for c, o in zip(obj['content'], old['content']):
            c['password'] = o['password']
            c['lines'] = o['lines']
        return obj

    @decode_mapping(PATH + r'\content\TDSequel.jet', OLD_PATH + r'\content\en\TDSequel.jet', PATH + r'\content\TDSequel.jet')
    def decode_sequel(self, obj, old):
        old = {_['id']: _ for _ in old['content']}
        for c in obj['content']:
            c['text'] = old[c['id']]['text']
        return obj

    @decode_mapping(folder + 'expanded.json', old_folder + 'text_subtitles.json', old_folder + 'EncodedAudio.json', folder + 'media_mapping.json')
    def get_media_mappings(self, obj, old_text, old_audio):
        maps = {}
        texts = defaultdict(list)
        for _ in old_text.values():
            for cid, t in _.items():
                texts[t].append(cid)
        audio = defaultdict(list)
        for cid, a in old_audio.items():
            audio[normalize_text(a)].append(cid)
        additional = {}
        for c in obj:
            if c['type'] == 'T':
                for v in c['versions']:
                    if v['text'] not in texts:
                        if re.match(r'^(SFX/|MUSIC/|[a-z_]+\d$|\d+\w?$|(TD|death|intro|end|jump|bomb)\w+$|\W+$|[A-Z ]+$)',
                                    v['text'].strip()):
                            continue
                        raise Exception
                    maps[c['id']] = texts[v['text']].pop(0)
            elif c['type'] == 'A':
                for v in c['versions']:
                    t = normalize_text(v['text'])
                    if t not in audio:
                        additional[v['id']] = remove_suffix(v['text'])
                    else:
                        maps[v['id']] = audio[t].pop(0)
        if additional:
            write_json(self.folder + 'additional_audio.json', additional)
        return maps
