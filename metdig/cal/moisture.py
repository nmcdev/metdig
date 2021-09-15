# -*- coding: utf-8 -*-

import numpy as np
import math

import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units

from metdig.cal.lib import utility as utl
import metdig.utl as mdgstda


__all__ = [
    'dewpoint_from_relative_humidity',
    'dewpoint_from_specific_humidity',
    'saturation_vapor_pressure',
    'specific_humidity_from_dewpoint',
    'cal_ivt_singlelevel',
    'cal_p_vapor',
]


def dewpoint_from_relative_humidity(tmp, rh):
    '''

    [Calculate the ambient dewpoint given air temperature and relative humidity.]

    Arguments:
        tmp {[stda]} -- [air temperature]
        rh {[stda]} -- [relative humidity]

    Returns:
        [stda] -- [The dewpoint temperature]
    '''

    tmp_p = utl.stda_to_quantity(tmp)  # degC
    rh_p = utl.stda_to_quantity(rh)  # percent

    td_p = mpcalc.dewpoint_from_relative_humidity(tmp_p, rh_p)  # degC

    td = utl.quantity_to_stda_byreference('td', td_p, tmp)

    return td

def dewpoint_from_specific_humidity(pres, tmp, spfh):
    
    '''

    [Calculate the dewpoint from specific humidity, temperature, and pressure.]

    Arguments:
        pres {[stda]} -- [pressure]
        tmp {[stda]} -- [air temperature]
        spfh {[stda]} -- [specific_humidity]

    Returns:
        [stda] -- [The dewpoint temperature]
    '''
    pres_p = utl.stda_to_quantity(pres)  # hPa
    tmp_p = utl.stda_to_quantity(tmp)  # degC
    spfh_p = utl.stda_to_quantity(spfh)  # g/kg

    td_p = mpcalc.dewpoint_from_specific_humidity(pres_p, tmp_p, spfh_p)

    td = utl.quantity_to_stda_byreference('td', td_p, tmp)

    return td

def saturation_vapor_pressure(tmp):
    '''

    [Calculate the saturation water vapor (partial) pressure.]

    Arguments:
        tmp {[stda]} -- [air temperature]

    Returns:
        [stda] -- [The saturation water vapor (partial) pressure]
    '''
    tmp_p = utl.stda_to_quantity(tmp).to('degC')

    es_p = mpcalc.saturation_vapor_pressure(tmp_p).to('hPa')

    es = utl.quantity_to_stda_byreference('es', es_p, tmp)

    return es


def specific_humidity_from_dewpoint(pres, td):
    '''

    [Calculate the specific humidity from the dewpoint temperature and pressure.]

    Arguments:
        td {[stda]} -- [dewpoint temperature]
        pres {[stda]} -- [pressure]

    Returns:
        [stda] -- [Specific humidity]
    '''
    td_p = utl.stda_to_quantity(td)  # degC
    pres_p = utl.stda_to_quantity(pres)  # hPa

    spfh_p = mpcalc.specific_humidity_from_dewpoint(pres_p, td_p)  # kg/kg(dimensionless) # modify by wenzhijun pres和td参数对调，适应于metpy1.0

    spfh = utl.quantity_to_stda_byreference('spfh', spfh_p, td)  # g/kg
    return spfh


def cal_ivt_singlelevel(spfh, wsp):
    '''

    [单层水汽通量]

    Arguments:
        spfh {[stda]} -- [Specific humidity. dims must be (1,1,1,1,M,N)]
        wsp {[stda]} -- [wind speed. dims must be (1,1,1,1,M,N)]

    Returns:
        [stda] -- [单层水汽通量]
    '''
    # spfh: g/kg
    # wsp: m*s-1
    # 9.8 m*s-2

    # iqv: 0.1g/(cm*hPa*s)
    '''
    iq = np.abs(wsp) * spfh / 9.8
    iq = iq * 10
    '''

    spfh_p = utl.stda_to_quantity(spfh)  # g/kg
    wsp_p = utl.stda_to_quantity(wsp)  # m/s

    iq = wsp_p * spfh_p / (9.8*units('m/s**2'))

    iq = utl.quantity_to_stda_byreference('wvfl', iq, spfh)  # g/(cm*hPa*s)

    return iq


def cal_p_vapor(tmp, rh):
    '''

    [计算水汽压]

    Arguments:
        tmp {[stda]} -- [relative humidity]
        rh {[stda]} -- [relative humidity]

    Returns:
        [stda] -- [水汽压]
    '''
    tmp_p = utl.stda_to_quantity(tmp)  # degC
    rh_p = utl.stda_to_quantity(rh)  # percent

    tmp_p = np.array(tmp_p)
    rh_p = np.array(rh_p)

    p_vapor_p = (rh_p / 100.) * 6.105 * (math.e**((17.27 * tmp_p / (237.7 + tmp_p))))*units('Pa')  # 水汽压

    p_vapor = utl.quantity_to_stda_byreference('p_vapor', p_vapor_p, tmp)

    return p_vapor
