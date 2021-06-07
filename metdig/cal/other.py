# -*- coding: utf-8 -*-

'''

'''

import numpy as np

from scipy import ndimage


import metpy.calc as mpcalc

from .lib import utility as utl

__all__ = [
    'smooth_n_point',
    'gaussian_filter',
    'wind_components',
    'wind_direction',
    'wind_speed',
]


def smooth_n_point(stda_data, n=5, passes=1):
    '''
    see detail:
    metpy.calc.smooth_n_point
    '''
    result = stda_data.copy(deep=True)
    for a in range(result.coords['member'].size):
        for b in range(result.coords['level'].size):
            for c in range(result.coords['time'].size):
                for d in range(result.coords['dtime'].size):
                    scalar_grid = stda_data.values[a, b, c, d]
                    scalar_grid = mpcalc.smooth_n_point(scalar_grid, n=n, passes=passes)
                    result.values[a, b, c, d] = scalar_grid
    return result


def gaussian_filter(input_stda, sigma, order=0, output=None, mode='reflect', cval=0.0, truncate=4.0):
    '''
    see detail: 
    scipy.ndimage.gaussian_filter
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter.html
    '''
    result = input_stda.copy(deep=True)
    for a in range(result.coords['member'].size):
        for b in range(result.coords['level'].size):
            for c in range(result.coords['time'].size):
                for d in range(result.coords['dtime'].size):
                    scalar_grid = input_stda.values[a, b, c, d]
                    scalar_grid = ndimage.gaussian_filter(scalar_grid, sigma, order=order, output=output, mode=mode, cval=cval, truncate=truncate)
                    result.values[a, b, c, d] = scalar_grid
    return result


def wind_components(wsp, wdir):
    '''

    [Calculate the U, V wind vector components from the speed and direction.]

    Arguments:
        wsp {[stda]} -- [The wind speed (magnitude)]
        wdir {[stda]} -- [The wind direction, specified as the direction from which the wind is blowing (0-2 pi radians or 0-360 degrees), with 360 degrees being North.]

    Returns:
        [u, v (tuple of stda) ] -- [The wind components in the X (East-West) and Y (North-South) directions, respectively]
    '''
    wsp_p = utl.stda_to_quantity(wsp)  # m/s
    wdir_p = utl.stda_to_quantity(wdir)  # degree

    u_p, v_p = mpcalc.wind_components(wsp_p, wdir_p)  # m/s

    u = utl.quantity_to_stda_byreference('u', u_p, wsp)
    v = utl.quantity_to_stda_byreference('v', v_p, wdir)

    return u, v


def wind_direction(u, v):
    '''

    [Compute the wind speed from u and v-components.]

    Arguments:
        u {[stda]} -- [Wind component in the X (East-West) direction]
        v {[stda]} -- [Wind component in the Y (East-West) direction]

    Returns:
        [wind speed (stda)] -- [The speed of the wind]
    '''
    u_p = utl.stda_to_quantity(u)  # m/s
    v_p = utl.stda_to_quantity(v)  # m/s

    wdir_p = mpcalc.wind_direction(u_p, v_p)  # degree

    wdir = utl.quantity_to_stda_byreference('wdir', wdir_p, u)

    return wdir


def wind_speed(u, v):
    '''

    [Compute the wind speed from u and v-components.]

    Arguments:
        u {[stda]} -- [Wind component in the X (East-West) direction]
        v {[stda]} -- [Wind component in the Y (East-West) direction]

    Returns:
        [wind speed (stda)] -- [The speed of the wind]
    '''
    u_p = utl.stda_to_quantity(u)  # m/s
    v_p = utl.stda_to_quantity(v)  # m/s

    wsp_p = mpcalc.wind_speed(u_p, v_p)

    wsp = utl.quantity_to_stda_byreference('wsp', wsp_p, u)

    return wsp
