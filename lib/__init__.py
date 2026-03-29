import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

from .crowdin import Crowdin
from .pp11 import *
from .pp3 import *
from .pp4 import *
from .pp5 import *
from .pp6 import *
from .pp7 import *
from .pp8 import *
from .standalone import *
from .tjsp import *
