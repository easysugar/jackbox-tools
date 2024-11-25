from lib.game import Game, decode_mapping
from paths import JPP4_PATH

PATH = JPP4_PATH + r'\games\MonsterMingle'
PATH_MONSTER = PATH + r'\content\MMMonster.jet'
PATH_AUDIENCE_ANSWER = PATH + r'\content\MMMonsterAudienceAnswer.jet'
PATH_AUDIENCE_QUESTION = PATH + r'\content\MMMonsterAudienceQuestion.jet'
PATH_NPC = PATH + r'\content\MMMonsterNpc.jet'
PATH_NPC_ANSWER = PATH + r'\content\MMMonsterNpcAnswer.jet'
PATH_SECRET_WORDS = PATH + r'\content\MMSecretWords.jet'
PATH_SPONSORS = PATH + r'\content\MMSponsors.jet'
PATH_LOCALIZATION = PATH + r'\Localization.json'

# encoded
PATH_EXPANDED = r'../data/pp4/monster/swf/expanded.json'


class Monster(Game):
    folder = '../data/pp4/monster/encoded/'
    folder_swf = '../data/pp4/monster/swf/'
    build = '../build/uk/JPP4/MSM/'

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

    @decode_mapping(PATH_MONSTER, build + 'monster.json', PATH_MONSTER)
    def decode_monster(self, obj, trans):
        for c in obj['content']:
            c.update(trans[str(c['id'])])
        return obj

    @decode_mapping(PATH_AUDIENCE_ANSWER, folder + 'audience_answer.json')
    def encode_audience_answer(self, obj):
        return {c['id']: c['answer'] for c in obj['content']}

    @decode_mapping(PATH_AUDIENCE_ANSWER, build + 'audience_answer.json', PATH_AUDIENCE_ANSWER)
    def decode_audience_answer(self, obj, trans):
        for c in obj['content']:
            c['answer'] = trans[str(c['id'])]
        return obj

    @decode_mapping(PATH_AUDIENCE_QUESTION, folder + 'audience_question.json')
    def encode_audience_question(self, obj):
        return {c['id']: c['question'] for c in obj['content']}

    @decode_mapping(PATH_AUDIENCE_QUESTION, build + 'audience_question.json', PATH_AUDIENCE_QUESTION)
    def decode_audience_question(self, obj, trans):
        for c in obj['content']:
            c['question'] = trans[str(c['id'])]
        return obj

    @decode_mapping(PATH_NPC, folder + 'npc.json')
    def encode_npc(self, obj):
        skip = ['id', 'frame', 'role', 'minimumPlayers', 'behaviorClass']
        return self.add_plural234({
            c['id']: {k: v for k, v in c.items() if k not in skip}
            for c in obj['content']
        })

    @decode_mapping(PATH_NPC, build + 'npc.json', PATH_NPC)
    def decode_npc(self, obj, trans):
        for c in obj['content']:
            c.update(trans[str(c['id'])])
        return obj

    @decode_mapping(PATH_NPC_ANSWER, folder + 'npc_answer.json')
    def encode_npc_answer(self, obj):
        return {c['id']: c['answer'] for c in obj['content']}

    @decode_mapping(PATH_NPC_ANSWER, build + 'npc_answer.json', PATH_NPC_ANSWER)
    def decode_npc_answer(self, obj, trans):
        for c in obj['content']:
            c['answer'] = trans[str(c['id'])]
        return obj

    @decode_mapping(PATH_SECRET_WORDS, folder + 'secret_words.json')
    def encode_secret_words(self, obj):
        return {c['id']: c['word'] for c in obj['content']}

    @decode_mapping(PATH_SECRET_WORDS, build + 'secret_words.json', PATH_SECRET_WORDS)
    def decode_secret_words(self, obj, trans):
        for c in obj['content']:
            c['word'] = trans[str(c['id'])]
        return obj

    @decode_mapping(PATH_SPONSORS, folder + 'sponsors.json')
    def encode_sponsor(self, obj):
        return {c['id']: c['sponsor'] for c in obj['content']}

    @decode_mapping(PATH_SPONSORS, build + 'sponsors.json', PATH_SPONSORS)
    def decode_sponsor(self, obj, trans):
        for c in obj['content']:
            c['sponsor'] = trans[str(c['id'])]
        return obj

    @decode_mapping(PATH_EXPANDED, folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj):
        return self._encode_subtitles(obj, 'T', '')

    def decode_media(self):
        audio = {}
        text = self._read_json(self.build + 'text_subtitles.json')
        self._decode_swf_media(path_media=self.folder_swf + 'dict.txt', path_expanded=PATH_EXPANDED, trans=audio | text,
                               path_save=self.folder_swf + 'translated_dict.txt')

    def decode_localization(self):
        self.update_localization(PATH_LOCALIZATION, self.build + 'localization.json')
