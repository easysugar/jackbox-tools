import pandas as pd
import tqdm

from lib.drive import Drive
from lib.game import Game, decode_mapping, remove_suffix
from paths import JPP4_PATH



class Bracketeering(Game):
    game = JPP4_PATH + r'\games\Bracketeering'
    folder = '../data/pp4/bracket/'
    build = '../build/uk/JPP4/Bracketeering/'
    drive = '1xTFolPKkGdeOEYRIJQ-QDMegpaS0_5wH'
    drive_prompts = '1aYcg7w_5SMvINVlhH0rbG67SWwbFDkZ5'
    audio_folder = r'X:\Jackbox\games\jpp4\bracket\audio\media2'
    audio_prompts_folder = r'X:\Jackbox\games\jpp4\bracket\audio\prompts2'
    audio_reactions_folder = r'X:\Jackbox\games\jpp4\bracket\audio\reactions2'

    @decode_mapping(game + r'\content\BRKPrompt.jet', folder + 'prompt.json')
    def encode_prompt(self, obj):
        res = {}
        for c in obj['content']:
            row = {}
            context = self.get_context(c, c['prompt']['text'])
            row['category'] = {'text': c['category'], 'crowdinContext': context}
            row['prompt'] = {'text': c['prompt']['text'], 'crowdinContext': context}
            row['twists'] = [{'text': t['text'], 'crowdinContext': context} for t in c['twists']]
            row['decoys'] = [{'text': t['text'], 'crowdinContext': context} for t in c['decoys']]
            o = self.read_content(c['id'], 'BRKPrompt')
            if o.get('PromptReactionAudio'):
                row['reaction'] = {'text': o['PromptReactionAudio']['s'], 'crowdinContext': context}
            if o.get('FinalReactionAudio'):
                row['final_reaction'] = {'text': o['FinalReactionAudio']['s'], 'crowdinContext': context}
            res[c['id']] = row
        return res

    @decode_mapping(game + r'\content\BRKPrompt.jet', folder + 'win_audio.json')
    def encode_win_audio(self, obj):
        res = {}
        for c in obj['content']:
            row = {}
            context = c['prompt']['text']
            for t in c['twists']:
                context += '\n-------------' + t['text']
            if c['x']:
                context += '\n-------------18+'
            o = self.read_content(c['id'], 'BRKPrompt')
            for i in range(5):
                key = f'Win{i}Audio'
                if o['Has' + key]['v'] == 'true':
                    row[key] = {'text': o[key]['s'], 'crowdinContext': context}
            res[c['id']] = row
        return res

    @decode_mapping(game + r'\content\BRKPrompt.jet', build + 'prompt.json', game + r'\content\BRKPrompt.jet')
    def decode_prompt(self, obj, trans):
        for c in obj['content']:
            t = trans[str(c['id'])]
            c['category'] = t['category']['text']
            c['prompt']['text'] = t['prompt']['text']
            for twist, t_twist in zip(c['twists'], t['twists']):
                twist['text'] = t_twist['text']
            for decoy, t_decoy in zip(c['decoys'], t['decoys']):
                decoy['text'] = t_decoy['text']
            o = self.read_content(c['id'], 'BRKPrompt')

            # Copy audio file for prompt
            self.copy_audio_to_content(c['id'], 'BRKPrompt', o['PromptAudio']['v'], self.audio_prompts_folder)

            # Copy audio files for twists
            for i in range(3):
                key = f'Twist{i}Audio'
                if key in o and o['Has' + key]['v'] == 'true':
                    self.copy_audio_to_content(c['id'], 'BRKPrompt', o[key]['v'], self.audio_prompts_folder)

            # Copy audio file for reaction
            if o['HasPromptReactionAudio']['v'] == 'true':
                self.copy_audio_to_content(c['id'], 'BRKPrompt', o['PromptReactionAudio']['v'], self.audio_prompts_folder)

            # Copy audio file for final reaction
            if 'FinalReactionAudio' in o and o['HasFinalReactionAudio']['v'] == 'true':
                prompt_to_copy = 'Twist0Audio' if 'Twist0Audio' in o else 'PromptAudio'
                self.copy_audio_to_content(c['id'], 'BRKPrompt', o['FinalReactionAudio']['v'], self.audio_prompts_folder,
                                           src_audio_id=o[prompt_to_copy]['v'])

            # Copy audio files for wins
            for i in range(5):
                key = f'Win{i}Audio'
                if o['Has' + key]['v'] == 'true':
                    self.copy_audio_to_content(c['id'], 'BRKPrompt', o[key]['v'], self.audio_reactions_folder)

        return obj

    @decode_mapping(folder + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T'}

    @decode_mapping(folder + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {v['id']: {"text": remove_suffix(v['text']), "crowdinContext": c.get('crowdinContext')}
                for c in obj for v in c['versions']
                if c['type'] == 'A' and 'category=host' in v['text']}

    def decode_media(self):
        text = self._read_json(self.build + 'text_subtitles.json')
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'expanded.json',
                               trans=text, path_save=self.folder + 'translated_dict.txt')

    def decode_localization(self):
        self.update_localization(self.game + r'\Localization.json', self.build + 'localization.json')

    @decode_mapping(folder + 'audio_subtitles.json', build + 'audio_subtitles.json', out=False)
    def upload_audio(self, original, obj):
        d = Drive(self.drive)
        data = []
        for cid in tqdm.tqdm(obj):
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg,
                         'context': obj[cid]['crowdinContext'],
                         'original': original[cid]['text'].strip().replace('\n', ' '),
                         'text': obj[cid]['text'].strip().replace('\n', ' ')})
            d.upload(self.game + r'\TalkshowExport\project\media', ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio.tsv', sep='\t', encoding='utf8', index=False)

    @decode_mapping(build + 'prompt.json', build + 'win_audio.json', out=False)
    def upload_audio_prompts(self, obj, wins):
        d = Drive(self.drive_prompts)
        prompts = []
        reactions = []
        win = []
        for cid, c in tqdm.tqdm(obj.items()):
            o = self.read_content(cid, 'BRKPrompt')
            audio_path = self.game + rf'\content\BRKPrompt\{cid}'
            ogg = o['PromptAudio']['v'] + '.ogg'
            prompts.append({'id': cid, 'ogg': ogg, 'text': c['prompt']['text'], 'original': o['PromptAudio']['s'], 'type': 'prompt'})
            d.upload(audio_path, ogg)
            for i, twist in enumerate(c.get('twists', [])):
                ogg = o[f'Twist{i}Audio']['v'] + '.ogg'
                prompts.append({'id': cid, 'ogg': ogg, 'text': twist['text'], 'original': o[f'Twist{i}Audio']['s'], 'type': 'twist'})
                d.upload(audio_path, ogg)
            if c['reaction'] and c['reaction']['text'] and o['PromptReactionAudio'].get('v'):
                ogg = o['PromptReactionAudio']['v'] + '.ogg'
                reactions.append({'id': cid, 'ogg': ogg, 'text': c['reaction']['text'], 'original': o['PromptReactionAudio']['s'],
                                  'context': prompts[-1]['text']})
                d.upload(audio_path, ogg)
            for i in range(5):
                key = f'Win{i}Audio'
                if o['Has' + key]['v'] == 'true':
                    ogg = o[key]['v'] + '.ogg'
                    win.append({'id': cid, 'ogg': ogg, 'text': wins[str(cid)][key]['text'], 'original': o[key]['s'],
                                'context': prompts[0]['text']})
                    d.upload(audio_path, ogg)

        for data in (prompts, reactions, win):
            for i in data:
                i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(prompts).to_csv(self.folder + 'audio_prompts.tsv', sep='\t', encoding='utf8', index=False)
        pd.DataFrame(reactions).to_csv(self.folder + 'audio_reactions.tsv', sep='\t', encoding='utf8', index=False)
        pd.DataFrame(win).to_csv(self.folder + 'audio_win.tsv', sep='\t', encoding='utf8', index=False)
