"""
Basic script to list ports and open command line interface
"""

from command import MountCmd
from serialport import list_ports

for pp in list_ports():
	if pp.product=='EQDIR Stick':
		portname = pp.device
		mcmd = MountCmd(portname)
		mcmd.synscan.north_south = mcmd.synscan.NORTH # set North hemisphere
		mcmd.cmdloop()
		
