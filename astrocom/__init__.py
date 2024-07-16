"""
SynScan Python library to communicate with telescope mounts
"""

import logging
logging.basicConfig(format='%(levelname)s :: %(message)s')

from . import astro
from . import serialport
from . import command

