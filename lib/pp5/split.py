from lib.game import Game, decode_mapping, read_from_folder, write_to_folder
from paths import JPP5_PATH

PATH = JPP5_PATH + r'\games\SplitTheRoom'


class SplitTheRoom(Game):
    folder = '../data/pp5/split/'
    build = '../build/uk/JPP5/SplitTheRoom/'

    @decode_mapping(folder + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T' and ' ' in v['text']}

    @decode_mapping(folder + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {v['id']: {"crowdinContext": c['context'], 'text': v['text'].replace('[category=host]', '').strip()}
                for c in obj for v in c['versions']
                if c['type'] == 'A'}

    def decode_localization(self):
        self.update_localization(PATH + r'\Localization.json', self.build + 'localization.json')

    @staticmethod
    def _encode_scenario(obj, path_folder):
        res = {}
        for c in obj['content']:
            context = c['scenarioText']
            if c['x']:
                context += '\n-------------18+'
            res[c['id']] = {
                'decoys': {'text': c['decoys'].replace(' | ', '\n'), 'crowdinContext': context},
                'category': {'text': c['category'], 'crowdinContext': context},
                'questionText': {'text': c['questionText'], 'crowdinContext': context},
            }
            if c['answerText']:
                res[c['id']]['answer'] = {'text': c['answerText'], 'crowdinContext': context}
            o = read_from_folder(str(c['id']), path_folder)
            scenario = ''
            for i in range(1, 10):
                try:
                    scenario += o[f'ScenarioText{i}']['v'] + '\n'
                except KeyError:
                    break
            res[c['id']]['scenario'] = {'text': scenario.strip(), 'crowdinContext': context}
            if o['ResponseAudio']['s']:
                res[c['id']]['response'] = {'text': o['ResponseAudio']['s'], 'crowdinContext': context}
        return res

    @staticmethod
    def _decode_scenario(obj, trans, path_folder: str):
        for c in obj['content']:
            cid = str(c['id'])
            t = trans[cid]
            c['decoys'] = ' | '.join([d.strip() for d in t['decoys']['text'].split('\n') if d.strip()])
            if 'category' in t:
                c['category'] = t['category']['text']
            if c['answerText']:
                c['answerText'] = t['answer']['text']
            c['questionText'] = t['questionText']['text']
            scenario = [d.strip() for d in t['scenario']['text'].split('\n') if d.strip()]
            c['scenarioText'] = ' '.join(scenario)
            o = read_from_folder(cid, path_folder)
            o['Decoys']['v'] = c['decoys']
            o['QuestionText']['v'] = c['questionText']
            if 'Answer' in o:
                o['Answer']['v'] = c['answerText']
            n = len(scenario)
            assert f'ScenarioText{n}' in o and f'ScenarioText{n + 1}' not in o, f'Prompt {cid} should have {n} lines'
            for i in range(n):
                o[f'ScenarioText{i+1}']['v'] = scenario[i]
            write_to_folder(cid, path_folder, o)
        return obj

    @decode_mapping(PATH + r'\content\SplitTheRoomShortie.jet', folder + 'scenarios.json')
    def encode_scenarios_shortie(self, obj: dict):
        return self._encode_scenario(obj, PATH + r'\content\SplitTheRoomShortie')

    @decode_mapping(PATH + r'\content\SplitTheRoomLater.jet', folder + 'scenarios_later.json')
    def encode_scenarios_later(self, obj: dict):
        return self._encode_scenario(obj, PATH + r'\content\SplitTheRoomLater')

    @decode_mapping(PATH + r'\content\SplitTheRoomFinal.jet', folder + 'scenarios_final.json')
    def encode_scenarios_final(self, obj: dict):
        return self._encode_scenario(obj, PATH + r'\content\SplitTheRoomFinal')

    @decode_mapping(PATH + r'\content\SplitTheRoomShortie.jet', build + 'scenarios.json', PATH + r'\content\SplitTheRoomShortie.jet')
    def decode_scenarios_shortie(self, obj, trans):
        return self._decode_scenario(obj, trans, PATH + r'\content\SplitTheRoomShortie')

    @decode_mapping(PATH + r'\content\SplitTheRoomLater.jet', build + 'scenarios_later.json', PATH + r'\content\SplitTheRoomLater.jet')
    def decode_scenarios_later(self, obj, trans):
        return self._decode_scenario(obj, trans, PATH + r'\content\SplitTheRoomLater')

    @decode_mapping(PATH + r'\content\SplitTheRoomFinal.jet', build + 'scenarios_final.json', PATH + r'\content\SplitTheRoomFinal.jet')
    def decode_scenarios_final(self, obj, trans):
        return self._decode_scenario(obj, trans, PATH + r'\content\SplitTheRoomFinal')
