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
