"""
Basic script to list ports and open command line interface
"""

from astrocom.command import MountCmd
from astrocom.serialport import list_ports

productname = 'EQDIR Stick'
port_found = False

for pp in list_ports():
	if pp.product==productname:
		port_found = True
		portname = pp.device
		mcmd = MountCmd(portname)
		mcmd.synscan.north_south = mcmd.synscan.NORTH # set North hemisphere
		mcmd.cmdloop()
		
if not port_found:
	print('Did not find any port matching <%s>'%productname)
