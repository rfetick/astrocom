"""
Command line interface
"""

import cmd
import time
from astrocom import logger
from astrocom.astro import turn_to_hms, turn_to_dms
from astrocom.serialport import SynScan, AstrocomException

class MountCmd(cmd.Cmd):
	intro = "\nWelcome to the ASTROCOM command line.\nType help or ? to list commands.\n"
	prompt = "(astrocom) "
	
	def __init__(self, portname):
		super().__init__()
		self.synscan = SynScan(portname)
		
	def do_init(self, _):
		"""
		Initialize both motors.
		> init
		"""
		self.synscan.init_motor(1)
		self.synscan.init_motor(2)
		
	def do_status(self, _):
		"""
		Get status and position of both motors.
		> status
		"""
		status_1 = self.synscan.get_axis_status_as_str(1)
		status_2 = self.synscan.get_axis_status_as_str(2)
		position_1 = self.synscan.get_axis_position(1)
		position_2 = self.synscan.get_axis_position(2)
		print(time.ctime())
		if (position_1 is not AstrocomException) and (status_1 is not AstrocomException):
			print('RA : %8.3f° %s'%(360*position_1,status_1))
		if (position_2 is not AstrocomException) and (status_2 is not AstrocomException):
			print('DEC: %8.3f° %s'%(360*position_2,status_2))
	
	def do_goto(self, arg):
		"""
		Goto position on given axis.
		> goto [axis] [degree]
		"""
		arg = arg.split()
		axis = int(arg[0])
		ratio = float(arg[1])/360
		self.do_stop(arg[0]) # automatically stop rotation
		self.synscan.set_goto_target(axis, ratio)
		self.do_mode(arg[0]+' goto') # automatically set GOTO
	
	def do_start(self, axnb):
		"""
		Start moving on one or both axis.
		> start [axis]
		"""
		if len(axnb)==0:
			 axnb = '3' # both axis if nothing provided
		try:
			axnb = int(axnb)
			self.synscan.start_motion(axnb)
		except:
			logger.warning('Cannot get axis number')
	
	def do_stop(self, axnb):
		"""
		Stop moving on one or both axis.
		> stop [axis]
		"""
		if len(axnb)==0:
			axnb = '3' # both axis if nothing provided
		try:
			axnb = int(axnb)
			self.synscan.stop_motion_now(axnb)
		except:
			logger.warning('Cannot get axis number')
			
	def do_mode(self, arg):
		"""
		Define axis mode.
		> mode [axis] [forward backward fast slow goto track]
		"""
		arg = arg.split()
		if len(arg)<2:
			logger.warning('Not enough arguments')
		else:
			axis = int(arg[0])
			# Get previous mode
			goto_or_track = self.synscan.get_axis_status_mode(axis)
			speed = self.synscan.get_axis_status_speed(axis)
			direction = self.synscan.get_axis_status_direction(axis)
			# Update if exists
			for a in arg[1:]:
				if a.upper() in ['FORWARD','BACKWARD']:
					direction = getattr(self.synscan, a.upper())
				if a.upper() in ['FAST','SLOW']:
					speed = getattr(self.synscan, a.upper())
				if a.upper() in ['GOTO','TRACK']:
					goto_or_track = getattr(self.synscan, a.upper())
			# Send
			if (goto_or_track is not AstrocomException) and (speed is not AstrocomException) and (direction is not AstrocomException):
				self.synscan.set_motion_mode(axis, goto_or_track, speed, direction)
				self.do_status(None) # also show status
			
	def do_exit(self, arg):
		"""Exit the command line interpreter"""
		return True

					
			
