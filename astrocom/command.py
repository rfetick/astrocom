"""
Command line interface
"""

import cmd
import datetime
from astrocom import logger
from astrocom.astro import longitude_to_sideraltime, dms_to_deg, deg_to_hms, deg_to_dms
from astrocom.serialport import SynScan, AstrocomException

class MountCmd(cmd.Cmd):
	intro = "\n".join(("","="*30,"Welcome to the ASTROCOM command line.","Type help or ? to list commands.","="*30,""))
	prompt = "(astrocom) "
	
	def __init__(self, portname, latitude_tpl, longitude_tpl):
		super().__init__()
		self.synscan = SynScan(portname)
		self.latitude = latitude_tpl #TODO use it to get mount sky coordinates
		self.longitude = longitude_tpl #TODO use it to get mount sky coordinates
		if latitude_tpl[0]>=0:
			self.synscan.north_south = self.synscan.NORTH
		else:
			self.synscan.north_south = self.synscan.SOUTH
		
	def do_help(self, _):
		"""
        Print help on functions
        > help
        """
		fct_list = [f for f in self.__dir__() if f.startswith('do_')]
		for f in fct_list:
			doc = getattr(self,f).__doc__
			doc_lines = doc.split('\n')
			fill = max(25-len(doc_lines[1]),1)
			print(doc_lines[1].replace("> "," "*4) + ' '*fill + doc_lines[0])
        
	def do_init(self, _):
		"""
		Initialize both motors
		> init
		"""
		self.synscan.init_motor(1)
		self.synscan.init_motor(2)
		
	def do_status(self, _):
		"""
		Get status and position of both motors
		> status
		"""
		status_1 = self.synscan.get_axis_status_as_str(1)
		status_2 = self.synscan.get_axis_status_as_str(2)
		position_1 = self.synscan.get_axis_position(1)
		position_2 = self.synscan.get_axis_position(2)
		sideral_time_deg = longitude_to_sideraltime(dms_to_deg(self.longitude)).degree
		if (position_1 is not AstrocomException) and (status_1 is not AstrocomException):
			sky_ra = deg_to_hms(sideral_time_deg - 360*position_1)
			print("""RA : %02u:%02u:%02u %s"""%(sky_ra[0], sky_ra[1], sky_ra[2], status_1))
		if (position_2 is not AstrocomException) and (status_2 is not AstrocomException):
			sky_dec = deg_to_dms(360*position_2)
			print("""DEC: %02u°%02u'%02u" %s"""%(sky_dec[0], sky_dec[1], sky_dec[2], status_2))
	
	def do_time(self, arg):
		"""
		Print current time
		> time
		"""
		dt_local = datetime.datetime.now()
		dt_utc = dt_local.utcnow()
		dt_sid = longitude_to_sideraltime(dms_to_deg(self.longitude))
		print('LOCAL  : %02u:%02u:%02u'%(dt_local.hour, dt_local.minute, dt_local.second))
		print('UTC    : %02u:%02u:%02u'%(dt_utc.hour, dt_utc.minute, dt_utc.second))
		print('SIDERAL: %02u:%02u:%02u'%dt_sid.hms)
    
	def do_goto(self, arg):
		"""
		Goto position on an axis
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
		Start moving on one or both axis
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
		Stop moving on one or both axis
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
		Define axis mode
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
		"""
        Exit the command line interpreter
        > exit
        """
		return True

					
			
