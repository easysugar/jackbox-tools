import os
import re

from lib.game import Game, clean_text, update_localization
from lib.utils import count_strings_and_words
from paths import JPP8_PATH


class WeaponsDrawn(Game):
    name = 'MurderDetectives'
    pack = JPP8_PATH
    international = True
    folder = './data/pp8/murders/'
    build = './build/uk/JPP8/Weapons Drawn/'
    font = r'''!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ¡¢£¥¨©«®°±´¶·»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿŒœŸˆ˜πЄІЇАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгдежзийклмнопрстуфхцчшщьюяєіїҐґ–—‘’“”„†•…‹›€™√∞∩≈'''

    def count_words_to_translate(self):
        audios = [
            clean_text(re.sub(r'(LORD\s*TIPPET|NARRATOR):', '', v['text'], flags=re.IGNORECASE))
            for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]

        strings, words = count_strings_and_words([
            self.read_localization(),
            [c['name'] for c in self.read_jet('Guest')['content']],
            [c['weapon'] for c in self.read_jet('Weapon')['content']],
            audios,
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')

    def encode_guest(self):
        obj = self.read_jet('Guest')
        res = {
            cid: {'crowdinContext': self.get_context(c), 'name': c['name']}
            for cid, c in enumerate(obj['content'])
        }
        self.write_to_data('guest.json', res)

    def decode_guest(self):
        trans = self.read_from_build('guest.json')
        obj = self.read_jet('Guest')
        for i, c in enumerate(obj['content']):
            c['name'] = trans[str(i)]['name']
        self.write_jet('Guest', obj)

    def encode_weapon(self):
        obj = self.read_jet('Weapon')
        res = {
            cid: {'crowdinContext': self.get_context(c), 'weapon': c['weapon']}
            for cid, c in enumerate(obj['content'])
        }
        self.write_to_data('weapon.json', res)

    def decode_weapon(self):
        trans = self.read_from_build('weapon.json')
        obj = self.read_jet('Weapon')
        for i, c in enumerate(obj['content']):
            c['weapon'] = trans[str(i)]['weapon']
        self.write_jet('Weapon', obj)

    def encode_audio_subtitles(self):
        obj = self.read_from_data(f'{self.name}.json')
        audio = {}
        for c in obj['media']:
            if c['type'] == 'A':
                for v in c['versions']:
                    if ':' not in v['text']:
                        host = 'LORD TIPPET'
                    else:
                        host, v['text'] = v['text'].split(':', 1)
                    audio[v['id']] = {
                        'text': clean_text(v['text']),
                        'crowdinContext': host.strip() + '\n' + c.get('crowdinContext', ''),
                    }
        self.write_to_data('audio.json', audio)

    def decode_localization(self):
        update_localization(os.path.join(self.game_path, 'Localization.json'), os.path.join(self.build, 'Localization.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationManager.json'), os.path.join('../build/uk/JPP8/', 'LocalizationManager.json'))
        update_localization(os.path.join(self.game_path, 'LocalizationPause.json'), os.path.join('../build/uk/JPP8/', 'LocalizationPause.json'))

    def decode_media(self):
        text = self.read_from_build('audio.json')
        text = {k: v['text'] for k, v in text.items()}
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'MurderDetectives.json',
                               trans=text, path_save=self.folder + 'translated_dict.txt')
