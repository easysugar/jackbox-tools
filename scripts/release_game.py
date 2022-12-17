from datetime import datetime

from lib import *
from lib.pp3.jpp3 import JPP3

START_TIME = datetime(2022, 12, 5)


def release_drawful2():
    PATH_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Drawful 2'
    PATH_RELEASE = r'C:\Users\админ\Desktop\Jackbox\drawful2\jackbox-drawful-2-ua'
    t = Drawful2()
    t.decode_localization()
    t.decode_decoy()
    t.decode_prompt()
    t.unpack_question()
    t.copy_to_release(PATH_GAME, PATH_RELEASE, START_TIME)


def release_starter_pack():
    TJSP().release(START_TIME)


def release_pack_3():
    JPP3().release(START_TIME)


if __name__ == '__main__':
    release_pack_3()
