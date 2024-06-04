import re
from collections import defaultdict

from lib.common import write_json
from lib.game import Game, decode_mapping, remove_suffix, normalize_text, read_from_folder, write_to_folder

PATH = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 6\games\TriviaDeath2'
OLD_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Starter\games\triviadeath2'


def transform_tags(s: str):
    return s.replace('[i]', '<i>').replace('[/i]', '</i>')


class OldTMP2(Game):
    folder = '../data/pp6/tmp2/'
    tjsp_folder = '../data/tjsp/tmp2/encoded/'
    build = '../build/uk/JPP6/TMP2/'
    tjsp_build = '../build/uk/TMP2/'

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

    @decode_mapping(PATH + r'\content\TDQuestion.jet', tjsp_folder + 'EncodedQuestion.json', folder + 'questions.json')
    def encode_question(self, obj, old):
        old = {re.sub(r'\W', '', _.split('\n')[-6].lower()) for _ in old.values()}
        res = {}
        for c in obj['content']:
            if re.sub(r'\W', '', c['text'].lower()) not in old:
                corrects = [i.get('correct') for i in c['choices']]
                answer = corrects.index(True) + 1
                res[c['id']] = '{}\n{}\n{}'.format(c['text'], '\n'.join([i['text'] for i in c['choices']]), answer)
                o = read_from_folder(c['id'], PATH + r'\content\TDQuestion')
                if intro := o.get('Intro', {}).get('s'):
                    res[c['id']] = intro + '\n' + res[c['id']]
        return res

    @decode_mapping(PATH + r'\content\TDQuestion.jet', OLD_PATH + r'\content\en\TDQuestion.jet',
                    build + 'questions.json', PATH + r'\content\TDQuestion.jet')
    def decode_question(self, obj, old, add):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            try:
                o = old[c['id']]
                c['text'] = transform_tags(o['text'])
                c['choices'] = [{'controllerClass': '', 'text': transform_tags(_['text'])} | ({'correct': True} if _['correct'] else {})
                                for _ in o['choices']]
            except KeyError:
                c['text'], *choices, answer = add[str(c['id'])].split('\n')
                c['choices'] = [{'controllerClass': '', 'text': _} for _ in choices]
                c['choices'][int(answer) - 1]['correct'] = True
            o = read_from_folder(c['id'], PATH + r'\content\TDQuestion.jet')
            if o.get('Intro') and o['Intro']['s']:
                n = read_from_folder(c['id'], OLD_PATH + r'\content\en\TDQuestion.jet')
                o['Intro']['s'] = n['Intro']['s']
                write_to_folder(c['id'], PATH + r'\content\TDQuestion.jet', o)
        return obj

    @decode_mapping(PATH + r'\content\QuiplashContent.jet', OLD_PATH + r'\content\en\QuiplashContent.jet', PATH + r'\content\QuiplashContent.jet')
    def decode_quiplash(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            c['prompt'] = transform_tags(old[c['id']]['prompt'].split('\n')[0])
            o = read_from_folder(c['id'], PATH + r'\content\QuiplashContent')
            o['PromptText']['v'] = c['prompt']
            o['PromptAudio']['s'] = c['prompt']
            write_to_folder(c['id'], PATH + r'\content\QuiplashContent', o)
        return obj

    @decode_mapping(PATH + r'\content\TDQuestionBomb.jet', OLD_PATH + r'\content\en\TDQuestionBomb.jet', PATH + r'\content\TDQuestionBomb.jet')
    def decode_bomb(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            c['text'] = transform_tags(old[c['id']]['text'])
            c['choices'] = old[c['id']]['choices']
            for _ in c['choices']:
                if _['correct'] is False:
                    _.pop('correct')
        return obj

    @decode_mapping(PATH + r'\content\TDQuestionGhost.jet', OLD_PATH + r'\content\en\TDQuestionGhost.jet', PATH + r'\content\TDQuestionGhost.jet')
    def decode_ghost(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            c['text'] = transform_tags(old[c['id']]['text'])
            for c1, c0 in zip(c['choices'], old[c['id']]['choices']):
                c1['text'] = c0['text']
        return obj

    @decode_mapping(PATH + r'\content\TDQuestionHat.jet', OLD_PATH + r'\content\en\TDQuestionHat.jet', PATH + r'\content\TDQuestionHat.jet')
    def decode_hat(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            c['text'] = transform_tags(old[c['id']]['text'])
            for c1, c0 in zip(c['choices'], old[c['id']]['choices']):
                c1['text'] = c0['text']
                if 'correct' in c1:
                    c1.pop('correct')
                if c0.get('correct'):
                    c1['correct'] = True
        return obj

    @decode_mapping(PATH + r'\content\TDQuestionKnife.jet', OLD_PATH + r'\content\en\TDQuestionKnife.jet', PATH + r'\content\TDQuestionKnife.jet')
    def decode_knife(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            c['text'] = transform_tags(old[c['id']]['text'])
            for c1, c0 in zip(c['choices'], old[c['id']]['choices']):
                c1['text'] = c0['text']
                if 'correct' in c1:
                    c1.pop('correct')
                if c0.get('correct'):
                    c1['correct'] = True
        return obj

    @decode_mapping(PATH + r'\content\TDQuestionMadness.jet', OLD_PATH + r'\content\en\TDQuestionMadness.jet',
                    PATH + r'\content\TDQuestionMadness.jet')
    def decode_madness(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            c['text'] = transform_tags(old[c['id']]['text'])
            for c1, c0 in zip(c['choices'], old[c['id']]['choices']):
                c1['text'] = c0['text']
                if 'correct' in c1:
                    c1.pop('correct')
                if c0.get('correct'):
                    c1['correct'] = True
        return obj

    @decode_mapping(PATH + r'\content\TDQuestionWig.jet', OLD_PATH + r'\content\en\TDQuestionWig.jet',
                    PATH + r'\content\TDQuestionWig.jet')
    def decode_madness(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            c['text'] = transform_tags(old[c['id']]['text'])
            for c1, c0 in zip(c['choices'], old[c['id']]['choices']):
                c1['text'] = c0['text']
                if 'correct' in c1:
                    c1.pop('correct')
                if c0.get('correct'):
                    c1['correct'] = True
        return obj

    @decode_mapping(PATH + r'\content\TDFinalRound.jet', tjsp_folder + 'final_questions.json', folder + 'final_questions.json')
    def encode_final_round(self, obj, old):
        old = {re.sub(r'\W', '', _.split('\n')[0].lower()) for _ in old.values()}
        res = {}
        for c in obj['content']:
            if re.sub(r'\W', '', c['text'].lower()) not in old:
                corrects = defaultdict(set)
                for ch in c['choices']:
                    corrects[ch['correct']].add(ch['text'].strip())
                text = c['text']
                for correct, answers in corrects.items():
                    text += '\n' + '-+'[correct] + '\n' + '\n'.join(answers)
                res[c['id']] = text
        return res

    @decode_mapping(PATH + r'\content\TDFinalRound.jet', OLD_PATH + r'\content\en\TDFinalRound.jet', PATH + r'\content\TDFinalRound.jet')
    def decode_final_round(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            o = old[c['id']]
            c['text'] = transform_tags(o['text'])
            c['choices'] = o['choices']
            for _ in c['choices']:
                _['text'] = transform_tags(_['text'])
            o = read_from_folder(c['id'], PATH + r'\content\TDFinalRound')
            o['Q']['s'] = c['text']
            write_to_folder(c['id'], PATH + r'\content\TDFinalRound', o)
        return obj

    @decode_mapping(PATH + r'\content\TDMindMeld.jet', OLD_PATH + r'\content\en\TDMindMeld.jet', PATH + r'\content\TDMindMeld.jet')
    def decode_mind_meld(self, obj, old):
        old = {int(_['id']): _ for _ in old['content']}
        for c in obj['content']:
            o = old[c['id']]
            c['text'] = transform_tags(o['text'])
            c['answers'] = o['answers']
            o = read_from_folder(c['id'], PATH + r'\content\TDMindMeld')
            o['PromptText']['v'] = c['text']
            o['PromptAudio']['s'] = c['text']
            write_to_folder(c['id'], PATH + r'\content\TDMindMeld', o)
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

    @decode_mapping(folder + 'expanded.json', tjsp_folder + 'text_subtitles.json', tjsp_folder + 'EncodedAudio.json', folder + 'media_mapping.json')
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
                    maps[v['id']] = texts[v['text']].pop(0)
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

    @decode_mapping(folder + 'expanded.json', tjsp_build + 'EncodedAudio.json', tjsp_build + 'in-game/text_subtitles.json', out=False)
    def decode_media(self, obj, tjsp_audio, tjsp_text):
        tjsp_text = {k: v for _ in tjsp_text.values() for k, v in _.items()}
        additional_audio = self._read_json(self.build + 'additional_audio.json')
        maps = self._read_json(self.folder + 'media_mapping.json')
        obj = {v['id']: v['text'] for c in obj for v in c['versions']}
        translations = {}  # version.id -> translated text
        for pp6_id, tjsp_id in maps.items():
            if tjsp_id in tjsp_audio:
                translations[pp6_id] = remove_suffix(tjsp_audio[tjsp_id])
            else:
                translations[pp6_id] = remove_suffix(tjsp_text[tjsp_id])
        for vid in additional_audio:
            translations[vid] = remove_suffix(additional_audio[vid])
        additional = {'270628': 'Ви отримаєте підказку, якщо вгадаєте правильну букву'}
        translations.update(additional)
        self._decode_swf_media(
            path_media=self.folder + 'dict.txt',
            path_expanded=self.folder + 'expanded.json',
            trans=translations,
            path_save=self.folder + 'translated_dict.txt',
        )
