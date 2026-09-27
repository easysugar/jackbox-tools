import os
import re

from lib.game import Game, update_localization, clean_text
from lib.pp4.fibbage3 import is_translated
from paths import JPP8_PATH


def build_text(*args):
    return '\n'.join([
        build_text(*a) if isinstance(a, list) else a.strip()
        for a in args if a
    ])


class TheWheelOfEnormousProportions(Game):
    name = 'TheWheel'
    pack = JPP8_PATH
    international = True
    folder = './data/pp8/wheel/'
    build = './build/uk/JPP8/Wheel/'

    def decode_localization(self):
        update_localization(os.path.join(self.game_path, 'Localization.json'), os.path.join(self.build, 'Localization.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationManager.json'), os.path.join('./build/uk/JPP8/', 'LocalizationManager.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationPause.json'), os.path.join('./build/uk/JPP8/', 'LocalizationPause.json'))

    def encode_tapping_list(self):
        obj = self.read_jet('TappingList')
        result = {}
        for c in obj['content']:
            cid = c['id']
            prompt = c['prompt']
            answers = '\n'.join([_['text'] for _ in c['answers']])
            decoys = '\n'.join([_['text'] for _ in c['decoys']])
            text = build_text(prompt, '+', answers, '-', decoys)
            result[cid] = text
        self.write_to_data('tapping_list.json', result)

    def decode_tapping_list(self):
        trans = self.read_from_build('tapping_list.json')
        obj = self.read_jet('TappingList')
        result = []
        for c in obj['content']:
            if not is_translated(trans[c['id']]):
                continue
            prompt, pls, *t = trans[c['id']].strip().splitlines()
            assert pls == '+'
            c['prompt'] = prompt
            assert '-' in t, f'Incorrect text: {t}'
            answers = t[:t.index('-')]
            decoys = t[t.index('-') + 1:]
            c['answers'] = [{'text': a} for a in answers]
            c['decoys'] = [{'text': d} for d in decoys]
            result.append(c)
        obj['content'] = result
        self.write_jet('TappingList', obj)

    def encode_number_target(self):
        obj = self.read_jet('NumberTarget')
        result = {}
        for c in obj['content']:
            cid = c['id']
            prompt = c['prompt']
            unit = c['unit'].strip()
            if unit:
                prompt = prompt + ' ' + unit
                assert unit.startswith('(') and unit.endswith(')')
            value = c['value']
            text = build_text(prompt, value)
            result[cid] = text
        self.write_to_data('number_target.json', result)

    def decode_number_target(self):
        trans = self.read_from_build('number_target.json')
        obj = self.read_jet('NumberTarget')
        result = []
        for c in obj['content']:
            if not is_translated(trans[c['id']]):
                continue
            prompt, answer = trans[c['id']].strip().splitlines()
            assert float(answer)
            c['value'] = answer
            unit = ''
            if prompt.strip().endswith(')'):
                prompt, unit = prompt.rsplit('(', 1)
                unit = '(' + unit
            prompt = prompt.strip()
            assert '?' in prompt, f'Prompt {prompt} has no ?'
            c['unit'] = (unit or '')
            c['prompt'] = prompt
            result.append(c)
        obj['content'] = result
        self.write_jet('NumberTarget', obj)

    def encode_matching(self):
        obj = self.read_jet('Matching')
        result = {}
        for c in obj['content']:
            cid = c['id']
            prompt = c['prompt']
            prompt_header = c['promptHeader']
            assert len(c['headers']) == 1
            header = '{text} - {match}'.format(**c['headers'][0])
            answers = ['{text} - {match}'.format(**a) for a in c['answers']]
            text = build_text(prompt, prompt_header, header, answers)
            result[cid] = text
        self.write_to_data('matching.json', result)

    def decode_matching(self):
        trans = self.read_from_build('matching.json')
        obj = self.read_jet('Matching')
        result = []
        for c in obj['content']:
            if not is_translated(trans[c['id']]):
                continue
            prompt, prompt_header, header, *answers = trans[c['id']].strip().splitlines()
            c['prompt'] = prompt
            c['promptHeader'] = prompt_header
            assert header.count(' - ') == 1
            header_a, header_b = header.split(' - ')
            c['headers'][0].update({'text': header_a, 'match': header_b})
            new_answers = []
            for ans in answers:
                if not ans:
                    continue
                assert ans.count(' - ') == 1
                a, b = ans.split(' - ')
                new_answers.append({'text': a, 'match': b})
            c['answers'] = new_answers
            result.append(c)
        obj['content'] = result
        self.write_jet('Matching', obj)

    def encode_rapid_fire(self):
        obj = self.read_jet('RapidFire')
        result = {}
        for c in obj['content']:
            cxt = {'crowdinContext': self.get_context(c, c['sort'], c['subtype'])}
            cid = c['id']
            prompt = c['prompt']
            unit = c['unit'].strip()
            if unit:
                prompt = prompt + ' ' + unit
                assert unit.startswith('(') and unit.endswith(')')
            c['answers'].sort(key=lambda x: float(x['value']))
            answers = [_['text'] for _ in c['answers']]
            if c['subtype'] in ('most/least', 'closest') and c['sort'] == 'ascending':
                answers = answers[::-1]
            text = build_text(prompt, answers)
            result[cid] = {'text': text, **cxt}
        self.write_to_data('rapid_fire.json', result)

    def decode_rapid_fire(self):
        trans = self.read_from_build('rapid_fire.json')
        obj = self.read_jet('RapidFire')
        result = []
        for c in obj['content']:
            t = trans[c['id']]['text']
            if not is_translated(t):
                continue
            prompt, *answers = t.strip().splitlines()
            unit = re.search(r' (\(.*?\))$', prompt)
            unit = '' if not unit else unit.group()
            c['unit'] = unit
            prompt = prompt.replace(unit, '') if unit else prompt
            c['prompt'] = prompt
            if c['subtype'] in ('most/least', 'closest') and c['sort'] == 'ascending':
                answers = answers[::-1]
            c['answers'] = [{'text': a, 'value': f'{i}'} for i, a in enumerate(answers)]
            result.append(c)
        obj['content'] = result
        self.write_jet('RapidFire', obj)

    def encode_typing_list(self):
        obj = self.read_jet('TypingList')
        result = {}
        for c in obj['content']:
            cxt = {'crowdinContext': self.get_context(c, c['subtype'], 'exact spelling' if c['exactSpelling'] else '')}
            cid = c['id']
            prompt = c['prompt']
            answers = []
            for ans in c['answers']:
                spellings = [ans['text'], *ans.get('altSpellings', [])]
                spellings = [_.replace(',', '').strip() for _ in spellings]
                answers.append(', '.join(spellings))
            text = build_text(prompt, answers)
            result[cid] = {'text': text, **cxt}
        self.write_to_data('typing_list.json', result)

    def decode_typing_list(self):
        trans = self.read_from_build('typing_list.json')
        obj = self.read_jet('TypingList')
        result = []
        for c in obj['content']:
            t = trans[c['id']]['text']
            if not is_translated(t):
                continue
            prompt, *answers = t.strip().splitlines()
            c['prompt'] = prompt
            spellings = [
                [_.strip() for _ in answer.strip().split(',') if _.strip()]
                for answer in answers
                if answer.strip()
            ]
            c['answers'] = [
                {'text': s[0], 'altSpellings': s[1:], "hint": ""}
                for s in spellings
            ]
            result.append(c)
        obj['content'] = result
        self.write_jet('TypingList', obj)

    def encode_guessing(self):
        obj = self.read_jet('Guessing')
        result = {}
        for c in obj['content']:
            cid = c['id']
            prompt = c['prompt']
            cxt = {'crowdinContext': self.get_context(c, prompt, c['answer'])}
            followup = c['followup'] or ''
            reveal = c['reveal'] or ''
            clues = []
            for cl in c['clues']:
                clue = cl['clue'].replace('’', "'")
                comment = cl.get('clueComment')
                if comment:
                    comment = re.split('[!.?]+', comment[len(clue) - 4:], 1)[-1].strip()
                    clue = clue + '\n' + comment
                clues.append(clue)
            answers = [c['answer'], *c.get('altSpellings', [])]
            for ans in answers:
                assert ',' not in ans
            answers = build_text(answers)
            result[cid] = {
                'followup': {'text': followup, **cxt},
                'prompt': {'text': prompt, **cxt},
                'clues': [{'text': clue, **cxt} for clue in clues],
                'reveal': {'text': reveal, **cxt},
                'answers': {'text': answers, **cxt},
            }
        self.write_to_data('guessing.json', result)

    def decode_guessing(self):
        trans = self.read_from_build('guessing.json')
        obj = self.read_jet('Guessing')
        result = []
        for c in obj['content']:
            t = trans[c['id']]
            if not is_translated(t['prompt']['text']):
                continue
            c['prompt'] = t['prompt']['text']
            c['followup'] = t['followup']['text'] or None
            c['reveal'] = t['reveal']['text'] or None
            answers = [_.strip() for _ in t['answers']['text'].strip().split('\n') if _.strip()]
            c['answer'] = answers[0]
            c['altSpellings'] = answers[1:]
            clues = []
            for clue in t['clues']:
                clue = clue['text'].strip()
                assert clue.count('\n') <= 1
                comment = ''
                if '\n' in clue:
                    clue, comment = clue.split('\n')
                    comment = clue + ' ' + comment
                clues.append({'clue': clue, 'clueComment': comment})
            c['clues'] = clues
            result.append(c)
        obj['content'] = result
        self.write_jet('Guessing', obj)

    def encode_answer_buckets(self):
        buckets = self.read_json('answerbuckets.json')['payload']
        result = []
        for i, b in enumerate(buckets):
            keyword = b['keywords'][0] if b['keywords'] else ''
            sequential = b['sequential'][0] if b['sequential'] else ''
            cxt = self.get_crowdin_context({}, keyword, sequential)
            result.append([
                {'text': ans, **cxt}
                for ans in b['answers']
            ])
        self.write_to_data('answer_buckets.json', result)

    def decode_answer_buckets(self):
        trans = self.read_from_build('answer_buckets.json')
        obj = self.read_json('answerbuckets.json')
        buckets = obj['payload']
        for i, b in enumerate(buckets[:len(trans)]):
            b['answers'] = [_['text'] for _ in trans[i]]
        self.write_json('answerbuckets.json', obj)

    def encode_audio_subtitles(self):
        obj = self.read_from_data('TheWheel.json')
        audio = {
            v['id']: {'text': clean_text(v['text']), 'crowdinContext': c.get('crowdinContext', '')}
            for c in obj['media']
            for v in c['versions']
            if c['type'] == 'A'
        }
        self.write_to_data('audio.json', audio)

    def decode_media(self):
        text = self.read_from_build('audio.json')
        text = {k: v['text'] for k, v in text.items()}
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'TheWheel.json',
                               trans=text, path_save=self.folder + 'translated_dict.txt')
