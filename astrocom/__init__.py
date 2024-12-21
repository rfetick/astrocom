"""
SynScan Python library to communicate with telescope mounts
"""

### DEFINE PRINT COLORS
class COLORS:
	BLACK = '\033[30m'
	RED = '\033[31m'
	GREEN = '\033[32m'
	YELLOW = '\033[33m' # orange on some systems
	BLUE = '\033[34m'
	MAGENTA = '\033[35m'
	CYAN = '\033[36m'
	LIGHT_GRAY = '\033[37m'
	DARK_GRAY = '\033[90m'
	BRIGHT_RED = '\033[91m'
	BRIGHT_GREEN = '\033[92m'
	BRIGHT_YELLOW = '\033[93m'
	BRIGHT_BLUE = '\033[94m'
	BRIGHT_MAGENTA = '\033[95m'
	BRIGHT_CYAN = '\033[96m'
	WHITE = '\033[97m'
	RESET = '\033[0m' # called to return to standard terminal text color


### DEFINE LOGGER and EXCEPTION
import logging as _logging

logger = _logging.getLogger('astrocom')
_logging.basicConfig(format='%(levelname)s :: %(funcName)s :: %(message)s')
logger.setLevel(_logging.INFO)

class AstrocomError(Exception):
	"""Define a specific Exception to Astrocom"""
	def __init__(self, *args):
		logger.error(*args)

class AstrocomSuccess:
	def __init__(self, *args):
		logger.info(*args)

### IMPORT MODULES
from . import astro
from . import serialport
from . import command

