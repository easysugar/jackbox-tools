from lib.game import Game, decode_mapping


class Fibbage3(Game):
    folder = '../data/pp4/fibbage3/'

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
