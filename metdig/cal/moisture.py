# -*- coding: utf-8 -*-

import numpy as np
import math

import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units

from metdig.cal.lib import utility as utl
import metdig.utl as mdgstda
from metdig.cal.lib.utility import unifydim_stda, check_stda


__all__ = [
    'dewpoint_from_relative_humidity',
    'dewpoint_from_specific_humidity',
    'saturation_vapor_pressure',
    'specific_humidity_from_dewpoint',
    'cal_ivt_singlelevel',
    'cal_p_vapor',
    'relative_humidity_from_dewpoint',
    'water_wapor_flux_divergence'
]


def integrated_water_vapor_flux(spfh,u,v, psfc=None):
    for itime in spfh.stda.get_dim_value('time'):
        for idtime in spfh.stda.get_dim_value('dtime'):
            for imember in spfh.stda.get_dim_value('member'):
                spfh_q=spfh.sel(time=itime,dtime=idtime,member=imember).transpose(['level','lat','lon'])
                u_q=u.sel(time=itime,dtime=idtime,member=imember).transpose(['level','lat','lon'])
                v_q=v.sel(time=itime,dtime=idtime,member=imember).transpose(['level','lat','lon'])
                psfc_q=psfc.sel(time=itime,dtime=idtime,member=imember).transpose(['level','lat','lon'])


if __name__ == '__main__':
    import metdig
    from datetime import datetime

    ret1=metdig.onestep.diag_synoptic.hgt_uv_wsp(is_return_data=True,is_draw=False)
    ret2=metdig.onestep.diag_moisture.hgt_uv_spfh(is_return_data=True,is_draw=False)

    u=ret1['data']['u']
    v=ret1['data']['v']
    spfh=ret2['data']['spfh']

    wvfldiv=integrated_water_vapor_flux(u,v,spfh)
    print (wvfldiv)

@check_stda(['tmp', 'td'])
@unifydim_stda(['tmp', 'td'])
def relative_humidity_from_dewpoint(tmp,td):
    tmp_p = utl.stda_to_quantity(tmp)  # degC
    td_p = utl.stda_to_quantity(td)  # degC

    rh_p = mpcalc.relative_humidity_from_dewpoint(tmp_p, td_p)*100*units('percent')  # percent

    rh = utl.quantity_to_stda_byreference('rh', rh_p, tmp)

    return rh

@check_stda(['tmp', 'rh'])
@unifydim_stda(['tmp', 'rh'])
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

@check_stda(['pres', 'tmp', 'spfh'])
@unifydim_stda(['pres', 'tmp', 'spfh'])
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

@check_stda(['tmp'])
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


@check_stda(['pres', 'td'])
@unifydim_stda(['pres', 'td'])
def specific_humidity_from_dewpoint(pres, td):
    '''

    [Calculate the specific humidity from the dewpoint temperature and pressure.]

    Arguments:
        pres {[stda]} -- [pressure]
        td {[stda]} -- [dewpoint temperature]

    Returns:
        [stda] -- [Specific humidity]
    '''
    td_p = utl.stda_to_quantity(td)  # degC
    pres_p = utl.stda_to_quantity(pres)  # hPa

    spfh_p = mpcalc.specific_humidity_from_dewpoint(pres_p, td_p)  # kg/kg(dimensionless) # modify by wenzhijun pres和td参数对调，适应于metpy1.0

    spfh = utl.quantity_to_stda_byreference('spfh', spfh_p, td)  # g/kg
    return spfh


@check_stda(['spfh', 'wsp'])
@unifydim_stda(['spfh', 'wsp'])
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


@check_stda(['tmp', 'rh'])
@unifydim_stda(['tmp', 'rh'])
def cal_p_vapor(tmp, rh):
    '''

    [计算水汽压]

    Arguments:
        tmp {[stda]} -- [air temperature]
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

@check_stda(['u', 'v', 'spfh'])
@unifydim_stda(['u', 'v', 'spfh'])
def water_wapor_flux_divergence(u,v,spfh):
    uwvfl=cal_ivt_singlelevel(u,spfh)
    vwvfl=cal_ivt_singlelevel(v,spfh)
    
    uwvfl_p = utl.stda_to_quantity(uwvfl) 
    vwvfl_p = utl.stda_to_quantity(vwvfl)

    lons = uwvfl['lon'].values
    lats = uwvfl['lat'].values

    dx, dy = mpcalc.lat_lon_grid_deltas(lons, lats)

    dx = dx[np.newaxis, np.newaxis, np.newaxis, np.newaxis, :, :]
    dy = dy[np.newaxis, np.newaxis, np.newaxis, np.newaxis, :, :]

    wvfldiv_p = mpcalc.divergence(uwvfl_p, vwvfl_p, dx=dx, dy=dy)

    wvfldiv = utl.quantity_to_stda_byreference('wvfldiv', wvfldiv_p, u)

    return wvfldiv
