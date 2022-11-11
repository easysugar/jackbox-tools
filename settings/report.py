BLUE = (89, 180, 222)
GREEN = (74, 186, 74)
GREY = (220, 222, 220)

IMAGES = {
    'tko': 'https://static.wikia.nocookie.net/jackboxgames/images/0/07/TeeKO-logo.png/revision/latest?cb=20210811073109',
    'q2': 'https://cdn.cloudflare.steamstatic.com/steam/apps/1111940/capsule_616x353.jpg?t=1635966633',
    'q3': 'https://jackboxgames.b-cdn.net/wp-content/uploads/2020/09/q3_websiteTile_v1.jpg',
    'tmp2': 'https://jackboxgames.b-cdn.net/wp-content/uploads/2019/08/TMP2_tile.jpg',
    'd2': 'https://images.greenmangaming.com/bdefabab026045ec8b1171728c051ea3/25ea8336263d4cc8b80126e7e15fd937.jpg',
    'tmp1': 'https://static.wikia.nocookie.net/jackboxgames/images/9/96/TMPBanner.png/revision/latest?cb=20210811072615',
    'poll': 'https://static.wikia.nocookie.net/jackboxgames/images/0/04/GuesspionageBanner.png/revision/latest?cb=20210811072840',
    'fakin': 'https://static.wikia.nocookie.net/jackboxgames/images/7/7f/Fakin-It.png/revision/latest?cb=20210811072948',
}

GRID = {
    '3й пак': ['tmp1', 'poll', 'fakin'],
    'Стартер пак': ['tmp2', 'tko', 'q3'],
    'Окремі ігри': ['d2', 'q2'],
}
GAMES = {
    'q3': {'name': 'Жартлист 3'},
    'q2': {'name': 'Жартлист 2', 'approved': 78, 'translated': 100},
    'tmp2': {'name': 'Смертельні\nВечорниці 2', 'approved': 43, 'translated': 99},
    'tko': {'name': 'Футбол К.О.', 'approved': 100, 'translated': 100, 'actor': 'Pad0n', 'status': '👑'},
    'd2': {'name': 'Малювач 2', 'approved': 66, 'translated': 99, 'actor': 'Lunar Shadow'},
    'poll': {'name': 'Шпигадаш'},
    'tmp1': {'name': 'Смертельні\nВечорниці'},
    'fakin': {'name': 'Обдурисвіт', 'approved': 7, 'translated': 27}
}
TOP_CONTRIBUTORS_TEXT = "Топ контриб'юторів"

WIDTH, HEIGHT = 310, 270

FONT_HEAD = '../fonts/a_AlbionicTitulInfl_Bold.ttf', 20
FONT_GAME = '../fonts/a_AlbionicTitulInfl_Bold.ttf', 35
FONT_PERCENT = '../fonts/Acme-Regular.ttf', 30
FONT_VOICE = '../fonts/Acme-Regular.ttf', 28
FONT_CONTRIBUTORS = '../fonts/Acme-Regular.ttf', 18
# FONT_CONTRIBUTORS = 'seguiemj.ttf', 20
ROW_CONTRIBUTORS = 0.1

AVATARS = {
    'Lunar Shadow': 'https://avatars.akamai.steamstatic.com/377c64e345750b516ff048186d96ec79fdd90df5_full.jpg',
    'Pad0n': 'https://avatars.akamai.steamstatic.com/ddd33361ad9ca81db1e35ea33d348f775cee3a89_full.jpg',
}

CONTRIBUTORS = [
    {
        "name": "Artem Tsynoborenko",
        "count": 1681,
        "url": "https://crowdin-static.downloads.crowdin.com/avatar/15373090/medium/fc84372c61988d23bca06c328bbfaa7a.jpeg"
    },
    {
        "name": "Irinniada",
        "count": 1603,
        "url": "https://crowdin-static.downloads.crowdin.com/avatar/15154446/medium/4c7c90ac5336b1f46da392ad9437ee6f.png"
    },
    {
        "name": "easy.sugar",
        "count": 1374,
        "url": "https://crowdin-static.downloads.crowdin.com/avatar/15271256/medium/109a081d51c0b02507963f58320e63ef.jpeg"
    },
    {
        "name": "Timonn",
        "count": 416,
        "url": "https://crowdin-static.downloads.crowdin.com/avatar/15254186/medium/2945d8546ba2af1a3a9cddff0fe81280_default.png"
    },
    {
        "name": "h-hh-hhh",
        "count": 176,
        "url": "https://crowdin-static.downloads.crowdin.com/avatar/15433330/medium/4cbe28eaad008cd7988aeb39a932b876.png"
    },
    {
        "name": "fozerion",
        "count": 14,
        "url": "https://crowdin-static.downloads.crowdin.com/avatar/15476814/medium/5f3c7ae3f81b0b7a7d5c82e2a48dea96.png"
    },
    {
        "name": "viktor_kozachok",
        "count": 5,
        "url": "https://crowdin-static.downloads.crowdin.com/avatar/15424414/medium/cd0facc897f92f62ac663f26ab71feda.png"
    },
    {
        "name": "ilyamaximencko",
        "count": 1,
        "url": "https://crowdin-static.downloads.crowdin.com/avatar/15433512/medium/e8a29581bced70d99520dc75d173ad25.png"
    }
]
