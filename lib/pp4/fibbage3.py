from lib.game import Game, decode_mapping, read_from_folder, write_to_folder


def generate_additional_context(c):
    context = ''
    if c['us'] or c['x']:
        context += '\n-------------'
        if c['us']:
            context += '\nfor USA'
        if c['x']:
            context += '\n18+'
    return context


class Fibbage3(Game):
    game_path = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 4\games\Fibbage3'
    fibbage_shortie = game_path + r'\content\fibbageshortie.jet'
    fibbage_shortie_dir = game_path + r'\content\fibbageshortie'
    fibbage_tmi = game_path + r'\content\tmishortie.jet'
    fibbage_tmi_dir = game_path + r'\content\tmishortie'
    fibbage_final = game_path + r'\content\finalfibbage.jet'
    fibbage_final_dir = game_path + r'\content\finalfibbage'
    fibbage_special = game_path + r'\content\fibbagespecial.jet'
    folder = '../data/pp4/fibbage3/'
    build = '../build/uk/JPP4/Fibbage3/'

    def decode_localization(self):
        self.update_localization(self.game_path + r'\Localization.json', self.build + 'localization.json')

    @decode_mapping(build + 'text_subtitles.json', out=False)
    def decode_media(self, text: dict):
        text = {k: v['text'] for k, v in text.items()}
        self._decode_swf_media(
            path_media=self.folder + 'dict.txt',
            path_expanded=self.folder + 'expanded.json',
            trans=text,
            path_save=self.folder + 'translated_dict.txt',
        )

    @decode_mapping(folder + 'expanded.json', folder + 'text_subtitles.json')
    def encode_text_subtitles(self, obj: dict):
        return {v['id']: {"text": v['text'], "crowdinContext": v['tags']}
                for c in obj
                for v in c['versions']
                if c['type'] == 'T'}

    @decode_mapping(folder + 'expanded.json', folder + 'audio_subtitles.json')
    def encode_audio_subtitles(self, obj: dict):
        return {
            v['id']: {"text": v['text'].replace('[category=host]', '').replace('[category=warning]', ''), "crowdinContext": c.get('crowdinContext')}
            for c in obj
            for v in c['versions']
            if c['type'] == 'A' and '[category=host]' in v['text'] and 'SFX' not in v['text']}

    @decode_mapping(fibbage_shortie, folder + 'fibbage_shortie.json')
    def encode_fibbage_shortie(self, obj: dict):
        res = {}
        for c in obj['content']:
            o = read_from_folder(str(c['id']), self.fibbage_shortie_dir)
            context = o['QuestionText']['v'] + generate_additional_context(c)
            row = {
                'question': {'text': o['QuestionText']['v'], 'crowdinContext': context},
                'suggestions': {'text': o['Suggestions']['v'], 'crowdinContext': context},
                'category': {'text': o['Category']['v'], 'crowdinContext': context},
                'answer': {'text': o['CorrectText']['v'], 'crowdinContext': context},
                'alternate_answer': {'text': o['AlternateSpellings']['v'], 'crowdinContext': context},
            }
            if response := o.get('CorrectAudio', {}).get('s'):
                row['response'] = {'text': response.replace('[category=host]', ''), 'crowdinContext': context}
            if o['QuestionAudio']['s'] != '[category=host]' + o['QuestionText']['v']:
                row['audio'] = {'text': o['QuestionAudio']['s'].replace('[category=host]', ''), 'crowdinContext': context}
            assert o['BumperType']['v'] == 'None'
            res[c['id']] = row
        return res

    @decode_mapping(fibbage_shortie, build + 'fibbage_shortie.json', fibbage_shortie)
    def decode_fibbage_shortie(self, obj, trans):
        for c in obj['content']:
            t = trans[str(c['id'])]
            c['category'] = t['category']['text']
            o = read_from_folder(c['id'], self.fibbage_shortie_dir)
            o['Suggestions']['v'] = t['suggestions']['text']
            o['QuestionText']['v'] = t['question']['text']
            o['Category']['v'] = t['category']['text']
            o['CorrectText']['v'] = t['answer']['text']
            o['AlternateSpellings']['v'] = t['alternate_answer']['text']
            write_to_folder(c['id'], self.fibbage_shortie_dir, o)
        return obj

    @decode_mapping(fibbage_tmi, folder + 'fibbage_tmi.json')
    def encode_fibbage_tmi(self, obj: dict):
        res = {}
        for c in obj['content']:
            o = read_from_folder(str(c['id']), self.fibbage_tmi_dir)
            context = o['QuestionText']['v'] + generate_additional_context(c)
            row = {
                'question': {'text': o['QuestionText']['v'], 'crowdinContext': context},
                'personal_question': {'text': o['PersonalQuestionText']['v'], 'crowdinContext': context},
                'suggestions': {'text': o['Suggestions']['v'], 'crowdinContext': context},
            }

            res[c['id']] = row
        return res

    @decode_mapping(fibbage_tmi, build + 'fibbage_tmi.json', fibbage_tmi)
    def decode_fibbage_tmi(self, obj, trans):
        for c in obj['content']:
            t = trans[str(c['id'])]
            o = read_from_folder(c['id'], self.fibbage_tmi)
            o['PersonalQuestionText']['v'] = c['personal'] = t['personal_question']['text']
            o['QuestionText']['v'] = t['question']['text']
            o['Suggestions']['v'] = t['suggestions']['text']
            write_to_folder(c['id'], self.fibbage_tmi, o)
        return obj

    @decode_mapping(fibbage_final, folder + 'fibbage_final.json')
    def encode_fibbage_final(self, obj: dict):
        res = {}
        for c in obj['content']:
            o = read_from_folder(str(c['id']), self.fibbage_final_dir)
            context = o['QuestionText']['v'] + generate_additional_context(c)
            row = {
                'question': {'text': o['QuestionText']['v'], 'crowdinContext': context},
                'suggestions': {'text': o['Suggestions']['v'].replace('|', '; ').replace(',', '\n'), 'crowdinContext': context},
                # 'category': {'text': o['Category']['v'], 'crowdinContext': context},
                'answer': {
                    'text': o['CorrectText']['v'].replace('|', '; ') + '\n' + o['AlternateSpellings']['v'].replace('|', '; ').replace(',', '\n'),
                    'crowdinContext': context
                },
            }
            row['answer']['text'].strip()
            if response := o.get('CorrectAudio', {}).get('s'):
                row['response'] = {'text': response.replace('[category=host]', ''), 'crowdinContext': context}
            if o['QuestionAudio']['s'] != '[category=host]' + o['QuestionText']['v']:
                row['audio'] = {'text': o['QuestionAudio']['s'].replace('[category=host]', ''), 'crowdinContext': context}
            res[c['id']] = row
        return res

    @staticmethod
    def _decode_final_suggestions(text: str, correct=False):
        suggestions = []
        for s in text.strip().split('\n'):
            assert s.count(';') == 1
            s1, s2 = s.split(';')
            suggestions.append(f'{s1}|{s2}')
        if correct:
            assert len(suggestions) == 1
        return ','.join(suggestions)

    @decode_mapping(fibbage_final, build + 'fibbage_final.json', fibbage_final)
    def decode_fibbage_final(self, obj, trans):
        for c in obj['content']:
            t = trans[str(c['id'])]
            o = read_from_folder(c['id'], self.fibbage_final)
            o['QuestionText']['v'] = t['question']['text']
            o['Suggestions']['v'] = self._decode_final_suggestions(t['suggestions']['text'])
            answer, spellings = t['answer']['text'].strip().split('\n', 1)
            o['CorrectText']['v'] = self._decode_final_suggestions(answer)
            o['AlternateSpellings']['v'] = self._decode_final_suggestions(spellings)
            write_to_folder(c['id'], self.fibbage_final, o)
        return obj

    @decode_mapping(fibbage_special, folder + 'fibbage_special.json')
    def encode_fibbage_special(self, obj: dict):
        res = {}
        for c in obj['content']:
            o = read_from_folder(str(c['id']), self.fibbage_special)
            context = {'crowdinContext': o['QuestionText']['v'] + '\nType: ' + c['bumper'] + generate_additional_context(c)}
            row = {
                'question': {'text': o['QuestionText']['v'], **context},
                'suggestions': {'text': o['Suggestions']['v'], **context},
                'answer': {'text': (o['CorrectText']['v'] + '\n' + o['AlternateSpellings']['v'].replace(',', '\n')).strip(), **context},
            }
            if response := o['CorrectAudio']['s'].replace('[category=host]', ''):
                row['response'] = {'text': response, **context}
            if bumper_audio := o['BumperAudio']['s'].replace('[category=host]', ''):
                row['bumper_audio'] = {'text': bumper_audio, **context}
            if o['QuestionAudio']['s'] != '[category=host]' + o['QuestionText']['v']:
                row['audio'] = {'text': o['QuestionAudio']['s'].removeprefix('[category=host]'), **context}
            if media_date := o['SocialMediaDate']['v']:
                row['media_date'] = {'text': media_date, **context}
            if media_name := o['SocialMediaName']['v']:
                row['media_name'] = {'text': media_name, **context}
            res[c['id']] = row
        return res

    @decode_mapping(fibbage_special, build + 'fibbage_special.json', fibbage_special)
    def decode_fibbage_special(self, obj, trans):
        for c in obj['content']:
            t = trans[str(c['id'])]
            o = read_from_folder(c['id'], self.fibbage_special)
            o['QuestionText']['v'] = t['question']['text']
            o['Suggestions']['v'] = t['suggestions']['text']
            answer, *spellings = t['answer']['text'].strip().split('\n')
            o['CorrectText']['v'] = answer.strip()
            o['AlternateSpellings']['v'] = ','.join([s.strip() for s in spellings if s.strip()])
            if media_date := t.get('media_date'):
                o['SocialMediaDate']['v'] = media_date['text']
            if media_name := t.get('media_name'):
                o['SocialMediaName']['v'] = media_name['text']
            write_to_folder(c['id'], self.fibbage_special, o)
        return obj
