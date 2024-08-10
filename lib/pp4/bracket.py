from lib.game import Game, decode_mapping, read_from_folder, remove_suffix

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 4\games\Bracketeering'


class Bracketeering(Game):
    folder = '../data/pp4/bracket/'
    build = '../build/uk/JPP4/Bracketeering/'

    @decode_mapping(PATH_GAME + r'\content\BRKPrompt.jet', folder + 'prompt.json')
    def encode_prompt(self, obj):
        res = {}
        for c in obj['content']:
            row = {}
            context = c['prompt']['text']
            if c['x']:
                context += '\n-------------18+'
            row['category'] = {'text': c['category'], 'crowdinContext': context}
            row['prompt'] = {'text': c['prompt']['text'], 'crowdinContext': context}
            row['twists'] = [{'text': t['text'], 'crowdinContext': context} for t in c['twists']]
            row['decoys'] = [{'text': t['text'], 'crowdinContext': context} for t in c['decoys']]
            o = read_from_folder(str(c['id']), PATH_GAME + r'\content\BRKPrompt')
            if o.get('PromptReactionAudio'):
                row['reaction'] = {'text': o['PromptReactionAudio']['s'], 'crowdinContext': context}
            if o.get('FinalReactionAudio'):
                row['final_reaction'] = {'text': o['FinalReactionAudio']['s'], 'crowdinContext': context}
            res[c['id']] = row
        return res

    @decode_mapping(PATH_GAME + r'\content\BRKPrompt.jet', build + 'prompt.json', PATH_GAME + r'\content\BRKPrompt.jet')
    def decode_prompt(self, obj, trans):
        for c in obj['content']:
            t = trans[str(c['id'])]
            c['category'] = t['category']['text']
            c['prompt']['text'] = t['prompt']['text']
            for twist, t_twist in zip(c['twists'], t['twists']):
                twist['text'] = t_twist['text']
            for decoy, t_decoy in zip(c['decoys'], t['decoys']):
                decoy['text'] = t_decoy['text']
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
        self.update_localization(PATH_GAME + r'\Localization.json', self.build + 'localization.json')
