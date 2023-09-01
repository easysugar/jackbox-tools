import json

import yaml

BLUE = (89, 180, 222)
GREEN = (74, 186, 74)
GREY = (220, 222, 220)

TOP_CONTRIBUTORS_TEXT = "Топ перекладачів"
TOP_PATRONS_TEXT = "Особлива подяка"

WIDTH, HEIGHT = 465, 405
COLUMNS_COUNT = 5

FONT_HEAD = '../fonts/a_AlbionicTitulInfl_Bold.ttf', 30
FONT_GAME = '../fonts/a_AlbionicTitulInfl_Bold.ttf', 52
FONT_PERCENT = '../fonts/Acme-Regular.ttf', 45
FONT_VOICE = '../fonts/Acme-Regular.ttf', 42
FONT_CONTRIBUTORS = '../fonts/Acme-Regular.ttf', 28
# FONT_CONTRIBUTORS = 'seguiemj.ttf', 20
ROW_CONTRIBUTORS = 0.05

PACKS = yaml.full_load(open('../settings/report.yaml'))
GAMES = {game: {**PACKS[pack][game], 'pack': pack} for pack in PACKS for game in PACKS[pack]}
CONTRIBUTORS = json.load(open('contributors.json'))
CONTRIBUTORS_POSITION = 2, 3
PATRONS = json.load(open('patrons.json'))
PATRONS_POSITION = 2, 4
PROGRESS = json.load(open('progress.json'))
GAMES_PATH = {game: GAMES[game].get('path') for game in GAMES}

LOGO_IMAGE = '../assets/jb_ua_logo.png'
LOGO_TEXT = 'Серпень 2023'
LOGO_POSITION = 3, 2
