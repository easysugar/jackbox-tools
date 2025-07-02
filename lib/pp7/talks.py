import os

from lib.game import Game, decode_mapping, clean_text, update_localization
from paths import JPP7_PATH


class Talks(Game):
    name = 'JackboxTalks'
    game = os.path.join(JPP7_PATH, 'games', 'JackboxTalks')
    folder = '../data/pp7/talks/'
    build = '../build/uk/JPP7/Talking Points/'

    def decode_localization(self):
        update_localization(os.path.join(self.game, 'Localization.json'), os.path.join(self.build, 'Localization.json'))

    def encode_picture(self):
        obj = self.read_jet('Picture')
        res = {}
        for c in obj['content']:
            res[c['id']] = {
                'name': c['name'],
                'crowdinContext': self.get_context(c),
            }
        self.write_to_data('picture.json', res)

    def encode_signpost(self):
        obj = self.read_jet('Signpost')
        res = {}
        for c in obj['content']:
            res[c['id']] = {
                'signpost': c['signpost'],
                'crowdinContext': c['position'] + self.get_context(c),
            }
        self.write_to_data('signpost.json', res)

    def decode_signpost(self):
        trans = self.read_from_build('signpost.json')
        obj = self.read_jet('Signpost')
        for c in obj['content']:
            c['signpost'] = trans[c['id']]['signpost']
        self.write_jet('Signpost', obj)

    def encode_title(self):
        obj = self.read_jet('Title')
        res = {}
        for c in obj['content']:
            context = c['title'] + self.get_context(c)
            res[c['id']] = {
                'title': {'text': c['title'], 'crowdinContext': context},
                'signpost': [{'text': s['signpost'], 'crowdinContext': f'({s["position"]}) ' + context} for s in c['signposts']],
                'safety_answers': [{'text': s, 'crowdinContext': context} for s in c['safetyAnswers']],
            }
        self.write_to_data('title.json', res)

    def decode_title(self):
        trans = self.read_from_build('title.json')
        obj = self.read_jet('Title')
        for c in obj['content']:
            c['title'] = trans[c['id']]['title']['text']
            c['safetyAnswers'] = [s['text'] for s in trans[c['id']]['safety_answers']]
            for i in range(len(c['signposts'])):
                c['signposts'][i]['signpost'] = trans[c['id']]['signpost'][i]['text']
        self.write_jet('Title', obj)

    def decode_media(self):
        text = self.read_from_build('audio_subtitles.json')
        text = {k: v['text'] for k, v in text.items()}
        self._decode_swf_media(path_media=self.folder + 'dict.txt', path_expanded=self.folder + 'expanded.json',
                               trans=text, path_save=self.folder + 'translated_dict.txt')

    @decode_mapping(folder + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {
            v['id']: {"text": clean_text(v['text']), "crowdinContext": c.get('context', '')}
            for c in obj
            for v in c['versions']
            if c['type'] == 'A'
        }
