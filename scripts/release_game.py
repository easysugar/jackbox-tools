from datetime import datetime

from lib import *

START_TIME = datetime(2023, 1, 1)
GAME = Quiplash2
# Games allowed: JPP3, TJSP, Drawful2, Quiplash2


if __name__ == '__main__':
    GAME().release(START_TIME)
