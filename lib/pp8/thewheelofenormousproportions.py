from lib.game import Game
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
