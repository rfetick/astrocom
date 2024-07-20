"""
Astronomical computations
"""

import datetime
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astropy import units as _u
from astropy.utils.iers import conf as _iers_config


def longitude_to_sideraltime(longitude_deg):
    """Get the current sideral time from a longitude [degree]"""
    _iers_config.auto_max_age = None # remove error when too old IERS data
    observ_loc = EarthLocation(lat=0*_u.deg, lon=longitude_deg*_u.deg)
    observ_time = Time(datetime.datetime.utcnow(), scale='utc', location=observ_loc)
    return observ_time.sidereal_time('apparent')


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


def dms_to_deg(tpl):
    """Convert a tuple (deg, arcmin, arcsec) to degree value"""
    if len(tpl)!=3:
        raise ValueError('Tuple must contain 3 elements (deg, arcmin, arcsec).')
    degree = abs(tpl[0]) + tpl[1]/60 + tpl[2]/3600
    positive = tpl[0] >= 0
    return positive*degree - (not positive)*degree
