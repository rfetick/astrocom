"""
Command line interface
"""

import cmd
import datetime
from astrocom import logger
from astrocom.astro import read_bsc, cardinal_point, MountPosition, RaDec
from astrocom.serialport import SynScan, AstrocomException

class MountCmd(cmd.Cmd):
	intro = "\n".join(("","="*35,"Welcome to the ASTROCOM command line.","Type help or ? to list commands.","="*35,""))
	prompt = "(astrocom) "
	
	def __init__(self, portname, longitude, latitude):
		super().__init__()
		self.catalog = read_bsc()
		self.synscan = SynScan(portname)
		self.mount = MountPosition(longitude, latitude)
		if latitude[0]>=0:
			self.synscan.north_south = self.synscan.NORTH
		else:
			self.synscan.north_south = self.synscan.SOUTH
	
	def postcmd(self, *args, **kwargs):
		"""Print empty line at end of each command"""
		print()
		return super().postcmd(*args,**kwargs)
	
	def do_help(self, _):
		"""
		Print help on functions
		> help
        """
		fct_list = [f for f in self.__dir__() if f.startswith('do_') and f!='do_help']
		for f in fct_list:
			doc = getattr(self,f).__doc__
			doc_lines = doc.split('\n')
			doc_lines[1] = doc_lines[1].replace("\t","")
			doc_lines[2] = doc_lines[2].replace("> "," "*4).replace("\t","")
			fill = max(26-len(doc_lines[2]),2)
			print(doc_lines[2] + ' '*fill + doc_lines[1])
        
	def do_bsc(self, arg):
		"""
		Print stars of the Bright Star Catalog
		> bsc [nb]
        """
		arg = arg.split()
		nb_star_print = 0
		print(self.catalog[0].header + '  %4s  %2s'%('ALT','AZ'))
		print('-'*(len(self.catalog[0].header)+10))
		for i in range(len(self.catalog)):
			alt,az = self.catalog[i].altaz(self.mount.longitude, self.mount.latitude)
			if alt > 0:
				print(self.catalog[i].__str__() + '  %3u°  %2s'%(alt,cardinal_point(az)))
				nb_star_print += 1
			if nb_star_print == int(arg[0]):
				break
        
	def do_init(self, _):
		"""
		Initialize motors
		> init
		"""
		ans1 = self.synscan.init_motor(1)
		ans2 = self.synscan.init_motor(2)
		if not AstrocomException in [ans1,ans2]:
			north = self.synscan.north_south==self.synscan.NORTH
			print('Assume looking at the celestial pole at startup')
			self.synscan.set_axis_position(2,(north - (not north))*0.25)
			speed = self.synscan.get_rotation_speed(1)
			if speed is not AstrocomException:
				print('Speed: %.4f °/h'%(speed*3600))
			self.do_status(_)
		
	def do_status(self, _):
		"""
		Print status and position of motors
		> status
		"""
		status_1 = self.synscan.get_axis_status_as_str(1)
		status_2 = self.synscan.get_axis_status_as_str(2)
		position_1 = self.synscan.get_axis_position(1)
		position_2 = self.synscan.get_axis_position(2)
		goto_1 = self.synscan.get_goto_target(1)
		goto_2 = self.synscan.get_goto_target(2)
		if AstrocomException not in [status_1, position_1, goto_1]:
			self.mount.hour_angle = 360*position_1 # degree
			goto_1_str = self.mount.complementary_angle(360*goto_1).ra_str
			print("""RA : %s ( %s) %s"""%(self.mount.ra_str, goto_1_str, status_1))
		if AstrocomException not in [status_2, position_2, goto_2]:
			self.mount.dec = 360*position_2
			goto_2_str = RaDec(0, 360*goto_2).dec_str
			print("""DEC:%s (%s) %s"""%(self.mount.dec_str, goto_2_str, status_2))
	
	def do_time(self, arg):
		"""
		Print current time
		> time
		"""
		dt_local = datetime.datetime.now()
		dt_utc = dt_local.utcnow()
		dt_sid = self.mount.sideral_time
		print('LOCAL  : %02u:%02u:%02u'%(dt_local.hour, dt_local.minute, dt_local.second))
		print('UTC    : %02u:%02u:%02u'%(dt_utc.hour, dt_utc.minute, dt_utc.second))
		print('SIDERAL: %02u:%02u:%02u'%dt_sid.hms)
		
	def do_ra(self, arg):
		"""
		Move along the RA axis
		> ra [+-]
		"""
		logger.error('Not implemented yet')

	def do_dec(self, arg):
		"""
		Move along the DEC axis
		> dec [+-]
		"""
		logger.error('Not implemented yet')
    
	def do_goto(self, arg):
		"""
		Define goto position with SAO number or RA-DEC coordinates
		> goto [sao radec]
		"""
		arg = arg.split()
		if len(arg)==1:
			sao = int(arg[0])
			star = None
			for s in self.catalog:
				if s.sao == sao:
					star = s
			if star is None:
				logger.error('Star SAO=%s is not in the catalog'%sao)
			else:
				alt,_ = star.altaz(self.mount.longitude, self.mount.latitude)
				if alt<0:
					logger.error('Star SAO=%s is below the horizon'%sao)
				else:
					logger.info('Goto SAO %u (%s)'%(star.sao,star.name))
					ha_degree = self.mount.complementary_angle(star.ra).ra_degree
					self.do_stop('')
					self.synscan.set_goto_target(1, ha_degree/360)
					self.do_mode('1 goto') # automatically set GOTO mode
					self.synscan.set_goto_target(2, star.dec_degree/360)
					self.do_mode('2 goto') # automatically set GOTO mode
					self.do_status(None) # also show status
		else:
			logger.error('Not implemented yet')
					
	
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
			self.synscan.stop_motion(axnb)
		except:
			logger.warning('Cannot get axis number')
			
	def do_mode(self, arg):
		"""
		Define axis motion mode
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
			
	def do_exit(self, arg):
		"""
		Exit the command line interpreter
		> exit
        """
		return True

					
			
