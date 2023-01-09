from lib.game import Game, decode_mapping
from settings.internet import *


class Internet(Game):
    folder = '../data/pp4/internet/encoded/'

    @decode_mapping(PATH_TWIST, folder + 'twist.json')
    def encode_twist(self, obj):
        return {c['id']: c['text'] for c in obj['content']}

    @decode_mapping(PATH_DESKTOP_FOLDER, folder + 'desktop_folder.json')
    def encode_desktop_folder(self, obj):
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
