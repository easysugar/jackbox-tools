import os
import re

from lib.game import Game, clean_text
from lib.utils import count_strings_and_words
from paths import JPP5_PATH


class PatentlyStupid(Game):
    name = 'PatentlyStupid'
    game = os.path.join(JPP5_PATH + rf'\games\{name}')
    folder = '../data/pp5/patents/'
    build = '../build/uk/JPP5/PatentlyStupid/'

    def count_words_to_translate(self):
        audios = [
            clean_text(re.sub('toby:|lena:', '', v['text'], flags=re.IGNORECASE))
            for m in self.read_from_data(f'{self.name}.json')['media']
            for v in m['versions']
            if m['type'] == 'A'
        ]
        prompts = []
        for c in self.read_jet('PatentlyStupidGeneDrawing')['content']:
            o = self.read_content(c['id'], 'PatentlyStupidGeneDrawing')
            prompts.append(o['Tagline']['v'])
        strings, words = count_strings_and_words([
            self._read_json(os.path.join(self.game, 'Localization.json'))['table']['en'],
            audios,
            self.read_jet('PatentlyStupidShortie'),
            self.read_jet('PatentlyStupidGeneDrawing'),
            prompts,
        ])
        print(f'Total strings: {strings}\nTotal words: {words}')

    def decode_localization(self):
        trans = self.read_from_build('Localization.json')['table']['en']
        for i, joke in enumerate(trans['CARD_JOKES']):
            trans['CARD_JOKES'][i] = joke.replace('\n', ' | ')
            if len(joke.split('\n')) == 2:
                joke = joke + '\n'
            if len(joke.split('\n')) == 4:
                joke = joke.strip()
            assert len(joke.split('\n')) == 3, f'Joke should include 3 parts: {joke}'
        self.write_localization(trans)

    def encode_drawing(self):
        obj = self.read_jet('GeneDrawing')
        res = {}
        for c in obj['content']:
            cid = c['id']
            o = self.read_content(cid, 'GeneDrawing')
            cxt = self.get_context(c, c['Title'])
            res[cid] = {
                'title': {'text': c['Title'], 'crowdinContext': cxt},
                'tagline': {'text': o['Tagline']['v'], 'crowdinContext': cxt},
            }
        self.write_to_data('gene_drawing.json', res)

    def decode_drawing(self):
        trans = self.read_from_build('gene_drawing.json')
        obj = self.read_jet('GeneDrawing')
        for c in obj['content']:
            cid = str(c['id'])
            c['Title'] = trans[cid]['title']['text']
            o = self.read_content(c['id'], 'GeneDrawing')
            o['Tagline']['v'] = trans[cid]['tagline']['text']
            self.write_content(c['id'], 'GeneDrawing', o)
        self.write_jet('GeneDrawing', obj)

    def encode_shortie(self):
        obj = self.read_jet('Shortie')
        res = {}
        for c in obj['content']:
            cid = c['id']
            cxt = self.get_context(c, c['prompt'])
            res[cid] = {
                'prompt': {'text': c['prompt'], 'crowdinContext': cxt},
                'decoys': [
                    {'text': clean_text(decoy), 'crowdinContext': cxt}
                    for decoy in c['decoys'].split('|')
                ],
            }
        self.write_to_data('shortie.json', res)

    def decode_shortie(self):
        trans = self.read_from_build('shortie.json')
        obj = self.read_jet('Shortie')
        for c in obj['content']:
            cid = str(c['id'])
            c['prompt'] = trans[cid]['prompt']['text']
            c['decoys'] = '|'.join([_['text'] for _ in trans[cid]['decoys']])
        self.write_jet('Shortie', obj)
