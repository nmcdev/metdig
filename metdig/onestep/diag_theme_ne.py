# -*- coding: utf-8 -*-
'''
@author:谭正华
'''

import numpy as np
import xarray as xr
import datetime

from metdig.io import get_model_grid
from metdig.io import get_model_3D_grid
from metdig.io import get_model_3D_grids
from metdig.io import get_obs_stations

from metdig.onestep.lib.utility import get_map_area, cross_extent, point_to1dim
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.onestep.complexgrid_var.div_uv import read_div_uv,read_div_uv_3d
from metdig.onestep.complexgrid_var.spfh import read_spfh
from metdig.onestep.complexgrid_var.theta import read_theta
from metdig.onestep.complexgrid_var.theta import read_theta3d
from metdig.onestep.complexgrid_var.w import read_w3d
from metdig.onestep.complexgrid_var.get_rain import read_rain

from metdig.products import diag_theme_ne as draw_theme_ne

import metdig.cal as mdgcal
import metdig.utl as mdgstda
import meteva.base as meb

from metdig.onestep.diag_synoptic import hgt_uv_wsp
from metdig.onestep.diag_moisture import hgt_uv_spfh
from metdig.onestep.diag_crossection import wind_theta_rh
from metdig.onestep.diag_crossection import time_rh_uv_tmp_vvel
from metdig.onestep.diag_qpf import rain


__all__ = [
    'obs_wind_div_td',
    'obs_wind_div_tmp',
    'obs_wind_wsp_div_dtmp',
    'obs_rain24',
    'prmsl_dprmsl24',
    'hgt_ana_fcst_bias',
    'wsp_ana_fcst_bias',
    'prmsl_ana_fcst_bias',
    'hgt_ivt',
    'wvfldiv_tcwv',
    'div_tcwv',
    'wsp_uv_div',
    'uv_fg_thta',
    'K_idx',
    'cape',
    'cross_theta_fg_mpv',
    'cross_div_uv_wsp',
    'cross_wind_w_tmp_vvel_tmpadv',
    'hgt_fcst_change',
    'wind_fcst_change',
    'prmsl_fcst_change',
]

@date_init('init_time')
def prmsl_dprmsl24(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                   is_mask_terrain=True,
                   area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    prmsl = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='prmsl', extent=map_extent)
    init_time0 = init_time+datetime.timedelta(days=-1)
    prmsl0 = get_model_grid(data_source=data_source, init_time=init_time0, fhour=fhour, data_name=data_name, var_name='prmsl', extent=map_extent)
    dprmsl24=prmsl.isel(member=0,level=0,time=0,dtime=0)-prmsl0.isel(member=0,level=0,time=0,dtime=0)
    dprmsl24.attrs['var_cn_name']='24小时变压'
    dprmsl24.attrs['var_units']='hPa'

    if is_return_data:
        dataret = {'prmsl': prmsl, 'dprmsl24': dprmsl24}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        prmsl = mask_terrian(psfc, prmsl)
        dprmsl24 = mask_terrian(psfc, dprmsl24)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_prmsl_dprmsl24(prmsl, dprmsl24, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def hgt_ana_fcst_bias(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                   hgt_lev=850, is_mask_terrain=True,
                   area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt_a = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    fhour0=24
    init_time0 = init_time-datetime.timedelta(hours=fhour0)
    hgt_f = get_model_grid(data_source=data_source, init_time=init_time0, fhour=fhour0, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    hgt_b=hgt_f.isel(member=0,level=0,time=0,dtime=0)-hgt_a.isel(member=0,level=0,time=0,dtime=0)
    hgt_b.attrs['var_cn_name']='24小时预报偏差'
    hgt_b.attrs['var_units']='dagpm'


    if is_return_data:
        dataret = {'hgt_a': hgt_a, 'hgt_f': hgt_f, 'hgt_b': hgt_b}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt_a = mask_terrian(psfc, hgt_a)
        hgt_f = mask_terrian(psfc, hgt_f)
        hgt_b = mask_terrian(psfc, hgt_b)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_hgt_ana_fcst_bias(hgt_a, hgt_f, hgt_b, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
@date_init('init_time')
def wsp_ana_fcst_bias(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                   hgt_lev=925, is_mask_terrain=True,
                   area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u_a = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=hgt_lev, extent=map_extent)
    v_a = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=hgt_lev, extent=map_extent)
    fhour0=24
    init_time0 = init_time-datetime.timedelta(hours=fhour0)
    u_f = get_model_grid(data_source=data_source, init_time=init_time0, fhour=fhour0, data_name=data_name, var_name='u', level=hgt_lev, extent=map_extent)
    v_f = get_model_grid(data_source=data_source, init_time=init_time0, fhour=fhour0, data_name=data_name, var_name='v', level=hgt_lev, extent=map_extent)
    wsp_a = mdgcal.wind_speed(u_a, v_a)
    wsp_f = mdgcal.wind_speed(u_f, v_f)
    wsp_b=wsp_f.isel(member=0,level=0,time=0,dtime=0)-wsp_a.isel(member=0,level=0,time=0,dtime=0)
    wsp_b.attrs['var_cn_name']='风速预报偏差'
    wsp_b.attrs['var_units']='m/s'


    if is_return_data:
        dataret = {'u_a': u_a, 'v_a': v_a, 'u_f': u_f, 'v_f': v_f, 'wsp_a': wsp_a, 'wsp_f': wsp_f, 'wsp_b': wsp_b}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        u_a = mask_terrian(psfc, u_a)
        v_a = mask_terrian(psfc, v_a)
        u_f = mask_terrian(psfc, u_f)
        v_f = mask_terrian(psfc, v_f)
        wsp_a = mask_terrian(psfc, wsp_a)
        wsp_f = mask_terrian(psfc, wsp_f)
        wsp_b = mask_terrian(psfc, wsp_b)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_wsp_ana_fcst_bias(u_a, v_a, u_f, v_f, wsp_a, wsp_f, wsp_b, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
    
@date_init('init_time')
def prmsl_ana_fcst_bias(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                   prmsl_lev=850, is_mask_terrain=True,
                   area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    prmsl_a = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='prmsl', extent=map_extent)
    fhour0=24
    init_time0 = init_time-datetime.timedelta(hours=fhour0)
    prmsl_f = get_model_grid(data_source=data_source, init_time=init_time0, fhour=fhour0, data_name=data_name, var_name='prmsl', extent=map_extent)
    prmsl_b=prmsl_f.isel(member=0,level=0,time=0,dtime=0)-prmsl_a.isel(member=0,level=0,time=0,dtime=0)
    prmsl_b.attrs['var_cn_name']='海平面气压预报偏差'
    prmsl_b.attrs['var_units']='hPa'


    if is_return_data:
        dataret = {'prmsl_a': prmsl_a, 'prmsl_f': prmsl_f, 'prmsl_b': prmsl_b}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        prmsl_a = mask_terrian(psfc, prmsl_a)
        prmsl_f = mask_terrian(psfc, prmsl_f)
        prmsl_b = mask_terrian(psfc, prmsl_b)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_prmsl_ana_fcst_bias(prmsl_a, prmsl_f, prmsl_b, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
    
@date_init('init_time')
def hgt_ivt(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
            hgt_lev=925, ivt_lev=925, is_mask_terrain=True,
            area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=ivt_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=ivt_lev, extent=map_extent)
    spfh = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='spfh', level=ivt_lev, extent=map_extent)

    wsp = mdgcal.other.wind_speed(u, v)
    ivt = mdgcal.moisture.cal_ivt_singlelevel(spfh, wsp)
    ivtu = mdgcal.moisture.cal_ivt_singlelevel(spfh, u)
    ivtv = mdgcal.moisture.cal_ivt_singlelevel(spfh, v)

    if is_return_data:
        dataret = {'hgt': hgt, 'ivt': ivt, 'ivtu': ivtu, 'ivtv': ivtv}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        ivt = mask_terrian(psfc, ivt)
        ivtu = mask_terrian(psfc, ivtu)
        ivtv = mask_terrian(psfc, ivtv)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_hgt_ivt(hgt, ivtu, ivtv, ivt, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def wvfldiv_tcwv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                wvfldiv_lev=925, is_mask_terrain=True,
                area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get data
    map_extent = get_map_area(area)
    tcwv = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='tcwv', extent=map_extent)
    
    # 水汽通量散度
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=wvfldiv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=wvfldiv_lev, extent=map_extent)
    spfh = read_spfh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=wvfldiv_lev, extent=map_extent)

    smt_stp=1
    u = mdgcal.gaussian_filter(u, smt_stp)
    v = mdgcal.gaussian_filter(v, smt_stp)
    spfh = mdgcal.gaussian_filter(spfh, smt_stp)
    wvfldiv=mdgcal.water_wapor_flux_divergence(u,v,spfh)
    wvfldiv=wvfldiv * 1e5
    
    if is_return_data:
        dataret = {'wvfldiv': wvfldiv, 'tcwv': tcwv}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        wvfldiv = mask_terrian(psfc, wvfldiv)
        tcwv = mask_terrian(psfc, tcwv)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_wvfldiv_tcwv(wvfldiv, tcwv, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
@date_init('init_time')
def div_tcwv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                div_lev=925, is_mask_terrain=True,
                area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get data
    map_extent = get_map_area(area)
    tcwv = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='tcwv', extent=map_extent)
    
    # 散度
    smth_stp=5
    div, u, v = read_div_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=div_lev, extent=map_extent)

    div_attrs = div.attrs
    div = div.rolling(lon=smth_stp, lat=smth_stp, min_periods=1, center=True).mean()
    div.attrs = div_attrs
    # div=div * 1e5    
    
    if is_return_data:
        dataret = {'div': div, 'tcwv': tcwv}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        div = mask_terrian(psfc, div)
        tcwv = mask_terrian(psfc, tcwv)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_div_tcwv(div, tcwv, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    

@date_init('init_time')
def wsp_uv_div(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
            uv_lev=925, is_mask_terrain=True,
            area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    
    wsp = mdgcal.wind_speed(u, v)
    div = mdgcal.divergence(u, v)

    if is_return_data:
        dataret = {'wsp': wsp, 'u': u, 'v': v, 'div': div}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        wsp = mask_terrian(psfc, wsp)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        div = mask_terrian(psfc, div)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_wsp_uv_div(wsp, u, v, div, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    

@date_init('init_time')
def uv_fg_thta(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
               fg_lev=500,smth_stp=5,is_mask_terrain=True,
               area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=fg_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=fg_lev, extent=map_extent)
    theta=read_theta(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=fg_lev, extent=map_extent)
    tmp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='tmp', level=fg_lev, extent=map_extent)
    
    pres = mdgstda.gridstda_full_like(tmp, fg_lev, var_name='pres')
    thta = mdgcal.potential_temperature(pres, tmp)
    
    # thta = mdgcal.gaussian_filter(thta, smth_stp)
    # fg = mdgcal.frontogenesis(mdgcal.gaussian_filter(thta, smth_stp), mdgcal.gaussian_filter(u, smth_stp), mdgcal.gaussian_filter(v, smth_stp))
    fg=mdgcal.frontogenesis(thta.rolling(lon=smth_stp, lat=smth_stp, min_periods=1, center=True).mean(skipna=True),
                            u.rolling(lon=smth_stp, lat=smth_stp, min_periods=1, center=True).mean(skipna=True),
                            v.rolling(lon=smth_stp, lat=smth_stp, min_periods=1, center=True).mean(skipna=True))

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        thta = mask_terrian(psfc, thta)
        # thta=theta
        fg = mask_terrian(psfc, fg)

    if is_return_data:
        dataret = {'u': u, 'v': v, 'thta': thta, 'fg': fg}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_uv_fg_thta(u, v, thta, fg, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def K_idx(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
          is_mask_terrain=True,
          area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    T850 = get_model_grid(data_source=data_source, data_name=data_name, var_name='tmp', init_time=init_time, fhour=fhour, level=850, extent=map_extent)
    T500 = get_model_grid(data_source=data_source, data_name=data_name, var_name='tmp', init_time=init_time, fhour=fhour, level=500, extent=map_extent)
    T700 = get_model_grid(data_source=data_source, data_name=data_name, var_name='tmp', init_time=init_time, fhour=fhour, level=700, extent=map_extent)
    rh850 = get_model_grid(data_source=data_source, data_name=data_name, var_name='rh', init_time=init_time, fhour=fhour, level=850, extent=map_extent)
    rh700 = get_model_grid(data_source=data_source, data_name=data_name, var_name='rh', init_time=init_time, fhour=fhour, level=700, extent=map_extent)
    
    Td850 = mdgcal.moisture.dewpoint_from_relative_humidity(T850, rh850)
    Td700 = mdgcal.moisture.dewpoint_from_relative_humidity(T700, rh700)
    K_idx=(T850.isel(member=0,level=0,time=0,dtime=0)-T500.isel(member=0,level=0,time=0,dtime=0))+Td850.isel(member=0,level=0,time=0,dtime=0)-(T700.isel(member=0,level=0,time=0,dtime=0)-Td700.isel(member=0,level=0,time=0,dtime=0))
 
    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        T850 = mask_terrian(psfc, T850)
        K_idx = mask_terrian(psfc, K_idx)

    if is_return_data:
        dataret = {'T850': T850, 'K_idx': K_idx}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_K_idx(T850, K_idx, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def cape(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
          is_mask_terrain=True,
          area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    cape = get_model_grid(data_source=data_source, data_name=data_name, var_name='cape', init_time=init_time, fhour=fhour, extent=map_extent)
    
    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        cape = mask_terrian(psfc, cape)

    if is_return_data:
        dataret = {'cape': cape}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_cape(cape, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
    
@date_init('init_time')
def cross_theta_fg_mpv(data_source='cmadaas', data_name='ecmwf', init_time=None, fhour=24,
                 levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                 st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=None, is_mask_terrain=True,
                 area=None, is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # points to 一维
    st_point = point_to1dim(st_point)
    ed_point = point_to1dim(ed_point)

    # 以st_point和ed_point包含的小区域
    minor_extent, map_extent = cross_extent(st_point, ed_point, area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=minor_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=minor_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=minor_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=minor_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    
    theta = read_theta3d(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=minor_extent)
    pres = mdgstda.gridstda_full_like_by_levels(u, levels)
    mpv = mdgcal.potential_vorticity_baroclinic(theta, pres, u, v)
    pressure_3d = mdgstda.gridstda_full_like_by_levels(tmp, tmp['level'].values)
    thta=mdgcal.thermal.potential_temperature(pressure_3d,tmp)
    fg=mdgcal.dynamic.frontogenesis(thta,u,v)

    res=rh.stda.horizontal_resolution
    if(lon_mean is not None):
        pnts_mean_lon=int(round(lon_mean/res))
    else:
        pnts_mean_lon=1
    if(lat_mean is not None):
        pnts_mean_lat=int(round(lat_mean/res))
    else:
        pnts_mean_lat=1

    rh=rh.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    thta=thta.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    mpv=mpv.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    fg=fg.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    
    cross_mpv = mdgcal.cross_section(mpv, st_point, ed_point)    
    cross_fg = mdgcal.cross_section(fg, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_thta = mdgcal.cross_section(thta, st_point, ed_point)
    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)
    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)
    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_thta, cross_td)

    # 隐藏被地形遮挡地区
    cross_terrain = None
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=minor_extent)
        if psfc is not None:
            psfc = psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
            # +form 3D psfc
            _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
            psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000
            cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
            cross_terrain = pressure - cross_psfc
            cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'theta':cross_theta, 'fg':cross_fg, 'mpv':cross_mpv, 'terrain':cross_terrain, 'hgt':hgt}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_theme_ne.draw_cross_theta_fg_mpv(cross_theta, cross_fg, cross_mpv, cross_terrain, hgt,
                                                  st_point=st_point, ed_point=ed_point,
                                                  map_extent=minor_extent, h_pos=h_pos,
                                                  **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
@date_init('init_time')
def cross_div_uv_wsp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                   levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                   st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=None, is_mask_terrain=True,
                   area=None, is_return_data=False, is_draw=True, **products_kwargs):

    ret = {}

    # points to 一维
    st_point = point_to1dim(st_point)
    ed_point = point_to1dim(ed_point)

    # 以st_point和ed_point包含的小区域
    minor_extent, map_extent = cross_extent(st_point, ed_point, area)

    div,u,v = read_div_uv_3d(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=minor_extent)
    # u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
    #                       var_name='u', levels=levels, extent=minor_extent)
    # v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
    #                       var_name='v', levels=levels, extent=minor_extent)
    prmsl = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='prmsl', extent=map_extent)
    
    res=div.stda.horizontal_resolution
    if(lon_mean is not None):
        pnts_mean_lon=int(round(lon_mean/res))
    else:
        pnts_mean_lon=1
    if(lat_mean is not None):
        pnts_mean_lat=int(round(lat_mean/res))
    else:
        pnts_mean_lat=1

    div=div.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    wsp = mdgcal.other.wind_speed(u, v)

    cross_div = mdgcal.cross_section(div, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_wsp = mdgcal.cross_section(wsp, st_point, ed_point)
    pressure = mdgstda.gridstda_full_like_by_levels(cross_u, cross_u['level'].values)
        
    # 隐藏被地形遮挡地区
    cross_terrain = None
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=minor_extent)
        if psfc is not None:
            psfc = psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
            # +form 3D psfc
            _, psfc_bdcst = xr.broadcast(u, psfc.squeeze())
            psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000
            cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
            cross_terrain = pressure - cross_psfc
            cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'div': cross_div, 'wsp': cross_wsp, 'u': cross_u, 'v': cross_v, 'terrain': cross_terrain, 'prmsl': prmsl}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_theme_ne.draw_cross_div_uv_wsp(cross_div, cross_wsp, cross_u, cross_v, cross_terrain, prmsl,
                                                st_point=st_point, ed_point=ed_point,
                                                map_extent=minor_extent, h_pos=h_pos,
                                                **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
@date_init('init_time')
def cross_wind_w_tmp_vvel_tmpadv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                      levels=[1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                      st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=None, is_mask_terrain=True,
                      area=None, is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # points to 一维
    st_point = point_to1dim(st_point)
    ed_point = point_to1dim(ed_point)

    # 以st_point和ed_point包含的小区域
    minor_extent, map_extent = cross_extent(st_point, ed_point, area)

    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=minor_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=minor_extent)

    w=read_w3d(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=minor_extent)

    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=minor_extent)
    vvel = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                             var_name='vvel', levels=levels, extent=minor_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)

    res=w.stda.horizontal_resolution
    if(lon_mean is not None):
        pnts_mean_lon=int(round(lon_mean/res))
    else:
        pnts_mean_lon=1
    if(lat_mean is not None):
        pnts_mean_lat=int(round(lat_mean/res))
    else:
        pnts_mean_lat=1
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    w=w.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()    
    vvel=vvel.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    tmpadv = mdgcal.var_advect(tmp, u, v)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_w = mdgcal.cross_section(w, st_point, ed_point)
    cross_t, cross_n = mdgcal.cross_section_components(cross_u, cross_v)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_vvel = mdgcal.cross_section(vvel, st_point, ed_point)
    cross_tmpadv = mdgcal.cross_section(tmpadv, st_point, ed_point)
    pressure = mdgstda.gridstda_full_like_by_levels(cross_tmp, cross_tmp['level'].values)

    # 隐藏被地形遮挡地区
    cross_terrain = None
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=minor_extent)
        if psfc is not None:
            psfc = psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
            # +form 3D psfc
            _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
            psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000
            cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
            cross_terrain = pressure - cross_psfc
            cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'tmpadv': cross_tmpadv, 'wind_n': cross_n,'wind_t': cross_t, 'w': cross_w, 'tmp': cross_tmp, 'vvel': cross_vvel, 'hgt': hgt, 'terrain': cross_terrain}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_theme_ne.draw_cross_wind_w_tmp_vvel_tmpadv(cross_tmpadv, cross_tmp, cross_t, cross_w, cross_vvel, cross_terrain, hgt,
                                                            st_point=st_point, ed_point=ed_point,
                                                            map_extent=minor_extent, h_pos=h_pos,
                                                            **products_kwargs)
        ret.update(drawret)
    if ret:
        return ret

@date_init('init_time')
def hgt_fcst_change(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    hgt_lev=500, is_mask_terrain=True,
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt_f = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    init_time0 = init_time-datetime.timedelta(days=1)
    fhour0 = fhour+24
    hgt_fp = get_model_grid(data_source=data_source, init_time=init_time0, fhour=fhour0, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    hgt_chg=hgt_f.isel(member=0,level=0,time=0,dtime=0)-hgt_fp.isel(member=0,level=0,time=0,dtime=0)
    hgt_chg.attrs['var_cn_name']='24小时变高'
    hgt_chg.attrs['var_units']='dagpm'


    if is_return_data:
        dataret = {'hgt_f': hgt_f, 'hgt_fp': hgt_fp, 'hgt_chg': hgt_chg}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt_f = mask_terrian(psfc, hgt_f)
        hgt_fp = mask_terrian(psfc, hgt_fp)
        hgt_chg = mask_terrian(psfc, hgt_chg)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_hgt_fcst_change(hgt_f, hgt_fp, hgt_chg, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def wind_fcst_change(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                     wind_lev=850, is_mask_terrain=True,
                     area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u_f = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=wind_lev, extent=map_extent)
    v_f = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=wind_lev, extent=map_extent)
    init_time0 = init_time-datetime.timedelta(days=1)
    fhour0 = fhour+24
    u_fp = get_model_grid(data_source=data_source, init_time=init_time0, fhour=fhour0, data_name=data_name, var_name='u', level=wind_lev, extent=map_extent)
    v_fp = get_model_grid(data_source=data_source, init_time=init_time0, fhour=fhour0, data_name=data_name, var_name='v', level=wind_lev, extent=map_extent)
    wsp_f = mdgcal.wind_speed(u_f,v_f)
    wsp_fp = mdgcal.wind_speed(u_fp,v_fp)
    wsp_chg=wsp_f.isel(member=0,level=0,time=0,dtime=0)-wsp_fp.isel(member=0,level=0,time=0,dtime=0)
    wsp_chg.attrs['var_cn_name']='风速预报调整'
    wsp_chg.attrs['var_units']='m/s'


    if is_return_data:
        dataret = {'wsp_f': wsp_f, 'wsp_fp': wsp_fp, 'wsp_chg': wsp_chg, 'u_f': u_f, 'v_f': v_f, 'u_fp': u_fp, 'v_f': v_fp}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        wsp_f = mask_terrian(psfc, wsp_f)
        wsp_fp = mask_terrian(psfc, wsp_fp)
        wsp_chg = mask_terrian(psfc, wsp_chg)
        u_f = mask_terrian(psfc, u_f)
        v_f = mask_terrian(psfc, v_f)
        u_fp = mask_terrian(psfc, u_fp)
        v_fp = mask_terrian(psfc, v_fp)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_wind_fcst_change(wsp_f, wsp_fp, wsp_chg, u_f, v_f, u_fp, v_fp, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def prmsl_fcst_change(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                      is_mask_terrain=True,
                      area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    prmsl_f = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='prmsl', extent=map_extent)
    init_time0 = init_time-datetime.timedelta(days=1)
    fhour0 = fhour+24
    prmsl_fp = get_model_grid(data_source=data_source, init_time=init_time0, fhour=fhour0, data_name=data_name, var_name='prmsl', extent=map_extent)
    prmsl_chg=prmsl_f.isel(member=0,level=0,time=0,dtime=0)-prmsl_fp.isel(member=0,level=0,time=0,dtime=0)
    prmsl_chg.attrs['var_cn_name']='24小时变压'
    prmsl_chg.attrs['var_units']='hPa'


    if is_return_data:
        dataret = {'prmsl_f': prmsl_f, 'prmsl_fp': prmsl_fp, 'prmsl_chg': prmsl_chg}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        prmsl_f = mask_terrian(psfc, prmsl_f)
        prmsl_fp = mask_terrian(psfc, prmsl_fp)
        prmsl_chg = mask_terrian(psfc, prmsl_chg)

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_prmsl_fcst_change(prmsl_f, prmsl_fp, prmsl_chg, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


def obs_wind_div_td(data_source='cassandra', data_name='sfc_chn_hor', obs_time=None,
                    area='全国',is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    td = get_obs_stations(obs_time=obs_time,data_name=data_name,var_name='td',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    td['sfc_chn_hor'].loc[td['sfc_chn_hor']>20]==np.nan
    # td[f'{data_name}'].loc[td[f'{data_name}']>20]==np.nan
    
    temp = get_obs_stations(obs_time=obs_time,data_name=data_name,var_name='gust10m',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    tempdir = get_obs_stations(obs_time=obs_time,data_name=data_name,var_name='gustdir10m',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    temp=temp.where(temp['id'].isin(list(set(temp['id']).intersection(tempdir['id'])))).dropna().sort_values('lon').reset_index(drop=True)
    tempdir=tempdir.where(tempdir['id'].isin(list(set(tempdir['id']).intersection(temp['id'])))).dropna().sort_values('lon').reset_index(drop=True)
    gust10m=temp
    gustdir10m=tempdir
    gustu10m,gustv10m=mdgcal.other.wind_components(gust10m,gustdir10m)
    
    grid0 = meb.grid([map_extent[0]-5,map_extent[1]+5,0.1],[map_extent[2]-5,map_extent[3]+5,0.1])
    td_grid=meb.interp_sg_cressman(td,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    gustu10m_grid=meb.interp_sg_cressman(gustu10m,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    gustv10m_grid=meb.interp_sg_cressman(gustv10m,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    div = mdgcal.divergence(gustu10m_grid, gustv10m_grid)
    
    td_grid.attrs['var_cn_name']='2米露点温度'
    td_grid.attrs['var_units']='℃'
    
    if is_return_data:
        dataret = {'div': div, 'gustu10m': gustu10m, 'gustv10m': gustv10m, 'td': td_grid}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_obs_wind_div_td(gustu10m, gustv10m, div, td_grid, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
    

def obs_wind_div_tmp(data_source='cassandra', data_name='sfc_chn_hor', obs_time=None,
                     area='全国',is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    tmp = get_obs_stations(obs_time=obs_time,data_name=data_name,var_name='tmp',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    tmp['sfc_chn_hor'].loc[tmp['sfc_chn_hor']>20]==np.nan
    # tmp[f'{data_name}'].loc[tmp[f'{data_name}']>20]==np.nan
    
    temp = get_obs_stations(obs_time=obs_time,data_name=data_name,var_name='gust10m',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    tempdir = get_obs_stations(obs_time=obs_time,data_name=data_name,var_name='gustdir10m',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    temp=temp.where(temp['id'].isin(list(set(temp['id']).intersection(tempdir['id'])))).dropna().sort_values('lon').reset_index(drop=True)
    tempdir=tempdir.where(tempdir['id'].isin(list(set(tempdir['id']).intersection(temp['id'])))).dropna().sort_values('lon').reset_index(drop=True)
    gust10m=temp
    gustdir10m=tempdir
    gustu10m,gustv10m=mdgcal.other.wind_components(gust10m,gustdir10m)
    
    grid0 = meb.grid([map_extent[0]-5,map_extent[1]+5,0.1],[map_extent[2]-5,map_extent[3]+5,0.1])
    tmp_grid=meb.interp_sg_cressman(tmp,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    gustu10m_grid=meb.interp_sg_cressman(gustu10m,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    gustv10m_grid=meb.interp_sg_cressman(gustv10m,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    div = mdgcal.divergence(gustu10m_grid, gustv10m_grid)
    
    tmp_grid.attrs['var_cn_name']='温度'
    tmp_grid.attrs['var_units']='℃'
    
    if is_return_data:
        dataret = {'div': div, 'gustu10m': gustu10m, 'gustv10m': gustv10m, 'tmp': tmp_grid}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_obs_wind_div_tmp(gustu10m, gustv10m, div, tmp_grid, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
    

def obs_wind_wsp_div_dtmp(data_source='cassandra', data_name='sfc_chn_hor', obs_time=None,
                          area='全国',is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    tmp1 = get_obs_stations(obs_time=obs_time,data_name=data_name,var_name='tmp',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    obs_time0 = obs_time-datetime.timedelta(hours=1)
    tmp0 = get_obs_stations(obs_time=obs_time0,data_name=data_name,var_name='tmp',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    
    temp = get_obs_stations(obs_time=obs_time,data_name=data_name,var_name='gust10m',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    tempdir = get_obs_stations(obs_time=obs_time,data_name=data_name,var_name='gustdir10m',data_source=data_source,extent=map_extent,is_save_other_info=None).dropna()
    temp=temp.where(temp['id'].isin(list(set(temp['id']).intersection(tempdir['id'])))).dropna().sort_values('lon').reset_index(drop=True)
    tempdir=tempdir.where(tempdir['id'].isin(list(set(tempdir['id']).intersection(temp['id'])))).dropna().sort_values('lon').reset_index(drop=True)
    gust10m=temp
    gustdir10m=tempdir
    gustu10m,gustv10m=mdgcal.other.wind_components(gust10m,gustdir10m)
    
    grid0 = meb.grid([map_extent[0]-5,map_extent[1]+5,0.1],[map_extent[2]-5,map_extent[3]+5,0.1])
    tmp1_grid=meb.interp_sg_cressman(tmp1,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    tmp0_grid=meb.interp_sg_cressman(tmp0,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    dtmp_grid=tmp1_grid.isel(member=0,level=0,time=0,dtime=0)-tmp0_grid.isel(member=0,level=0,time=0,dtime=0)
    gustu10m_grid=meb.interp_sg_cressman(gustu10m,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    gustv10m_grid=meb.interp_sg_cressman(gustv10m,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    div = mdgcal.divergence(gustu10m_grid, gustv10m_grid)
    gust10m_grid=meb.interp_sg_cressman(gust10m,grid = grid0,r_list = [1000,200,100,50],nearNum = 100)
    
    dtmp_grid.attrs['var_cn_name']='1小时变温'
    dtmp_grid.attrs['var_units']='℃'
    
    if is_return_data:
        dataret = {'div': div, 'gustu10m': gustu10m, 'gustv10m': gustv10m, 'dtmp': dtmp_grid, 'wsp':gust10m_grid}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_theme_ne.draw_obs_wind_wsp_div_dtmp(gustu10m, gustv10m, gust10m_grid, div, dtmp_grid, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
        
        
@date_init('init_time')
def obs_rain24(data_source='cassandra', data_name='cldas', init_time=None, fhour=24, atime=6, hgt_lev=500, area='全国',
             is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}
    map_extent = get_map_area(area)

    rain = read_rain(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          atime=atime, extent=map_extent)
    
    rain=rain.rolling(lon=1, lat=1, min_periods=1, center=True).mean(skipna=True)

    if is_return_data:
        dataret = {'rain': rain}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_theme_ne.draw_obs_rain24(rain, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret