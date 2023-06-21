from lib.game import Game, decode_mapping
from settings.internet import *


class Internet(Game):
    folder = '../data/pp4/internet/encoded/'
    folder_swf = '../data/pp4/internet/swf/'

    @decode_mapping(PATH_TWIST, folder + 'twist.json')
    def encode_twist(self, obj):
        return {c['id']: c['text'] for c in obj['content']}

    @decode_mapping(PATH_DESKTOP_FOLDER, folder + 'desktop_folder.json')
    def encode_desktop_folder(self, obj):
        return {c['id']: c['text'] for c in obj['content']}

    @decode_mapping(PATH_FINAL_ROUND, folder + 'final_round.json')
    def encode_final_round(self, obj):
        return {c['id']: {'twistPlaceholder': c['twistPlaceholder'], 'belowBlackBox': c['controllerTextSpec']['belowBlackBox']}
                for c in obj['content']}

    @decode_mapping(PATH_THEME, folder + 'theme.json')
    def encode_theme(self, obj):
        return {c['id']: {'twistPlaceholder': c['twistPlaceholder'], 'belowBlackBox': c['controllerTextSpec']['belowBlackBox']}
                for c in obj['content']}

    @decode_mapping(PATH_JOB_PROMPT, folder + 'job_prompt.json')
    def encode_job_prompt(self, obj):
        return {c['id']: {c['prompt']['text']: {'prompt': c['prompt']['text'], 'decoys': [i['text'] for i in c['decoys']]}}
                for c in obj['content']}

    @decode_mapping(PATH_PHOTO_PROMPT, folder + 'photo_prompt.json')
    def encode_photo_prompt(self, obj):
        return {c['id']: {c['prompt']['text']: {'prompt': c['prompt']['text'], 'choices': {i['id']: i['text'] for i in c['choices']}}}
                for c in obj['content']}

    @decode_mapping(PATH_STORE_PROMPT, folder + 'store_prompt.json')
    def encode_store_prompt(self, obj):
        return {c['id']: {c['prompt']['text']: {'prompt': c['prompt']['text'], 'decoys': [i['text'] for i in c['decoys']]}}
                for c in obj['content']}

    @decode_mapping(PATH_PROMPT, folder + 'prompt.json')
    def encode_prompt(self, obj):
        return {c['id']: {c['prompt']['text']: {'prompt': c['prompt']['text'], 'decoys': [i['text'] for i in c['decoys']]}}
                for c in obj['content']}

    @decode_mapping(PATH_STICKY_NOTE, folder + 'sticky_note.json')
    def encode_sticky_note(self, obj):
        return {c['id']: c['text'] for c in obj['content']}

    @decode_mapping(PATH_WARNING, folder + 'warning.json')
    def encode_warning(self, obj):
        return {c['id']: c['text'] for c in obj['content']}

    @decode_mapping(PATH_MESSENGER, folder + 'messenger.json')
    def encode_messenger(self, obj):
        return {c['id']: c['windowTitle'] + '\n' + '\n'.join(i['from'] + ': ' + i['text'] for i in c['messages']) for c in obj['content']}

    @decode_mapping(PATH_ADDRESS_BAR, folder + 'address_bar.json')
    def encode_address_bar(self, obj):
        return {c['id']: '\n'.join([i['url'] for i in c['history']]) for c in obj['content']}

    @decode_mapping(PATH_NAME, folder + 'name.json')
    def encode_name(self, obj):
        return [c['text'] for c in obj['content']]

    @decode_mapping(PATH_THEME_INTRO, folder + 'theme_intro.json')
    def encode_theme_intro(self, obj):
        return {c['id']: {c['applicableThemes'][0]: c['twistText'] + '\n' + c['responseText']} for c in obj['content']}

    @decode_mapping(folder_swf + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {
            v['id']: {
                'name': v['text'].replace('[category=host]', '').strip(),
                'crowdinContext': (c.get('context') or v.get('context') or '') + ('' if not v['tags'] else ' [%s]' % v['tags'])
            }
            for c in obj for v in c['versions'] if c['type'] == 'A' and '[category=host]' in v['text']
        }
