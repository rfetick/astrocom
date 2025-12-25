"""
SynScan Python library to communicate with telescope mounts
"""

### DEFINE COLORS
class COLORS:
	GREEN = "\x1b[32;20m"
	BLUE = "\033[34m"
	YELLOW = "\x1b[33;20m"
	RED = "\x1b[31;20m"
	CYAN = '\033[36m'
	RESET = '\033[0m'

### DEFINE LOGGER and EXCEPTION
import logging

class _CustomFormatter(logging.Formatter):
    """
    https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    """
    
    FORMAT = "%(levelname)s - %(message)s"

    FORMAT_LIST = {
        logging.DEBUG: COLORS.YELLOW + FORMAT + COLORS.RESET,
        logging.INFO: COLORS.GREEN + FORMAT + COLORS.RESET,
        logging.WARNING: COLORS.YELLOW + FORMAT + COLORS.RESET,
        logging.ERROR: COLORS.RED + FORMAT + COLORS.RESET,
        logging.CRITICAL: COLORS.RED + FORMAT + COLORS.RESET
    }

    def format(self, record):
        log_fmt = self.FORMAT_LIST.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logger = logging.getLogger('astrocom')
logger.setLevel(logging.DEBUG)
_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)
_ch.setFormatter(_CustomFormatter())
logger.addHandler(_ch)

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
from . import interface

