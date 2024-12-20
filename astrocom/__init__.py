"""
SynScan Python library to communicate with telescope mounts
"""

### DEFINE LOGGER and EXCEPTION
import logging as _logging

logger = _logging.getLogger('astrocom')
_logging.basicConfig(format='%(levelname)s :: %(funcName)s :: %(message)s')
logger.setLevel(_logging.INFO)

class AstrocomError(Exception):
	"""Define a specific Exception to Astrocom"""
	def __init__(self, msg):
		logger.error(msg)

### IMPORT MODULES
from . import astro
from . import serialport
from . import command

