"""
Astronomical computations
"""

import os
import re
import datetime
import numpy as np
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from astropy.time import Time
from astropy import units as _u
from astropy.utils.iers import conf as _iers_config
from astrocom import COLORS

_iers_config.auto_max_age = None # remove error when too old IERS data

SIDERAL_DAY_SEC = 23*3600 + 56*60 + 4.09
SOLAR_DAY_SEC = 24*3600


class RaDec:
	"""An object with sky coordinates RA-DEC"""
	def __init__(self, ra, dec):
		self.ra = ra
		self.dec = dec
	
	def __repr__(self):
		return "RaDec %s %s"%(self.ra_str,self.dec_str)
	
	@property
	def ra(self):
		return self._ra
		
	@property
	def dec(self):
		return self._dec
	
	@ra.setter
	def ra(self, val):
		# Data given as string '12:26:45' or '12:26'
		if type(val) is str:
			coord = re.findall('[0-9-]+',val)
			val = [0,0,0]
			for i in range(len(coord)):
				val[i] = int(float(coord[i]))
		# Data given as degrees
		if type(val) in [float, int, np.float64]:
			val = degree_to_hms(val)
		# Data given as tuple (default)
		self._ra = tuple(val)
		
	@dec.setter
	def dec(self, val):
		# Data given as string "12°26'45" or "12°26"
		if type(val) is str:
			coord = re.findall('[0-9-]+',val)
			val = [0,0,0]
			for i in range(len(coord)):
				val[i] = int(float(coord[i]))
		# Data given as degrees
		if type(val) in [float, int, np.float64]:
			val = degree_to_dms(val)
		# Data given as tuple (default)
		self._dec = tuple(val)
	
	@property
	def ra_degree(self):
		return hms_to_degree(self.ra)
		
	@property
	def dec_degree(self):
		return dms_to_degree(self.dec)
		
	@property
	def ra_str(self):
		return "%02u:%02u:%02u"%self.ra
		
	@property
	def dec_str(self):
		return "%3u°%02u'%02u"%self.dec
		
	def altaz(self, latitude_tpl, longitude_tpl):
		latitude_deg = dms_to_degree(latitude_tpl)
		longitude_deg = dms_to_degree(longitude_tpl)
		return radec_to_altaz(self.ra_degree, self.dec_degree, latitude_deg, longitude_deg)


class MountPosition(RaDec):
	"""MountPosition is located at (longitude,latitude) on Earth and observes a target"""
	def __init__(self, longitude, latitude):
		# Data given as degrees
		if type(longitude) in [float, int]:
			longitude = degree_to_dms(longitude)
		if type(latitude) in [float, int]:
			latitude = degree_to_dms(latitude)
		# Data given as tuple (default)
		self._longitude = tuple(longitude)
		self._latitude = tuple(latitude)
		# looks towards celestial pole at startup
		# the relative target (HA,DEC) is defined with respect to the meridian
		# the absolute target (RA,DEC) is defined with respect to the ra-dec system
		self._target_hadec = RaDec(0, 90*self.north-90*self.south)
	
	def __repr__(self):
		return "MountPosition %sN %sE"%(self.latitude_str,self.longitude_str)
	
	def complementary_angle(self, ha_or_ra):
		"""
		Get complementary angle as:
		RA + HA = sideral time
		"""
		ra_or_ha_degree = RaDec(ha_or_ra, 0).ra_degree
		return RaDec(self.sideral_time.degree - ra_or_ha_degree, 0)
	
	@property
	def _ra(self):
		"""Target sky RA (hh,mm,ss)"""
		return degree_to_hms(self.sideral_time.degree - self._target_hadec.ra_degree)
		
	@property
	def _dec(self):
		"""Target sky DEC (dd,arcmin,arcsec)"""
		return self._target_hadec.dec
	
	@_dec.setter
	def _dec(self, val):
		self._target_hadec.dec = val
	
	@property
	def altaz(self):
		"""Get current Altitude-Azimuth of the telescope"""
		return super().altaz(self.latitude, self.longitude)
	
	@property
	def hour_angle(self):
		"""Target sky Hour Angle"""
		return self._target_hadec.ra
		
	@hour_angle.setter
	def hour_angle(self, val):
		self._target_hadec.ra = val
	
	@property
	def longitude(self):
		"""Telescope longitude (dd,arcmin,arcsec)"""
		return self._longitude
		
	@property
	def latitude(self):
		"""Telescope latitude (dd,arcmin,arcsec)"""
		return self._latitude
		
	@property
	def longitude_degree(self):
		return dms_to_degree(self.longitude)
		
	@property
	def latitude_degree(self):
		return dms_to_degree(self.latitude)
	
	@property
	def longitude_str(self):
		return "%3u°%02u'%02u"%self.longitude
		
	@property
	def latitude_str(self):
		return "%3u°%02u'%02u"%self.latitude
	
	@property
	def north(self):
		"""Is the telescope located North"""
		return self.latitude[0] >= 0
		
	@property
	def south(self):
		"""Is the telescope located South"""
		return not self.north	
	
	@property
	def sideral_time(self):
		"""Get current sideral time"""
		return sideral_time(self.longitude_degree)
		


class Star(RaDec):
	"""A star in the sky, inherits from RaDec class"""
	def __init__(self, ra, dec, hr, vmag, constell=None, sptype=None, name=None):
		super().__init__(ra, dec)
		self.hr = hr
		self.vmag = vmag
		self.constell = constell
		self.sptype = sptype
		self.name = name
		
	@property
	def header(self):
		return '%4s  %5s  %10s  %5s  %6s  %4s'%('HR','CONST','NAME','RA','DEC','MV')
		
	def __repr__(self):
		hr = '%4u'%self.hr
		constell = '%5s'%self.constell[-3:]
		name = '%10s'%self.name[0:min(10,len(self.name))]
		ra = '%02u:%02u'%self.ra[:-1]
		dec = "%3u°%02u"%self.dec[:-1]
		mag = "%4.1f"%self.vmag
		return '  '.join((hr, constell, name, ra, dec, mag))
		


def read_bsc():
	"""Read the simplified Bright Star Catalog"""
	stars = []
	header = True
	with open(os.path.dirname(__file__)+'/bsc_simplified.txt','r') as myfile:
		for line in myfile:
			if not header:
				try:
					elem = line.split('|')
					hr = int(elem[0])
					constell = elem[1].replace(' ','')
					ra = (int(elem[2]), int(elem[3]), int(float(elem[4])))
					if '-' in elem[5]:
						dec_sign = -1
					else:
						dec_sign = 1
					dec = (dec_sign*int(elem[6]), int(elem[7]), int(elem[8]))
					vmag = float(elem[9])
					sptype = elem[10].replace(' ','')
					name = elem[11].replace(' ','')
					stars.append(Star(ra, dec, hr, vmag, constell, sptype, name=name))
				except:
					pass
			header = False
	return sorted(stars, key=lambda s:s.vmag) # sort by magnitude


def catalog_str(catalog, nb_to_print, latitude_dms, longitude_dms, alt_min=10, bicolor=False):
	"""Get the brightest stars of the catalog as a string"""
	st = '-'*(len(catalog[0].header)+10) + '\n'
	st += catalog[0].header + '  %4s  %2s'%('ALT','AZ') + '\n'
	st += '-'*(len(catalog[0].header)+10) + '\n'
	clr = '' # no color by default
	clr_reset = ''
	for i in range(len(catalog)):
		alt,az = catalog[i].altaz(latitude_dms, longitude_dms)
		if alt >= alt_min:
			if bicolor:
				clr_reset = COLORS.RESET
				if nb_to_print%2:
					clr = COLORS.BLUE
				else:
					clr = COLORS.RESET
			st += clr + catalog[i].__str__() + '  %3u°  %2s'%(alt,cardinal_point(az)) + clr_reset + '\n'
			nb_to_print -= 1
			if nb_to_print <= 0:
				break
	st += '-'*(len(catalog[0].header)+10)
	return st


def print_catalog(*args, **kwargs):
	"""Print the brightest stars of the catalog"""
	print(catalog_str(*args, **kwargs))


def sideral_time(longitude_deg):
	"""Get the current sideral time from a longitude [degree]"""
	observ_loc = EarthLocation(lat=0*_u.deg, lon=longitude_deg*_u.deg)
	observ_time = Time(datetime.datetime.utcnow(), scale='utc', location=observ_loc)
	return observ_time.sidereal_time('apparent')


def radec_to_altaz(ra_deg, dec_deg, latitude_deg, longitude_deg):
	"""Convert RA-DEC to ALT-AZ coordinates"""
	observ_loc = EarthLocation(lat=latitude_deg*_u.deg, lon=longitude_deg*_u.deg)
	observ_time = Time(datetime.datetime.utcnow(), scale='utc', location=observ_loc)
	altaz_frame = AltAz(obstime=observ_time, location=observ_loc)
	sc = SkyCoord(ra=ra_deg*_u.deg, dec=dec_deg*_u.deg, frame='icrs')
	sc_az = sc.transform_to(altaz_frame)
	return sc_az.alt.value, sc_az.az.value


def cardinal_point(az_deg):
	"""Get cardinal point string from azimuth [°]"""
	az_list = np.array([0, 45, 90, 135, 180, 225, 270, 315, 360])
	az_letter = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
	idx = np.argmin(np.abs(az_list-az_deg))
	return az_letter[idx]


def dms_to_degree(tpl):
	"""Convert a tuple (deg, arcmin, arcsec) to degree value"""
	if len(tpl)!=3:
		raise ValueError('Tuple must contain 3 elements (deg, arcmin, arcsec).')
	degree = abs(tpl[0]) + tpl[1]/60 + tpl[2]/3600
	positive = tpl[0] >= 0
	return positive*degree - (not positive)*degree


def hms_to_degree(tpl):
	"""Convert a tuple (hh,mm,ss) to degree value"""
	if len(tpl)!=3:
		raise ValueError('Tuple must contain 3 elements (hh,mm,ss).')
	degree = 360/24*(tpl[0] + tpl[1]/60 + tpl[2]/3600)
	return degree % 360


def degree_to_hms(deg):
	"""Convert degrees into (hour,min,sec) tuple"""
	deg = deg % 360
	hh = int(24*deg/360)
	mm = int(24*60*deg/360 - hh*60)
	ss = round(24*3600*deg/360 - hh*3600 - mm*60)
	return (hh,mm,ss)


def degree_to_dms(deg):
	"""Convert degrees into (deg,arcmin,arcsec) tuple"""
	deg = deg % 360
	dd = int(deg)
	arcmin = int(deg*60 - dd*60)
	arcsec = round(deg*3600 - dd*3600 - arcmin*60)
	return (dd,arcmin,arcsec)

