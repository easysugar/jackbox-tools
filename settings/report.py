import json

import yaml

BLUE = (89, 180, 222)
GREEN = (74, 186, 74)
GREY = (220, 222, 220)

TOP_CONTRIBUTORS_TEXT = "Топ контриб'юторів"

WIDTH, HEIGHT = 310, 270

FONT_HEAD = '../fonts/a_AlbionicTitulInfl_Bold.ttf', 20
FONT_GAME = '../fonts/a_AlbionicTitulInfl_Bold.ttf', 35
FONT_PERCENT = '../fonts/Acme-Regular.ttf', 30
FONT_VOICE = '../fonts/Acme-Regular.ttf', 28
FONT_CONTRIBUTORS = '../fonts/Acme-Regular.ttf', 18
# FONT_CONTRIBUTORS = 'seguiemj.ttf', 20
ROW_CONTRIBUTORS = 0.1

GAMES = yaml.full_load(open('../settings/report.yaml'))
CONTRIBUTORS = json.load(open('contributors.json'))
PROGRESS = json.load(open('progress.json'))
