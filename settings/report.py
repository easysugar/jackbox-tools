import json

import yaml

BLUE = (89, 180, 222)
GREEN = (74, 186, 74)
GREY = (220, 222, 220)

GAMES = yaml.full_load(open('../settings/report.yaml'))

# IMAGES = {name: game['img'] for name, game in config['games'].items()}
# GRID = {row['name']: row['order'].strip().split(', ') for row in config['grid']}
# GAMES = {name: game for name, game in config['games'].items()}

# IMAGES = {
#     'tko': 'https://static.wikia.nocookie.net/jackboxgames/images/0/07/TeeKO-logo.png/revision/latest?cb=20210811073109',
#     'q2': 'https://cdn.cloudflare.steamstatic.com/steam/apps/1111940/capsule_616x353.jpg?t=1635966633',
#     'q3': 'https://jackboxgames.b-cdn.net/wp-content/uploads/2020/09/q3_websiteTile_v1.jpg',
#     'tmp2': 'https://jackboxgames.b-cdn.net/wp-content/uploads/2019/08/TMP2_tile.jpg',
#     'd2': 'https://images.greenmangaming.com/bdefabab026045ec8b1171728c051ea3/25ea8336263d4cc8b80126e7e15fd937.jpg',
#     'tmp1': 'https://static.wikia.nocookie.net/jackboxgames/images/9/96/TMPBanner.png/revision/latest?cb=20210811072615',
#     'poll': 'https://static.wikia.nocookie.net/jackboxgames/images/0/04/GuesspionageBanner.png/revision/latest?cb=20210811072840',
#     'fakin': 'https://static.wikia.nocookie.net/jackboxgames/images/7/7f/Fakin-It.png/revision/latest?cb=20210811072948',
# }

# GRID = {
#     '3й пак': ['poll', 'fakin'],
#     '4й пак': ['mmm', 'sti'],
#     'Стартер пак': ['tmp2', 'tko', 'q3'],
#     'Окремі ігри': ['d2', 'q2'],
# }
# GAMES = {
#     'q3': {'name': 'Жартлист 3'},
#     'q2': {'name': 'Жартлист 2'},
#     'tmp2': {'name': 'Смертельні\nВечорниці 2'},
#     'tko': {'name': 'Футбол К.О.', 'actor': 'Pad0n', 'status': '👑'},
#     'd2': {'name': 'Малювач 2', 'actor': 'Lunar Shadow'},
#     'poll': {'name': 'Шпигадаш'},
#     'tmp1': {'name': 'Смертельні\nВечорниці'},
#     'fakin': {'name': 'Обдурисвіт'}
# }
TOP_CONTRIBUTORS_TEXT = "Топ контриб'юторів"

WIDTH, HEIGHT = 310, 270

FONT_HEAD = '../fonts/a_AlbionicTitulInfl_Bold.ttf', 20
FONT_GAME = '../fonts/a_AlbionicTitulInfl_Bold.ttf', 35
FONT_PERCENT = '../fonts/Acme-Regular.ttf', 30
FONT_VOICE = '../fonts/Acme-Regular.ttf', 28
FONT_CONTRIBUTORS = '../fonts/Acme-Regular.ttf', 18
# FONT_CONTRIBUTORS = 'seguiemj.ttf', 20
ROW_CONTRIBUTORS = 0.1

# AVATARS = {
#     'Lunar Shadow': 'https://avatars.akamai.steamstatic.com/377c64e345750b516ff048186d96ec79fdd90df5_full.jpg',
#     'Pad0n': 'https://avatars.akamai.steamstatic.com/ddd33361ad9ca81db1e35ea33d348f775cee3a89_full.jpg',
# }

CONTRIBUTORS = json.load(open('contributors.json'))
PROGRESS = json.load(open('progress.json'))
