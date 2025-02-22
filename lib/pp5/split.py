import csv
import os

import pandas as pd
import tqdm

from lib.audio import get_audio_markers
from lib.common import copy_file
from lib.drive import Drive
from lib.game import Game, decode_mapping, read_from_folder, write_to_folder
from paths import JPP5_PATH

PATH = JPP5_PATH + r'\games\SplitTheRoom'
PATH_MEDIA = PATH + r'\TalkshowExport\project\media'


class SplitTheRoom(Game):
    game = PATH
    drive = '1-7isayk367umf7bz3tYF913DXrowy6o_'
    folder = '../data/pp5/split/'
    build = '../build/uk/JPP5/SplitTheRoom/'
    audio = r'X:\Jackbox\games\jpp5\split\audio\scenarios'
    rounds = {1: 'SplitTheRoomShortie', 2: 'SplitTheRoomLater', 3: 'SplitTheRoomFinal'}

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

    def _decode_scenario(self, obj, trans, path_folder: str):
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
            audio_file = os.path.join(self.audio, o['ScenarioAudio']['v'] + '.ogg')
            if os.path.isfile(audio_file):
                self._set_scenario_audio_cue(o, audio_file)
                copy_file(audio_file, os.path.join(path_folder, cid, o['ScenarioAudio']['v'] + '.ogg'))
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

    @decode_mapping(folder + 'audio_subtitles.json', build + 'audio_subtitles.json', out=False)
    def upload_audio(self, original, obj):
        d = Drive(self.drive)
        data = []
        for cid in tqdm.tqdm(obj):
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg, 'text': obj[cid]['text'].strip().replace('\n', ' '),
                         'context': obj[cid]['crowdinContext'],
                         'original': original[cid]['text'].strip().replace('\n', ' ')})
            d.upload(PATH_MEDIA, ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio.tsv', sep='\t', encoding='utf8', index=False)

    @decode_mapping(build + 'scenarios.json', build + 'scenarios_later.json', out=False)
    def upload_audio_categories(self, round1, round2):
        d = Drive(self.drive)
        data = []
        for cid in tqdm.tqdm(round1):
            o = read_from_folder(cid, PATH + r'\content\SplitTheRoomShortie')
            ogg = f"{o['CategoryAudio']['v']}.ogg"
            data.append({'id': cid, 'ogg': ogg, 'text': round1[cid]['category']['text'], 'original': o['CategoryAudio']['s']})
            d.upload(PATH + rf'\content\SplitTheRoomShortie\{cid}', ogg)
        for cid in tqdm.tqdm(round2):
            o = read_from_folder(cid, PATH + r'\content\SplitTheRoomLater')
            ogg = f"{o['CategoryAudio']['v']}.ogg"
            data.append({'id': cid, 'ogg': ogg, 'text': round2[cid]['category']['text'], 'original': o['CategoryAudio']['s']})
            d.upload(PATH + rf'\content\SplitTheRoomLater\{cid}', ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio_categories.tsv', sep='\t', encoding='utf8', index=False)

    @decode_mapping(build + 'scenarios.json', build + 'scenarios_later.json', out=False)
    def upload_audio_categories(self, round1, round2):
        d = Drive(self.drive)
        data = []
        for cid in tqdm.tqdm(round1):
            o = read_from_folder(cid, PATH + r'\content\SplitTheRoomShortie')
            ogg = f"{o['CategoryAudio']['v']}.ogg"
            data.append({'id': cid, 'ogg': ogg, 'text': round1[cid]['category']['text'], 'original': o['CategoryAudio']['s']})
            d.upload(PATH + rf'\content\SplitTheRoomShortie\{cid}', ogg)
        for cid in tqdm.tqdm(round2):
            o = read_from_folder(cid, PATH + r'\content\SplitTheRoomLater')
            ogg = f"{o['CategoryAudio']['v']}.ogg"
            data.append({'id': cid, 'ogg': ogg, 'text': round2[cid]['category']['text'], 'original': o['CategoryAudio']['s']})
            d.upload(PATH + rf'\content\SplitTheRoomLater\{cid}', ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio_categories.tsv', sep='\t', encoding='utf8', index=False)

    @decode_mapping(build + 'scenarios.json', build + 'scenarios_later.json', build + 'scenarios_final.json', out=False)
    def upload_audio_scenarios(self, round1, round2, final):
        d = Drive(self.drive)
        data = []
        for round_num, round_name in self.rounds.items():
            scenarios = {1: round1, 2: round2, 3: final}[round_num]
            for cid in tqdm.tqdm(scenarios):
                o = read_from_folder(cid, PATH + rf'\content\{round_name}')
                ogg = f"{o['ScenarioAudio']['v']}.ogg"
                text = scenarios[cid]['scenario']['text'] + '\n' + scenarios[cid]['questionText']['text']
                data.append({'id': cid, 'ogg': ogg, 'original': o['ScenarioAudio']['s'], 'text': text})
                d.upload(PATH + rf'\content\{round_name}\{cid}', ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio_scenarios.tsv', sep='\t', encoding='utf8', index=False, quoting=csv.QUOTE_ALL)

    @decode_mapping(build + 'scenarios_final.json', out=False)
    def upload_audio_responses(self, final):
        d = Drive(self.drive)
        data = []
        for cid in tqdm.tqdm(final):
            o = read_from_folder(cid, PATH + rf'\content\SplitTheRoomFinal')
            if o['HasResponseAudio']['v'] != 'true':
                continue
            ogg = f"{o['ResponseAudio']['v']}.ogg"
            text = final[cid]['response']['text']
            data.append({'id': cid, 'ogg': ogg, 'original': o['ResponseAudio']['s'], 'text': text})
            d.upload(PATH + rf'\content\SplitTheRoomFinal\{cid}', ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio_responses.tsv', sep='\t', encoding='utf8')

    @decode_mapping(build + 'scenarios.json', build + 'scenarios_later.json', out=False)
    def _copy_audio_to_scenarios(self, round1, round2):
        for cid in tqdm.tqdm(round1):
            o = read_from_folder(cid, PATH + r'\content\SplitTheRoomShortie')
            ogg = f"{o['CategoryAudio']['v']}.ogg"
            copy_file(os.path.join(self.audio, ogg), os.path.join(PATH, 'content', 'SplitTheRoomShortie', str(cid), ogg))
        for cid in tqdm.tqdm(round2):
            o = read_from_folder(cid, PATH + r'\content\SplitTheRoomLater')
            ogg = f"{o['CategoryAudio']['v']}.ogg"
            copy_file(os.path.join(self.audio, ogg), os.path.join(PATH, 'content', 'SplitTheRoomLater', str(cid), ogg))

    @staticmethod
    def _set_scenario_audio_cue(obj: dict, audio_path: str):
        markers = get_audio_markers(audio_path)
        n = len([k for k in obj if k.startswith('$ScenarioAudio$ScenarioTextCue')])
        assert len(markers) == n, f'Audio {audio_path} should have {n} markers, but has only {len(markers)}'
        for i in range(2, 10):
            key = f'$ScenarioAudio$ScenarioTextCue{i}'
            if key not in obj:
                break
            obj[key]['v'] = markers.pop(0)
        obj['$ScenarioAudio$QuestionTextCue']['v'] = markers.pop(0)
