"""
Basic script to list ports and open command line interface
"""

from astrocom.command import MountCmd
from astrocom.serialport import list_ports

#%% PARAMETERS TO MODIFY
productname = 'EQDIR Stick' # USB product name
latitude = (43,36,15) # (sign*degree, arcmin, arcsec)
longitude = (1,26,37) # (sign*degree, arcmin, arcsec) 

#%% FIND USB PORT and RUN COMMAND LINE INTERFACE
port_found = False

for pp in list_ports():
	if pp.product==productname:
		port_found = True
		portname = pp.device
		print('Initialize mount on %s'%portname)
		mcmd = MountCmd(portname, longitude, latitude)
		mcmd.cmdloop()
		
if not port_found:
	print('Did not find any port matching <%s>'%productname)
