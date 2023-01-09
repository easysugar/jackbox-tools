from lib.game import Game, decode_mapping
from settings.monster import *


class Monster(Game):
    folder = '../data/pp4/monster/encoded/'

    def add_plural234(self, obj):
        if isinstance(obj, dict):
            for key in list(obj):
                if isinstance(obj[key], dict):
                    self.add_plural234(obj[key])
                if 'plural' in key:
                    obj[key.replace('plural', 'plural234')] = obj[key]
                if 'multiple' in key:
                    obj[key.replace('multiple', 'multiple234')] = obj[key]
        if isinstance(obj, list):
            for item in obj:
                self.add_plural234(item)
        return obj

    @decode_mapping(PATH_MONSTER, folder + 'monster.json')
    def encode_monster(self, obj):
        skip = ['id', 'frame', 'role', 'minimumPlayers', 'behaviorClass']
        return self.add_plural234({
            c['id']: {k: v for k, v in c.items() if k not in skip}
            for c in obj['content']
        })

    @decode_mapping(PATH_AUDIENCE_ANSWER, folder + 'audience_answer.json')
    def encode_audience_answer(self, obj):
        return {c['id']: c['answer'] for c in obj['content']}

    @decode_mapping(PATH_AUDIENCE_QUESTION, folder + 'audience_question.json')
    def encode_audience_question(self, obj):
        return {c['id']: c['question'] for c in obj['content']}

    @decode_mapping(PATH_NPC, folder + 'npc.json')
    def encode_npc(self, obj):
        skip = ['id', 'frame', 'role', 'minimumPlayers', 'behaviorClass']
        return self.add_plural234({
            c['id']: {k: v for k, v in c.items() if k not in skip}
            for c in obj['content']
        })

    @decode_mapping(PATH_NPC_ANSWER, folder + 'npc_answer.json')
    def encode_npc_answer(self, obj):
        return {c['id']: c['answer'] for c in obj['content']}

    @decode_mapping(PATH_SECRET_WORDS, folder + 'secret_words.json')
    def encode_secret_words(self, obj):
        return {c['id']: c['word'] for c in obj['content']}

    @decode_mapping(PATH_SPONSORS, folder + 'sponsors.json')
    def encode_sponsor(self, obj):
        return {c['id']: c['sponsor'] for c in obj['content']}

    @decode_mapping(PATH_EXPANDED, folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj):
        return self._encode_subtitles(obj, 'T', '')
