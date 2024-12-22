"""
Command line interface
"""

import cmd
import datetime
from astrocom import AstrocomError
from astrocom.astro import read_bsc, cardinal_point, MountPosition, RaDec, print_catalog
from astrocom.serialport import MountSW

class MountCmd(cmd.Cmd):
	intro = "\n".join(("","="*35,"Welcome to the ASTROCOM command line.","Type help or ? to list commands.","="*35,""))
	prompt = "(astrocom) "
	
	def __init__(self, portname, longitude, latitude):
		super().__init__()
		self.catalog = read_bsc()
		self.mount_position = MountPosition(longitude, latitude)
		self.mount_serial = MountSW(portname)
		if latitude[0]>=0:
			self.mount_serial.north_south = self.mount_serial.NORTH
		else:
			self.mount_serial.north_south = self.mount_serial.SOUTH
	
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
			fill = max(30-len(doc_lines[2]),1)
			print(doc_lines[2] + ' '*fill + doc_lines[1])
        
	def do_bsc(self, arg):
		"""
		Print visible stars of the Bright Star Catalog
		> bsc [nb]
        """
		arg = arg.split()
		if len(arg)==0:
			arg = ['10']
		print_catalog(self.catalog, int(arg[0]), self.mount_position.latitude, self.mount_position.longitude)
        
	def do_init(self, _):
		"""
		Initialize motors
		> init
		"""
		ans = self.mount_serial.init_mount()
		if type(ans) is not AstrocomError:
			self.do_status(_)
		
	def do_track(self, _):
		"""
		Start sideral tracking
		> track
		"""
		self.mount_serial.track()
		
	def do_status(self, _):
		"""
		Print status and position of motors
		> status
		"""
		status_1 = self.mount_serial.get_axis_status_as_str(1)
		status_2 = self.mount_serial.get_axis_status_as_str(2)
		position_1, position_2 = self.mount_serial.get_position()
		goto_1, goto_2 = self.mount_serial.get_goto()
		print("AXIS POSITION      GOTO  MOVING  MODE    DIR SPEED")
		if AstrocomError not in [type(status_1), type(position_1), type(goto_1)]:
			self.mount_position.hour_angle = 360*position_1 # degree
			goto_1_str = self.mount_position.complementary_angle(360*goto_1).ra_str
			print("""RA   %s  %s %s"""%(self.mount_position.ra_str, goto_1_str, status_1.lower()))
		if AstrocomError not in [type(status_2), type(position_2), type(goto_2)]:
			self.mount_position.dec = 360*position_2
			goto_2_str = RaDec(0, 360*goto_2).dec_str
			print("""DEC %s %s %s"""%(self.mount_position.dec_str, goto_2_str, status_2.lower()))
	
	def do_time(self, arg):
		"""
		Print current time
		> time
		"""
		dt_local = datetime.datetime.now()
		dt_utc = dt_local.utcnow()
		dt_sid = self.mount_position.sideral_time
		print('LOCAL  : %02u:%02u:%02u'%(dt_local.hour, dt_local.minute, dt_local.second))
		print('UTC    : %02u:%02u:%02u'%(dt_utc.hour, dt_utc.minute, dt_utc.second))
		print('SIDERAL: %02u:%02u:%02u'%dt_sid.hms)
		
	def do_ra(self, arg):
		"""
		Step move along the RA axis
		> ra [arcmin]
		"""
		AstrocomError('Not implemented yet')

	def do_dec(self, arg):
		"""
		Step move along the DEC axis
		> dec [arcmin]
		"""
		AstrocomError('Not implemented yet')
    
	def do_goto(self, arg):
		"""
		Define goto position with HR number, star name or RA-DEC coord
		> goto [hrXXXX name ra dec]
		"""
		arg = arg.split()
		if len(arg)==1:
			name = arg[0]
			star = None
			for s in self.catalog:
				if name.lower() in ['hr%u'%s.hr, s.name.lower()]:
					star = s
					break
			if star is None:
				AstrocomError('Star <%s> is not in the catalog'%name)
			else:
				alt,_ = star.altaz(self.mount_position.latitude, self.mount_position.longitude)
				if alt<0:
					AstrocomError('Star <%s> is below the horizon'%name)
				else:
					ha_degree = self.mount_position.complementary_angle(star.ra).ra_degree
					self.mount_serial.goto(ha_degree/360, star.dec_degree/360)
					self.do_status(None)
		elif len(arg)==2:
			star = RaDec(arg[0], arg[1])
			ha_degree = self.mount_position.complementary_angle(star.ra).ra_degree
			self.mount_serial.goto(ha_degree/360, star.dec_degree/360)
			self.do_status(None)
		else:
			AstrocomError('Goto does not accept more than 2 elements')
					
	def do_start(self, axnb):
		"""
		Start moving on one or both axis
		> start [axis]
		"""
		if len(axnb)==0:
			 axnb = '3' # both axis if nothing provided
		axnb = int(axnb)
		self.mount_serial.start(axnb)
	
	def do_stop(self, axnb):
		"""
		Stop moving on one or both axis
		> stop [axis]
		"""
		if len(axnb)==0:
			axnb = '3' # both axis if nothing provided
		axnb = int(axnb)
		self.mount_serial.stop(axnb)
			
	def do_exit(self, arg):
		"""
		Exit the command line interpreter
		> exit
        """
		return True
		
