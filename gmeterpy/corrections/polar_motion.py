# -*- coding: utf-8 -*-
"""Polar motion correction.

This module contains the polar motion correction to the gravity observations.

"""

import warnings

import numpy as np

from astropy.utils import iers

iers.conf.auto_max_age = 10
iers.conf.auto_download = None
IERS_A_URL = 'ftp://ftp.iers.org/products/eop/rapid/standard/finals2000A.all'
iers.conf.iers_auto_url = IERS_A_URL
iers.conf.remote_timeout = 60


def get_iers_polar_motion(jd):
    """Interpolate polar motions from the IERS for the given dates.

    This function will automatically download IERS data and interpolate
    pole coordinates for the given dates `jd`.

    Parameters
    ----------
    jd : float, array, or `astropy.time.Time` object
        Julian Date or `astropy.time.Time` object.

    Returns
    -------
    xp, yp : float or array_like
        Polar motion coordinates, in arcsec.

    """
    iers_table = iers.IERS_Auto.open()
    pm_x, pm_y, status = iers_table.pm_xy(jd, return_status=True)

    if np.any(status != iers.FROM_IERS_B):
        wrnmsg = ("Some pole coordinates are not final.")
        warnings.warn(wrnmsg)

    return pm_x, pm_y


def polar_motion_correction(xp, yp, lat, lon):
    r"""Polar motion correction, in m/s**2.

    Parameters
    ----------
    xp : float
        x coordinate of the terrestrial pole, in arcsec.
    yp : float
        y coordinate of the terrestrial pole, in arcsec.
    lat : float
        Geocentric latitude of the observation point referred to IERS pole, in degrees.
    lon : float
        Geocentric longitude of the observation point referred to IERS pole, in degrees.

    Returns
    -------
    float or array_like:
        Polar motion correction, in m/s**2.

    Notes
    -----
    Variations in the geocentric position of the Earth's rotation axis
    (polar motion) cause deformation within the Earth due to centrifugal forces.
    The actual position of the rotational axis is referenced to the IERS pole
    and described by the pole coordinates. The gravity correction (pole tide)
    is expressed by, e.g. Wahr (1985) [1]_:

    .. math::

       \delta g = -\delta\omega^2\times a \times 2 \times
       \sin\phi\cos\phi\left(x\cos\lambda - y\sin\lambda\right)\quad
       [\textrm{ms}^{-2}]

    where :math:`x,y` -- pole coordinates,
    :math:`\omega` -- mean angular velocity,
    :math:`a = 6 378 136` [m] -- equatirial radius of the Earth,
    :math:`\phi,\lambda` -- geocentric coordinates of the station,
    :math:`\delta = 1.164` -- is the amplitude factor for
    the elastic response of the Earth.

    Reference
    ---------
    .. [1] Wahr, J. M. ( 1985), Deformation induced by polar motion,
       J. Geophys. Res., 90( B11), 9363– 9368, doi:10.1029/JB090iB11p09363

    """

    a = 6378136
    omega = 7292115e-11

    xp = np.radians(xp / 3600)
    yp = np.radians(yp / 3600)
    lat = np.radians(lat)
    lon = np.radians(lon)

    coords = 2 * np.sin(lat) * np.cos(lat) * \
        (xp * np.cos(lon) - yp * np.sin(lon))

    return -1.164 * omega**2 * a * coords
