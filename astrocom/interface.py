"""
User interface: command line (CLI) or graphical (GUI)
"""

import cmd
import datetime
import tkinter as tk
from tkinter import ttk
from astrocom import AstrocomError
from astrocom.astro import read_bsc, cardinal_point, MountPosition, RaDec, print_catalog, catalog_brightest
from astrocom.serialport import MountSW

#############################################
###        COMMAND LINE INTERFACE
#############################################

class MountCLI(cmd.Cmd):
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
			arg = ['15']
		print_catalog(self.catalog, int(arg[0]), self.mount_position.latitude, self.mount_position.longitude, bicolor=True)
        
	def do_init(self, _):
		"""
		Initialize motors
		> init
		"""
		try:
			self.mount_serial.init_mount()
		except AstrocomError:
			pass
		else:
			self.do_status(None)
		
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
		Start fast moving along the RA axis
		> ra [speed]
		"""
		arg = arg.split()
		try:
			self.mount_serial.move_ra(int(arg[0]))
		except AstrocomError:
			pass

	def do_dec(self, arg):
		"""
		Start fast moving along the DEC axis
		> dec [speed]
		"""
		arg = arg.split()
		try:
			self.mount_serial.move_dec(int(arg[0]))
		except AstrocomError:
			pass
		
	def do_track(self, _):
		"""
		Start sideral tracking
		> track
		"""
		try:
			self.mount_serial.track()
		except AstrocomError:
			pass
		
	def do_status(self, _):
		"""
		Print status and position of motors
		> status
		"""
		try:
			status_1 = self.mount_serial.get_axis_status_as_str(1)
			status_2 = self.mount_serial.get_axis_status_as_str(2)
			pos = self.mount_position.telescope_to_radec(self.mount_serial.get_position())
			goto = self.mount_position.telescope_to_radec(self.mount_serial.get_goto())
			print("AXIS POSITION      GOTO  MOVING  MODE    DIR SPEED")
			print("""RA   %s  %s %s"""%(pos.ra_str, goto.ra_str, status_1.lower()))
			print("""DEC %s %s %s"""%(pos.dec_str, goto.dec_str, status_2.lower()))
		except AstrocomError:
			pass
    
	def do_set(self, arg):
		"""
		Set current position
		> set [name ra dec]
		"""
		arg = arg.split()
		try:
			if len(arg)==1:
				name = arg[0]
				if name.lower() == 'home':
					star = RaDec(0,0)
				for s in self.catalog:
					if name.lower() in ['hr%u'%s.hr, s.name.lower()]:
						star = s
						break
				if star is None:
					raise AstrocomError('Star <%s> is not in the catalog'%name)
				alt,_ = star.altaz(self.mount_position.latitude, self.mount_position.longitude)
			elif len(arg)==2:
				star = RaDec(arg[0], arg[1])
			else:
				raise AstrocomError('Set does not accept more than 2 elements')
			self.mount_serial.set_position(*self.mount_position.radec_to_telescope(star))
			self.do_status(None)
		except AstrocomError:
			pass
    
	def do_goto(self, arg):
		"""
		Define goto position (home, HR number, star name or RA-DEC)
		> goto [hrXXXX name ra dec]
		"""
		arg = arg.split()
		try:
			if len(arg)==1:
				name = arg[0]
				if name.lower() == 'home':
					self.mount_serial.goto_home()
					self.do_status(None)
					return
				star = None
				for s in self.catalog:
					if name.lower() in ['hr%u'%s.hr, s.name.lower()]:
						star = s
						break
				if star is None:
					raise AstrocomError('Star <%s> is not in the catalog'%name)
				alt,_ = star.altaz(self.mount_position.latitude, self.mount_position.longitude)
				if alt<0:
					raise AstrocomError('Star <%s> is below the horizon'%name)
			elif len(arg)==2:
				star = RaDec(arg[0], arg[1])
			else:
				raise AstrocomError('Goto does not accept more than 2 elements')
			self.mount_serial.goto(*self.mount_position.radec_to_telescope(star))
			self.do_status(None)
		except AstrocomError:
			pass
					
	def do_start(self, axnb):
		"""
		Start moving on one or both axis
		> start [axis]
		"""
		if len(axnb)==0:
			 axnb = '3' # both axis if nothing provided
		axnb = int(axnb)
		try:
			self.mount_serial.start(axnb)
		except AstrocomError:
			pass
	
	def do_stop(self, axnb):
		"""
		Stop moving on one or both axis
		> stop [axis]
		"""
		if len(axnb)==0:
			axnb = '3' # both axis if nothing provided
		axnb = int(axnb)
		try:
			self.mount_serial.stop(axnb)
		except AstrocomError:
			pass
			
	def do_exit(self, arg):
		"""
		Exit the command line interpreter
		> exit
        """
		return True




#############################################
###        GRAPHICAL USER INTERFACE
#############################################

class MountGUI:
	def __init__(self, portname, longitude, latitude):
		self.catalog = read_bsc()
		self.mount_position = MountPosition(longitude, latitude)
		self.mount_serial = MountSW(portname)
		if latitude[0]>=0:
			self.mount_serial.north_south = self.mount_serial.NORTH
		else:
			self.mount_serial.north_south = self.mount_serial.SOUTH
		
		
		BCK_COLOR = '#8B8378'
		L0_COLOR = '#CDC0B0'
		L1_COLOR = '#EEDFCC'
		TXT_COLOR = 'white'
		
		root = tk.Tk()
		root.title("ASTROCOM")
		root.geometry("600x550+50+50")
		root.configure(bg=BCK_COLOR)

		# Create a style with smaller padding (reduced height)
		style = ttk.Style()
		style.configure("Small.TButton", padding=(1, 0))   # (x-padding, y-padding)
		
		style_bg = ttk.Style()
		style_bg.configure("Blue.TFrame", background=BCK_COLOR)
		
		# --- Configure grid ---
		root.columnconfigure(0, weight=1)
		root.columnconfigure(1, weight=1)
		root.rowconfigure(0, weight=0)
		root.rowconfigure(1, weight=1)
		root.rowconfigure(2, weight=0)
		
		# Define actions
		def status():
			dt_local = datetime.datetime.now()
			dt_utc = dt_local.utcnow()
			dt_sid = self.mount_position.sideral_time
			string =         'LOCAL      %02u:%02u:%02u'%(dt_local.hour, dt_local.minute, dt_local.second)
			string += '\n' + 'UTC          %02u:%02u:%02u'%(dt_utc.hour, dt_utc.minute, dt_utc.second)
			string += '\n' + 'SIDERAL   %02u:%02u:%02u'%dt_sid.hms
			string += '\n\n' + "AXIS POSITION      GOTO  MOVING  MODE    DIR SPEED"
			try:
				status_1 = self.mount_serial.get_axis_status_as_str(1)
				status_2 = self.mount_serial.get_axis_status_as_str(2)
				position_1, position_2 = self.mount_serial.get_position()
				goto_1, goto_2 = self.mount_serial.get_goto()
				
				self.mount_position.hour_angle = 360*position_1 # degree
				goto_1_str = self.mount_position.complementary_angle(360*goto_1).ra_str
				string += '\n' + """RA   %s  %s    %s"""%(self.mount_position.ra_str, goto_1_str, status_1.lower())
				self.mount_position.dec = 360*position_2
				goto_2_str = RaDec(0, 360*goto_2).dec_str
				string += '\n' + """DEC %s %s     %s"""%(self.mount_position.dec_str, goto_2_str, status_2.lower())
					
			except (AstrocomError,ValueError):
				string += '\nRA  %15s\nDEC %15s'%('error','error')
			lbl_status.config(text=string)
			lbl_status.after(1000, status)
			
		def bsc():
			bright = catalog_brightest(self.catalog, len(lbl_bsc), self.mount_position.latitude, self.mount_position.longitude)
			for i in range(len(lbl_bsc)):
				lbl_bsc[i].config(text='%s'%bright[i])
			lbl_bsc[0].after(30*1000, bsc)
			
		
		def init():
			try:
				self.mount_serial.init_mount()
			except AstrocomError:
				pass
			else:
				pass
				
			
		def track():
			try:
				self.mount_serial.track()
			except AstrocomError:
				pass
			
		def stop():
			try:
				self.mount_serial.stop(3) # both axis
			except AstrocomError:
				pass
		
		def goto():
			pass
		
		# -------------------- Init/Track/Stop --------------------
		top_left_frame = ttk.Frame(root, style="Blue.TFrame")
		top_left_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

		btn_init = ttk.Button(top_left_frame, text="Init", command=init)
		btn_track = ttk.Button(top_left_frame, text="Track", command=track)
		btn_stop = ttk.Button(top_left_frame, text="Stop", command=stop)

		btn_init.grid(row=0, column=0, padx=5)
		btn_track.grid(row=0, column=1, padx=5)
		btn_stop.grid(row=0, column=2, padx=5)

		# -------------------- Direction Buttons (Cross Layout) --------------------
		dpad_frame = ttk.Frame(root, style="Blue.TFrame")
		dpad_frame.grid(row=0, column=1, sticky="n", pady=5)

		ttk.Button(dpad_frame, text="DEC +", width=5).grid(row=0, column=1, pady=2, ipady=5)
		ttk.Button(dpad_frame, text="RA -", width=5).grid(row=1, column=0, padx=2, ipady=5)
		ttk.Button(dpad_frame, text="RA +", width=5).grid(row=1, column=2, padx=2, ipady=5)
		ttk.Button(dpad_frame, text="DEC -", width=5).grid(row=2, column=1, pady=2, ipady=5)

		# -------------------- Middle Area Frames --------------------
		middle_left_frame = ttk.Frame(root, style="Blue.TFrame")
		middle_left_frame.grid(row=1, column=0, sticky="nw", padx=10, pady=10)

		middle_right_frame = ttk.Frame(root, style="Blue.TFrame")
		middle_right_frame.grid(row=1, column=1, sticky="ne", padx=10, pady=10)

		# -------------------- Star labels and buttons --------------------
		def make_handler(n):
			return lambda: print(f"Button {n} pressed")
		
		lbl_bsc = []
		for i in range(10):
			lbl = ttk.Label(middle_left_frame, text="", background=[L0_COLOR,L1_COLOR][i%2], justify='left', width=45)
			lbl.grid(row=i, column=0, sticky="w", ipady=2)
			lbl_bsc += [lbl]
			
			b = ttk.Button(middle_right_frame, text=f"Goto {i+1}",
				command=make_handler(i+1), style="Small.TButton")
			b.grid(row=i, column=0, sticky="e", pady=1)

		# -------------------- Time label --------------------
		lower_middle_frame = ttk.Frame(root)
		lower_middle_frame.grid(row=2, column=0, columnspan=2, pady=10)

		lbl_status = ttk.Label(lower_middle_frame, text="", font=('calibri', 12, 'bold'), background=BCK_COLOR, foreground=TXT_COLOR, justify='left')
		lbl_status.pack()
		
		### START GUI ###
		bsc() # first call to BSC
		status() # first call to status
		root.mainloop()

