"""
Test connection to a mount
"""

from astrocom.serialport import list_ports, MountSW

#%% PARAMETERS TO MODIFY
productname = 'EQDIR Stick' # USB product name

#%% FIND USB PORT and RUN COMMAND LINE INTERFACE
port_found = False

for pp in list_ports():
	if pp.product==productname:
		port_found = True
		portname = pp.device
		print('Initialize mount on %s'%portname)
		mount = MountSW(portname)
		print('Motor version: %u'%mount.get_motor_board_version(1))
		print('High speed ratio: %s'%mount.get_high_speed_ratio(1))
		print('Speed: %.3f °/h'%(3600*mount.get_rotation_speed(1)))
		
if not port_found:
	print('Did not find any port matching <%s>'%productname)
