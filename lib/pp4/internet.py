import pandas as pd
import tqdm

from lib.drive import Drive
from lib.game import Game, decode_mapping
from paths import JPP4_PATH

PATH = JPP4_PATH + r'\games\SurviveTheInternet'
PATH_LOCALIZATION = PATH + r'\Localization.json'
PATH_TWIST = PATH + r'\content\STITwist.jet'
PATH_DESKTOP_FOLDER = PATH + r'\content\STIDesktopFolderName.jet'
PATH_WARNING = PATH + r'\content\STIWarningGag.jet'
PATH_MESSENGER = PATH + r'\content\STIMessengerGag.jet'
PATH_ADDRESS_BAR = PATH + r'\content\STIAddressBarGag.jet'
PATH_NAME = PATH + r'\content\STIName.jet'
PATH_THEME = PATH + r'\content\STITheme.jet'
PATH_THEME_INTRO = PATH + r'\content\STIThemeIntro.jet'
PATH_FINAL_ROUND = PATH + r'\content\STIFinalRoundTheme.jet'
PATH_JOB_PROMPT = PATH + r'\content\STIJobPrompt.jet'
PATH_PHOTO_PROMPT = PATH + r'\content\STIPhotoPrompt.jet'
PATH_STORE_PROMPT = PATH + r'\content\STIStorePrompt.jet'
PATH_PROMPT = PATH + r'\content\STIPrompt.jet'
PATH_STICKY_NOTE = PATH + r'\content\STIStickyNoteGag.jet'
PATH_MEDIA = PATH + r'\TalkshowExport\project\media'

# encoded
PATH_EXPANDED = r'data/pp3/fakin/swf/FakinIt_Expanded.json'
PATH_AUDIO_SUBTITLES = r'data/pp3/fakin/swf/audio_subtitles.json'
PATH_TASKS_ENCODED = r'data/pp3/fakin/encoded/tasks.json'
PATH_CATEGORIES_ENCODED = r'data/pp3/fakin/encoded/categories.json'
PATH_INPUT_ENCODED = r'data/pp3/fakin/encoded/input.json'
PATH_LEADERBOARDS_ENCODED = r'data/pp3/fakin/encoded/leaderboards.json'
PATH_SETTINGS_ENCODED = r'data/pp3/fakin/encoded/settings.json'



def _replace_text(obj, trans):
    for c in obj['content']:
        c['text'] = trans[str(c['id'])]
    return obj


class Internet(Game):
    folder = '../data/pp4/internet/encoded/'
    folder_swf = '../data/pp4/internet/swf/'
    build = '../build/uk/JPP4/STI/'
    drive = '18N-GPGwsbm80DJRMMa7QufsIXBOj_nDs'

    @decode_mapping(PATH_TWIST, folder + 'twist.json')
    def encode_twist(self, obj):
        return {c['id']: c['text'] for c in obj['content']}

    @decode_mapping(PATH_TWIST, build + 'twist.json', PATH_TWIST)
    def decode_twist(self, obj, trans):
        return _replace_text(obj, trans)

    @decode_mapping(PATH_DESKTOP_FOLDER, folder + 'desktop_folder.json')
    def encode_desktop_folder(self, obj):
        return {c['id']: c['text'] for c in obj['content']}

    @decode_mapping(PATH_DESKTOP_FOLDER, build + 'desktop_folder.json', PATH_DESKTOP_FOLDER)
    def decode_desktop_folder(self, obj, trans):
        return _replace_text(obj, trans)

    @decode_mapping(PATH_FINAL_ROUND, folder + 'final_round.json')
    def encode_final_round(self, obj):
        return {c['id']: {'twistPlaceholder': c['twistPlaceholder'], 'belowBlackBox': c['controllerTextSpec']['belowBlackBox']}
                for c in obj['content']}

    @decode_mapping(PATH_FINAL_ROUND, build + 'final_round.json', PATH_FINAL_ROUND)
    def decode_final_round(self, obj, trans):
        for c in obj['content']:
            c['twistPlaceholder'] = trans[str(c['id'])]['twistPlaceholder']
            c['controllerTextSpec']['belowBlackBox'] = trans[str(c['id'])]['belowBlackBox']
        return obj

    @decode_mapping(PATH_THEME, folder + 'theme.json')
    def encode_theme(self, obj):
        return {c['id']: {'twistPlaceholder': c['twistPlaceholder'], 'belowBlackBox': c['controllerTextSpec']['belowBlackBox']}
                for c in obj['content']}

    @decode_mapping(PATH_THEME, build + 'theme.json', PATH_THEME)
    def decode_theme(self, obj, trans):
        for c in obj['content']:
            c['twistPlaceholder'] = trans[str(c['id'])]['twistPlaceholder']
            c['controllerTextSpec']['belowBlackBox'] = trans[str(c['id'])]['belowBlackBox']
        return obj

    @decode_mapping(PATH_JOB_PROMPT, folder + 'job_prompt.json')
    def encode_job_prompt(self, obj):
        return {c['id']: {c['prompt']['text']: {'prompt': c['prompt']['text'], 'decoys': [i['text'] for i in c['decoys']]}}
                for c in obj['content']}

    @decode_mapping(PATH_JOB_PROMPT, build + 'job_prompt.json', PATH_JOB_PROMPT)
    def decode_job_prompt(self, obj, trans):
        for c in obj['content']:
            t = list(trans[str(c['id'])].values())[0]
            c['prompt']['text'] = t['prompt']
            for decoy, t_decoy in zip(c['decoys'], t['decoys']):
                decoy['text'] = t_decoy
        return obj

    @decode_mapping(PATH_PHOTO_PROMPT, folder + 'photo_prompt.json')
    def encode_photo_prompt(self, obj):
        return {c['id']: {c['prompt']['text']: {'prompt': c['prompt']['text'], 'choices': {i['id']: i['text'] for i in c['choices']}}}
                for c in obj['content']}

    @decode_mapping(PATH_PHOTO_PROMPT, build + 'photo_prompt.json', PATH_PHOTO_PROMPT)
    def _decode_photo_prompt(self, obj, trans):
        for c in obj['content']:
            t = list(trans[str(c['id'])].values())[0]
            c['prompt']['text'] = t['prompt']
            for choice in c['choices']:
                choice['text'] = t['choices'][choice['id']]
                if choice['id'] == 'Football':
                    choice['id'] = 'Soccer'
                if choice['id'] == 'Baseball':
                    choice['id'] = 'Basketball'
        return obj

    @decode_mapping(PATH_STORE_PROMPT, folder + 'store_prompt.json')
    def encode_store_prompt(self, obj):
        return {c['id']: {c['prompt']['text']: {'prompt': c['prompt']['text'], 'decoys': [i['text'] for i in c['decoys']]}}
                for c in obj['content']}

    @decode_mapping(PATH_STORE_PROMPT, build + 'store_prompt.json', PATH_STORE_PROMPT)
    def decode_store_prompt(self, obj, trans):
        for c in obj['content']:
            t = list(trans[str(c['id'])].values())[0]
            c['prompt']['text'] = t['prompt']
            for decoy, t_decoy in zip(c['decoys'], t['decoys']):
                decoy['text'] = t_decoy
        return obj

    @decode_mapping(PATH_PROMPT, folder + 'prompt.json')
    def encode_prompt(self, obj):
        return {c['id']: {c['prompt']['text']: {'prompt': c['prompt']['text'], 'decoys': [i['text'] for i in c['decoys']]}}
                for c in obj['content']}

    @decode_mapping(PATH_PROMPT, build + 'prompt.json', PATH_PROMPT)
    def decode_prompt(self, obj, trans):
        for c in obj['content']:
            t = list(trans[str(c['id'])].values())[0]
            c['prompt']['text'] = t['prompt']
            for decoy, t_decoy in zip(c['decoys'], t['decoys']):
                decoy['text'] = t_decoy
        return obj

    @decode_mapping(PATH_STICKY_NOTE, folder + 'sticky_note.json')
    def encode_sticky_note(self, obj):
        return {c['id']: c['text'] for c in obj['content']}

    @decode_mapping(PATH_STICKY_NOTE, build + 'sticky_note.json', PATH_STICKY_NOTE)
    def decode_sticky_note(self, obj, trans):
        return _replace_text(obj, trans)

    @decode_mapping(PATH_WARNING, folder + 'warning.json')
    def encode_warning(self, obj):
        return {c['id']: c['text'] for c in obj['content']}

    @decode_mapping(PATH_WARNING, build + 'warning.json', PATH_WARNING)
    def decode_warning(self, obj, trans):
        return _replace_text(obj, trans)

    @decode_mapping(PATH_MESSENGER, folder + 'messenger.json')
    def encode_messenger(self, obj):
        return {c['id']: c['windowTitle'] + '\n' + '\n'.join(i['from'] + ': ' + i['text'] for i in c['messages']) for c in obj['content']}

    @decode_mapping(PATH_MESSENGER, build + 'messenger.json', PATH_MESSENGER)
    def decode_messenger(self, obj, trans):
        for c in obj['content']:
            title, *messages = trans[str(c['id'])].strip().split('\n')
            for msg, t_msg in zip(c['messages'], messages):
                msg['from'], msg['text'] = t_msg.split(': ')
            c['windowTitle'] = title
        return obj

    @decode_mapping(PATH_ADDRESS_BAR, folder + 'address_bar.json')
    def encode_address_bar(self, obj):
        return {c['id']: '\n'.join([i['url'] for i in c['history']]) for c in obj['content']}

    @decode_mapping(PATH_ADDRESS_BAR, build + 'address_bar.json', PATH_ADDRESS_BAR)
    def decode_address_bar(self, obj, trans):
        for c in obj['content']:
            for row, t_row in zip(c['history'], trans[str(c['id'])].split('\n')):
                row['url'] = t_row
        return obj

    @decode_mapping(PATH_NAME, folder + 'name.json')
    def encode_name(self, obj):
        return [c['text'] for c in obj['content']]

    @decode_mapping(PATH_NAME, build + 'name.json', PATH_NAME)
    def decode_name(self, obj, trans):
        for c, t in zip(obj['content'], trans):
            c['text'] = t
        return obj

    @decode_mapping(PATH_THEME_INTRO, folder + 'theme_intro.json')
    def encode_theme_intro(self, obj):
        return {c['id']: {c['applicableThemes'][0]: c['twistText'] + '\n' + c['responseText']} for c in obj['content']}

    @decode_mapping(PATH_THEME_INTRO, build + 'theme_intro.json', PATH_THEME_INTRO)
    def decode_theme_intro(self, obj, trans):
        for c, t in zip(obj['content'], trans):
            arr = list(trans[str(c['id'])].values())[0].strip().split('\n')
            if len(arr) == 1:
                arr.append('')
            c['twistText'], c['responseText'] = arr
        return obj

    @decode_mapping(folder_swf + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {
            v['id']: {
                'name': v['text'].replace('[category=host]', '').strip(),
                'crowdinContext': (c.get('context') or v.get('context') or '') + ('' if not v['tags'] else ' [%s]' % v['tags'])
            }
            for c in obj for v in c['versions'] if c['type'] == 'A' and '[category=host]' in v['text']
        }

    def decode_localization(self):
        self.update_localization(PATH_LOCALIZATION, self.build + 'localization.json')

    def upload_audio(self):
        d = Drive(self.drive)
        data = []
        original = self._read_json(self.folder + 'audio_subtitles.json')
        obj = self._read_json(self.build + 'audio_subtitles.json')
        for cid in tqdm.tqdm(obj):
            ogg = f'{cid}.ogg'
            data.append({'id': cid, 'ogg': ogg, 'text': obj[cid]['name'].strip().replace('\n', ' '),
                         'context': obj[cid]['crowdinContext'],
                         'original': original[cid]['name'].strip().replace('\n', ' ')})
            d.upload(PATH_MEDIA, ogg)
        for i in data:
            i['link'] = d.get_link(i['ogg'])
        pd.DataFrame(data).to_csv(self.folder + 'audio.tsv', sep='\t', encoding='utf8', index=False)
