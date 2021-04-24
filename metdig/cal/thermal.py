# -*- coding: utf-8 -*-

import numpy as np
import math

import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units

from .lib import utility  as utl
import metdig.utl as mdgstda


def potential_temperature(pres, tmp):
    '''

    [Calculate the potential temperature.

    Uses the Poisson equation to calculation the potential temperature given pressure and temperature]

    Arguments:
        pres {[stda]} -- [total atmospheric pressure]
        tmp {[stda]} -- [air temperature]
    '''
    pres_p = utl.stda_to_quantity(pres)  # hPa
    tmp_p = utl.stda_to_quantity(tmp)  # degC

    thta_p = mpcalc.potential_temperature(pres_p, tmp_p)  # kelvin

    thta = utl.quantity_to_stda_byreference('thta', thta_p, tmp)  # degC

    return thta



def equivalent_potential_temperature(pres, tmp, td):
    '''

    [Calculate equivalent potential temperature.]

    Arguments:
        pres {[stda]} -- [Total atmospheric pressure]
        tmp {[stda]} -- [temperature of parcel]
        td {[stda]} -- [dewpoint of parcel]

    Returns:
        [stda] -- [The equivalent potential temperature of the parcel]
    '''
    pres_p = utl.stda_to_quantity(pres)  # hPa
    tmp_p = utl.stda_to_quantity(tmp)  # degC
    td_p = utl.stda_to_quantity(td)  # degC

    theta_p = mpcalc.equivalent_potential_temperature(pres_p, tmp_p, td_p)  # kelvin

    theta = utl.quantity_to_stda_byreference('theta', theta_p, tmp)  # kelvin

    return theta




def apparent_temperature(tmp, wsp, p_vapor):
    '''

    [计算体感温度]

    Arguments:
        tmp {[stda]} -- [temperature]
        wsp {[stda]} -- [wind speed]
        p_vapor {[stda]} -- [水汽压]

    Returns:
        [stda] -- [体感温度]
    '''
    tmp_p = utl.stda_to_quantity(tmp)  # degC
    wsp_p = utl.stda_to_quantity(wsp)  # m/s
    p_vapor_p = utl.stda_to_numpy(p_vapor)

    tmp_p = np.array(tmp_p)
    wsp_p = np.array(wsp_p)

    at_p = (1.07 * tmp_p + 0.2 * p_vapor_p - 0.65 * wsp_p - 2.7)*units('degC')  # 体感温度

    at = utl.quantity_to_stda_byreference('at', at_p, tmp)

    return at
