"""
Astronomical computations
"""

import datetime
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astropy import units as _u
from astropy.utils.iers import conf as _iers_config

SIDERAL_DAY_SEC = 23*3600 + 56*60 + 4.09
SOLAR_DAY_SEC = 24*3600

def sideral_time(longitude_deg):
    """Get the current sideral time from a longitude [degree]"""
    _iers_config.auto_max_age = None # remove error when too old IERS data
    observ_loc = EarthLocation(lat=0*_u.deg, lon=longitude_deg*_u.deg)
    observ_time = Time(datetime.datetime.utcnow(), scale='utc', location=observ_loc)
    return observ_time.sidereal_time('apparent')


def turn_ratio_to_ra(turn_ratio, longitude_dms):
	"""Get right ascension [°] from mount position and longitude (dd,mm,ss)"""
	sideral_time_deg = sideral_time(dms_to_deg(longitude_dms)).degree
	return sideral_time_deg - 360*turn_ratio
	
	
def turn_ratio_to_ra_hms(*args):
	"""Get right ascension (hh,mm,ss) from mount position and longitude (dd,mm,ss)"""
	return deg_to_hms(turn_ratio_to_ra(*args))


def ra_to_turn_ratio(ra_deg, longitude_dms):
	"""Get mount position from right ascension [°] and longitude (dd,mm,ss)"""
	sideral_time_deg = sideral_time(dms_to_deg(longitude_dms)).degree
	return (sideral_time_deg - ra_deg)/360
	

def dms_to_deg(tpl):
    """Convert a tuple (deg, arcmin, arcsec) to degree value"""
    if len(tpl)!=3:
        raise ValueError('Tuple must contain 3 elements (deg, arcmin, arcsec).')
    degree = abs(tpl[0]) + tpl[1]/60 + tpl[2]/3600
    positive = tpl[0] >= 0
    return positive*degree - (not positive)*degree


def deg_to_hms(deg):
    """Convert degrees into (hour,min,sec) tuple"""
    deg = deg%360
    hh = int(24*deg/360)
    mm = int(24*60*deg/360 - hh*60)
    ss = round(24*3600*deg/360 - hh*3600 - mm*60)
    return (hh,mm,ss)


def deg_to_dms(deg):
    """Convert degrees into (deg,arcmin,arcsec) tuple"""
    deg = deg%360
    dd = int(deg)
    arcmin = int(deg*60 - dd*60)
    arcsec = round(deg*3600 - dd*3600 - arcmin*60)
    return (dd,arcmin,arcsec)
