"""
Open serial port with mount.

General comment:
The mount saves and returns the declination and hour angle coordinates.
"""

import serial.tools.list_ports
from serial import Serial, PARITY_NONE
import time
from astrocom import logger, AstrocomError, AstrocomSuccess
from astrocom.astro import SIDERAL_DAY_SEC, RaDec

### CONSTANTS
class SWCMD:
	GET_CPR = 'a'
	GET_TIF = 'b'
	SET_POSITION = 'E'
	GET_MOTOR_BOARD_VERSION = 'e'
	INIT_MOTOR = 'F'
	GET_AXIS_STATUS = 'f'
	GET_AXIS_POSITION = 'j'
	SET_MOTION_MODE = 'G'
	GET_GOTO_POSITION = 'h'
	SET_STEP_PERIOD = 'I'
	GET_STEP_PERIOD = 'i'
	START_MOTION = 'J'
	STOP_MOTION = 'K'
	STOP_MOTION_NOW = 'L'
	SET_AUTOGUIDE_RATE = 'P'
	SET_GOTO_TARGET = 'S'
	SET_LED_BRIGHTNESS = 'V'
	GET_HIGH_SPEED_RATIO = 'g'
    
SW_ERROR = {
'0':'UNKNOWN_COMMAND',
'1':'INVALID_COMMAND_LENGTH',
'2':'MOTOR_RUNNING',
'3':'INVALID_CHARACTER',
'4':'NOT_INITIALIZED',
'5':'DRIVER_ASLEEP',
'6':'MOUNT_NOT_TRACKING',
'7':'PEC_RUNNING',
'8':'INVALID_PEC_DATA',
'9':'INVALID_CMD'}

SW_MODE = {
'FORWARD':0,
'BACKWARD':1,
'NORTH':0,
'SOUTH':1,
'GOTO':0,
'TRACK':1,
'SLOW':0,
'FAST':1}

SW_POS_MAXI = int("F"*6,16) / 2.0
SW_POS_OFFSET = int("800000",16)
SW_POS_STEP = 1.0 / SW_POS_MAXI

TIMEOUT = 0.5 # second

### FUNCTIONS
def list_ports():
	"""Get list of serial ports"""
	return serial.tools.list_ports.comports()
	
	
def print_ports():
	"""Print the list of serial ports"""
	for p in list_ports():
		print(p.device)
		print(p.product)
		print(p.manufacturer)
		print()
    

def has_error(strng):
	"""Check if the string is valid or not (empty or includes error pattern)"""
	if type(strng) is AstrocomError:
		return True
	if len(strng)==0:
		return True
	if '!' in strng:
		return True
	return False


def error_to_str(strng):
	"""Decode error to human format"""
	if type(strng) is AstrocomError:
		return 'ASTROCOM_ERROR'
	if len(strng)==0:
		return 'EMPTY_ANSWER'
	error_code = strng[1:]
	if error_code in SW_ERROR.keys():
		return SW_ERROR[error_code]
	else:
		return 'UNKNOWN_ERROR'


def axis_status_to_dict(strng):
	"""Convert axis status to dictionary"""
	bt = bytes(strng,'utf8')
	status = {}
	status['STOP'] = (bt[2] & 0x01) == 0
	status['TRACK'] = (bt[1] & 0x01) != 0
	status['GOTO'] = not status['TRACK']
	status['FORWARD'] = (bt[1] & 0x02) == 0
	status['BACKWARD'] = not status['FORWARD']
	status['FAST'] = (bt[1] & 0x04) != 0
	status['SLOW'] = not status['FAST']
	status['INIT'] = (bt[3] & 1) == 1
	return status


def axis_dict_to_str(dic):
	"""Convert axis status dictionary to a one-line string"""
	ans = ""
	if not dic['INIT']:
		return 'NOT-INITIALIZED'
	if dic['STOP']:
		ans += '%7s'%'STOP'
	else:
		ans += '%7s'%'MOVING'
	for k in ['TRACK','GOTO']:
		if dic[k]:
			ans += '%6s'%k
	if dic['FORWARD']:
		ans += '%7s'%'FORWRD'
	else:
		ans += '%7s'%'BCKWRD'
	if dic['FAST']:
		ans += '%6s'%'FAST'
	else:
		ans += '%6s'%'SLOW'
	return ans


def hexa_response_to_int(res):
	"""Convert an hexadecimal response to an integer"""
	if len(res) == 6:
		descramble = res[4] + res[5] + res[2] + res[3] + res[0] + res[1]
	elif len(res) == 4:
		descramble = res[2] + res[3] + res[0] + res[1]
	elif len(res) == 2:
		descramble = res[0] + res[1]
	else:
		return AstrocomError('Uncompatible length to decode hexadecimal <%s>'%res)
	return int(descramble, 16)


def int_to_hexa_cmd(value_int):
	"""Convert an integer to an hexadecimal command"""
	hexa = hex(value_int)[2:].upper()
	hexa = "0"*(6-len(hexa)) + hexa
	return hexa[4] + hexa[5] + hexa[2] + hexa[3] + hexa[0] + hexa[1]


def position_to_turn_ratio(pos):
	"""
	Convert a mount position string to a turn ratio [-1,+1].
	hexa=0x123456 -> pos=563412
	"""
	try:
		ans = (hexa_response_to_int(pos) - SW_POS_OFFSET) / SW_POS_MAXI
		return ans
	except:
		return AstrocomError('Cannot convert %s from hexadecimal to decimal'%pos)


def turn_ratio_to_position(ratio):
	"""
	Convert turn ratio [-1,+1] to a position string for mount.
	hexa=0x123456 -> pos=563412
	"""
	ratio = (ratio+1)%2 - 1   # make sure ratio between [-1,1]
	return int_to_hexa_cmd(int(round(ratio*SW_POS_MAXI + SW_POS_OFFSET)))


def gimbal_lock(dec_ratio):
	"""Return True if position is close to gimbal lock"""
	return abs(abs(dec_ratio) - 0.25) < SW_POS_STEP


### CLASS
class MountSW(Serial):
	
	### BASIC READ and WRITE FUNCTIONS
	def __init__(self, portname):
		"""Init a MountSW serial port"""
		super().__init__(port=portname, baudrate=9600, parity=PARITY_NONE, stopbits=1, timeout=TIMEOUT)
		if not self.is_open:
			self.open()
		self.flushInput()
		self.flushOutput()
		
		for k in SW_MODE.keys():
			setattr(self, k, SW_MODE[k])
			
		# Assume North for now, but needs to be updated by user !
		self._north_south = self.NORTH
		
		# Define home position: (HA = 18h, DEC = 90°)
		# When HA init and set DEC<90°, the mount looks towards East
		self.home_position = RaDec('18:00', '90°00')
		
	@property
	def north_south(self):
		return self._north_south
		
	@north_south.setter
	def north_south(self, value):
		if value == self.NORTH:
			self.home_position.dec = '90°00'
		else:
			self.home_position.dec = '-90°00'
		self._north_south = value

	def __del__(self):
		"""Delete instance, but try to close port before"""
		try:
			ans = self.stop_motion_now(3)
			if type(ans) is not AstrocomError:
				AstrocomSuccess('Motors have been stopped')
			else:
				AstrocomError('Could not stop motors')
		except:
			AstrocomError('Could not stop motors')
		try:
			self.close()
			AstrocomSuccess('Port has been closed')
		except:
			AstrocomError('Port closing encountered an error')
			
	def write(self, strng):
		"""Write a string into the serial port"""
		super().write(bytes(':'+strng+'\r','utf8'))
		
	def read(self):
		"""
		Get a string from the serial port.
		Ending character is chr(13) = \ r
		"""
		ans = bytearray()
		t0 = time.time()
		t1 = time.time()
		stop = False
		while not stop: 
		    ans += super().read()
		    t1 = time.time()
		    if (t1-t0)>TIMEOUT:
		        stop = True
		    if len(ans)>0:
		        if ans[-1] == 13: # chr(13) == b'\r'
		            stop = True
		try:
			ans = ans.decode('utf8')
			return ans
		except:
			return AstrocomError('Could not decode data')
	
	def send_cmd(self, cmd_letter, axis_int, cmd_string='', retry=2):
		"""
		Send a command to the mount and read response.
		Return the mount string or AstrocomError.
		"""
		if (type(cmd_letter)!=str) or (type(axis_int)!=int) or (type(cmd_string)!=str):
			return AstrocomError('WRONG_INPUT_TYPE')
		if axis_int in [1,2,3]: # 3=both
		    self.write(cmd_letter+str(axis_int)+cmd_string)
		    ans = self.read()
		    if has_error(ans) and (retry>0):
		    	ans = self.send_cmd(cmd_letter, axis_int, cmd_string=cmd_string, retry=retry-1)
		    if has_error(ans) and (retry==0):
		    	return AstrocomError(error_to_str(ans))
		    return ans
		else:
		    return AstrocomError('INVALID_AXIS_ID')
	
	def send_cmd_hexa_ans(self, *args, **kwargs):
		"""Send a command and decode an hexadecimal answer"""
		ans = self.send_cmd(*args, **kwargs)
		if type(ans) is AstrocomError:
			return ans
		return hexa_response_to_int(ans[1:-1])
		
	def send_cmd_ratio_ans(self, *args, **kwargs):
		"""Send a command and decode a ratio answer"""
		ans = self.send_cmd(*args, **kwargs)
		if type(ans) is AstrocomError:
			return ans
		return position_to_turn_ratio(ans[1:-1])
	
	### SKY-WATCHER BASIC FUNCTIONS (END-USER SHOULD REFRAIN USING THEM)
	def set_motion_mode(self, axis, goto_or_track, speed, direction):
		"""Set motion mode"""
		if goto_or_track == self.GOTO:
			speed = 1 - speed # in GOTO mode, FAST and SLOW are inverted
		return self.send_cmd(SWCMD.SET_MOTION_MODE, axis, str(2*speed+goto_or_track)+str(2*self.north_south+direction))

	def init_motor(self, axis):
		"""Initialize motor"""
		return self.send_cmd(SWCMD.INIT_MOTOR, axis)
		
	def get_cpr(self, axis):
		"""Get Counts Per Revolution"""
		return self.send_cmd_hexa_ans(SWCMD.GET_CPR, axis)
		
	def get_tif(self, axis):
		"""Get Timer Interrupt Frequency"""
		return self.send_cmd_hexa_ans(SWCMD.GET_TIF, axis)
		
	def get_step_period(self, axis):
		"""Get step period"""
		return self.send_cmd_hexa_ans(SWCMD.GET_STEP_PERIOD, axis)
		
	def set_step_period(self, axis, value_int):
		"""Set step period"""
		value_hexa = int_to_hexa_cmd(value_int)
		return self.send_cmd(SWCMD.SET_STEP_PERIOD, axis, value_hexa)
		
	def get_axis_position(self, axis):
		"""Get axis position as ratio of turn"""
		return self.send_cmd_ratio_ans(SWCMD.GET_AXIS_POSITION, axis)
	
	def set_axis_position(self, axis, ratio):
		"""Set axis position from a turn ratio"""
		pos = turn_ratio_to_position(ratio)
		return self.send_cmd(SWCMD.SET_POSITION, axis, pos)
	
	def set_goto_target(self, axis, ratio):
		"""Set goto target from a turn ratio"""
		pos = turn_ratio_to_position(ratio)
		return self.send_cmd(SWCMD.SET_GOTO_TARGET, axis, pos)
	
	def get_goto_target(self, axis):
		"""Get the goto target as turn ratio"""
		return self.send_cmd_ratio_ans(SWCMD.GET_GOTO_POSITION, axis)
	
	def get_axis_status(self, axis):
		"""Get axis status"""
		return self.send_cmd(SWCMD.GET_AXIS_STATUS, axis)
		
	def get_axis_status_as_dict(self, axis):
		"""Get axis status as dictionary"""
		ans = self.get_axis_status(axis)
		if type(ans) is AstrocomError:
			return ans
		return axis_status_to_dict(ans)
	
	def get_axis_status_speed(self, axis):
		"""Get status speed SLOW or FAST"""
		dic = self.get_axis_status_as_dict(axis)
		if type(dic) is AstrocomError:
			return dic
		return dic['FAST']*self.FAST + dic['SLOW']*self.SLOW
		
	def get_axis_status_mode(self, axis):
		"""Get status mode TRACK or GOTO"""
		dic = self.get_axis_status_as_dict(axis)
		if type(dic) is AstrocomError:
			return dic
		return dic['GOTO']*self.GOTO + dic['TRACK']*self.TRACK
		
	def get_axis_status_direction(self, axis):
		"""Get status direction FORWARD or BACKWARD"""
		dic = self.get_axis_status_as_dict(axis)
		if type(dic) is AstrocomError:
			return dic
		return dic['FORWARD']*self.FORWARD + dic['BACKWARD']*self.BACKWARD
	
	def get_axis_status_as_str(self, axis):
		"""Get axis status as a string to print"""
		dic = self.get_axis_status_as_dict(axis)
		if type(dic) is AstrocomError:
			return dic
		return axis_dict_to_str(dic)
	
	def get_motor_board_version(self, axis):
		"""Get motor board version"""
		return self.send_cmd_hexa_ans(SWCMD.GET_MOTOR_BOARD_VERSION, axis)
	
	def start_motion(self, axis):
		"""Start motion"""
		return self.send_cmd(SWCMD.START_MOTION, axis)

	def stop_motion(self, axis):
		"""Stop motion"""
		return self.send_cmd(SWCMD.STOP_MOTION, axis)
		
	def stop_motion_now(self, axis):
		"""Instantaneously stop motion"""
		return self.send_cmd(SWCMD.STOP_MOTION_NOW, axis)

	def set_autoguide_rate(self, axis, rate):
		"""Set rate [0:4] <=> [1.0, 0.75, 0.50, 0.25, 0.125]"""
		return self.send_cmd(SWCMD.SET_AUTOGUIDE_RATE, axis, str(rate))
		
	def get_high_speed_ratio(self, axis):
		"""Get high speed ratio"""
		return self.send_cmd_hexa_ans(SWCMD.GET_HIGH_SPEED_RATIO, axis)
		
	### END-USER FUNCTIONS (SAFE TO ACCESS)
	def init_mount(self):
		"""Initialize the mount"""
		ans1 = self.init_motor(1)
		ans2 = self.init_motor(2)
		if not AstrocomError in [type(ans1),type(ans2)]:
			north = self.north_south==self.NORTH
			logger.info('Assume looking at the celestial pole at startup')
			self.set_axis_position(1, self.home_position.ra_degree/360)
			self.set_axis_position(2, self.home_position.dec_degree/360)
			return AstrocomSuccess('Motors correctly initialized')
		else:
			return AstrocomError('Could not initialize motors')
	
	def get_position(self):
		"""Get current mount position (as fraction of turn)"""
		ra_ratio = self.get_axis_position(1)
		dec_ratio = self.get_axis_position(2)
		if gimbal_lock(dec_ratio):
			logger.info('RA poorly determined close to the Pole')
		return ra_ratio, dec_ratio
		
	def get_goto(self):
		"""Get current goto target (as fraction of turn)"""
		ra_ratio = self.get_goto_target(1)
		dec_ratio = self.get_goto_target(2)
		return ra_ratio, dec_ratio
	
	def stop(self, axis):
		"""Stop motion on one or both motors"""
		ans = self.stop_motion(axis)
		if type(ans) is AstrocomError:
			return ans
		else:
			return AstrocomSuccess('Motor correctly stopped')
	
	def start(self, axis):
		"""Start motion on one or both motors"""
		ans = self.start_motion(axis)
		if type(ans) is AstrocomError:
			return ans
		else:
			return AstrocomSuccess('Motor started')
	
	def goto(self, ra_ratio, dec_ratio):
		"""Stop motors and set a goto target (as fraction of turn)"""
		ans = self.stop_motion(3)
		if type(ans) is AstrocomError:
			return ans
		if (ra_ratio%1) < 0.5: # looking West
			logger.info('Work in progress for stars at West')
			ra_ratio = (ra_ratio%1) - 0.5
			dec_ratio = 2*self.home_position.dec_degree/360 - dec_ratio
		self.set_goto_target(1, ra_ratio)
		self.set_goto_target(2, dec_ratio)
		for axis in [1,2]:
			speed = self.get_axis_status_speed(axis)
			direction = self.get_axis_status_direction(axis)
			ans = self.set_motion_mode(axis, self.GOTO, speed, direction)
			if type(ans) is AstrocomError:
				return ans
		return AstrocomSuccess('Goto correctly defined')
	
	def goto_home(self):
		"""Goto home position"""
		return self.goto(self.home_position.ra_degree/360, self.home_position.dec_degree/360)
	
	def track(self):
		"""Start sideral tracking"""
		ans = self.stop_motion(3)
		if type(ans) is AstrocomError:
			return ans
		for axis in [1,2]:
			ans = self.set_motion_mode(axis, self.TRACK, self.SLOW, self.FORWARD)
			if type(ans) is AstrocomError:
				return ans
		self.start_motion(1)
		return AstrocomSuccess('Start tracking')
	
	def get_rotation_speed(self, axis):
		"""Get rotation speed (deg/sec)"""
		cpr = self.get_cpr(axis)
		tif = self.get_tif(axis)
		step = self.get_step_period(axis)
		if AstrocomError in [type(cpr),type(tif),type(step)]:
			return AstrocomError('Could not get CPR, TIF or STEP')
		return tif*360/step/cpr
		
	def set_sideral_speed(self):
		"""Set sideral speed on the Right-Ascension axis"""
		axis = 1
		cpr = self.get_cpr(axis)
		tif = self.get_tif(axis)
		if AstrocomError in [type(cpr),type(tif)]:
			return AstrocomError('Could not get CPR or TIF')
		step = int(round(SIDERAL_DAY_SEC*tif/cpr))
		return self.set_step_period(axis, step)
		
