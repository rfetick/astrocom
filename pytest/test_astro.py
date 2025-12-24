
import pytest
import numpy as np
from astrocom.astro import dms_to_degree, degree_to_dms, hms_to_degree, degree_to_hms
from astrocom.astro import MountPosition, RaDec


def test_degree_to_dms():
    """Test degree to (dd,arcmin,arcsec) conversion"""
    for d in np.arange(-90, 90, 0.2):
        assert dms_to_degree(degree_to_dms(d)) == pytest.approx(d, abs=1e-8)


def test_degree_to_hms():
    """Test degree to (hh,mm,ss) conversion"""
    for d in np.arange(0, 360, 0.2):
        assert hms_to_degree(degree_to_hms(d)) == pytest.approx(d, abs=1e-8)


def test_radec():
    """Test set RaDec with coordinates in degrees"""
    for ra in range(0, 360, 15):
        for dec in range(0, 90, 15):
            radec = RaDec(ra, dec)
            assert radec.ra_degree == pytest.approx(ra, abs=1e-8)
            assert radec.dec_degree == pytest.approx(dec, abs=1e-8)


def test_conversion():
    """Test MountPosition conversion radec to telescope"""
    mp = MountPosition(5.2,45.2)
    for ra in range(1, 360, 30): # 1 to avoid time issue in 0
        for dec in range(-20, 90, 20):
            tel_pos = mp.radec_to_telescope(RaDec(ra, dec))
            radec = mp.telescope_to_radec(tel_pos)
            assert radec.ra_degree == pytest.approx(ra, abs=0.015)
            assert radec.dec_degree == pytest.approx(dec, abs=0.015)
            
    
    
