"""
Astronomical computations
"""

def turn_to_hms(value):
	"""Convert percentage of turn to (hh,mm,ss) tuple"""
	hh = int(24*value)
	mm = int(60*24*value - 60*hh)
	ss = int(3600*24*value - 3600*hh - 60*mm)
	return (hh,mm,ss)
	
	
def turn_to_dms(value):
	"""Convert percentage of turn to (degree,arcmin,arcsec) tuple"""
	dd = int(360*value)
	mm = int(60*360*value - 60*dd)
	ss = int(3600*360*value - 3600*dd - 60*mm)
	return (dd,mm,ss)
