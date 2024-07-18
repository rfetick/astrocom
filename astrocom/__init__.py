"""
SynScan Python library to communicate with telescope mounts
"""

import logging as _logging

logger = _logging.getLogger('astrocom')
_logging.basicConfig(format='%(levelname)s :: %(funcName)s :: %(message)s')
logger.setLevel(_logging.INFO)

from . import astro
from . import serialport
from . import command

