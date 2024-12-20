"""
Test coordinates conversion
"""


from astrocom.astro import dms_to_degree, sideral_time, radec_to_altaz, hms_to_degree, read_bsc, print_catalog

latitude_dms = (43,36,15) # (sign*degree, arcmin, arcsec)
longitude_dms = (1,26,37) # (sign*degree, arcmin, arcsec) 
catalog = read_bsc()

### PRINT ZENITH AND POLE
latitude_deg = dms_to_degree(latitude_dms)
longitude_deg = dms_to_degree(longitude_dms)
sid_time = sideral_time(longitude_deg)
meridian_deg = hms_to_degree(sid_time.hms)

north_pole_altaz = radec_to_altaz(0, 90, latitude_deg, longitude_deg)
zenith_altaz = radec_to_altaz(meridian_deg, latitude_deg, latitude_deg, longitude_deg)

print('Sideral time  = %02u:%02u:%02u'%sid_time.hms)
print('Zenith alt-az = %5.1f° %5.1f°'%zenith_altaz)
print('Pole   alt-az = %5.1f° %5.1f°'%north_pole_altaz)

### PRINT CATALOG
print()
print_catalog(catalog, 15, latitude_dms, longitude_dms)

