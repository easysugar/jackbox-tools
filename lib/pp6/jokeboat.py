from lib.game import Game, decode_mapping
from lib.pp4.fibbage3 import generate_additional_context

PATH = r'C:\Program Files (x86)\Steam\steamapps\common\The Jackbox Party Pack 6\games\Jokeboat'


def transform_tags(s: str):
    return s.replace('[i]', '<i>').replace('[/i]', '</i>')


class Jokeboat(Game):
    folder = '../data/pp6/jokeboat/'
    build = '../build/uk/JPP6/Jokeboat/'

    @decode_mapping(PATH + r'\Localization.json', folder + 'localization.json')
    def encode_localization(self, obj):
        return {k: v for k, v in obj['table']['en'].items()}

    @decode_mapping(PATH + r'\content\JokeboatAnimal.jet', folder + 'animal.json')
    def encode_animal(self, obj):
        return {c['id']: c['topic'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatBrand.jet', folder + 'brand.json')
    def encode_brand(self, obj):
        return {c['id']: c['topic'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatCaptainLog.jet', folder + 'captain_log.json')
    def encode_captain_log(self, obj):
        return {c['id']: c['log'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatCaptainLogFinal.jet', folder + 'captain_log_final.json')
    def encode_captain_final_log(self, obj):
        return {c['id']: c['log'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatCatchphrase.jet', folder + 'catchphrase.json')
    def encode_catchphrase(self, obj):
        return {c['id']: c['topic'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatCatchphraseFill.jet', folder + 'catchphrase_fill.json')
    def encode_catchphrase_fill(self, obj):
        return {c['id']: c['topic'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatFood.jet', folder + 'food.json')
    def encode_food(self, obj):
        return {c['id']: c['topic'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatLocation.jet', folder + 'location.json')
    def encode_location(self, obj):
        return {c['id']: c['topic'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatObject.jet', folder + 'object.json')
    def encode_object(self, obj):
        return {c['id']: c['topic'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatPerson.jet', folder + 'person.json')
    def encode_person(self, obj):
        return {c['id']: c['topic'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatThings.jet', folder + 'thing.json')
    def encode_thing(self, obj):
        return {c['id']: c['topic'] for c in obj['content']}

    @decode_mapping(PATH + r'\content\JokeboatSetup.jet', folder + 'setup.json')
    def encode_setup(self, obj):
        res = {}
        for c in obj['content']:
            setup = c['setup'] + ' ' + c['punchline']
            decoys = '\n'.join([i.replace(' | ', '; ') for i in c['decoys']])
            context = setup + generate_additional_context(c)
            res[c['id']] = {
                'setup': {'text': setup, 'crowdinContext': context},
                'decoys': {'text': decoys, 'crowdinContext': context},
            }
        return res
