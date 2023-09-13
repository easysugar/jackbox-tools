from lib.game import Game, decode_mapping, read_from_folder

PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 4\games\Bracketeering'


class Bracketeering(Game):
    folder = '../data/pp4/bracket/'

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

    @decode_mapping(folder + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'T'}

    @decode_mapping(folder + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: v['text'] for c in obj for v in c['versions'] if c['type'] == 'A'}
