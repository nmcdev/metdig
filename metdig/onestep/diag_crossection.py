# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import datetime

from metdig.io import get_model_grid
from metdig.io import get_model_3D_grid
from metdig.io import get_model_3D_grids

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init
from metdig.onestep.complexgrid_var.pv_div_uv import read_pv_div_uv
from metdig.onestep.complexgrid_var.div_uv import read_div_uv_4d,read_div_uv_3d
from metdig.onestep.complexgrid_var.vort_uv import read_vort_uv_4d
from metdig.onestep.complexgrid_var.spfh import read_spfh_4D,read_spfh_3D
from metdig.onestep.complexgrid_var.theta import read_theta3d
from metdig.onestep.complexgrid_var.w import read_w3d
from metdig.onestep.complexgrid_var.vvel import read_vvel3ds,read_vvel3d


from metdig.products import diag_crossection as draw_cross

import metdig.cal as mdgcal
import metdig.utl as mdgstda

__all__ = [
    'wind_theta_wvfldiv',
    'wind_theta_wvfl',
    'wind_theta_wsp',
    'wind_theta_vort',
    'wind_theta_fg',
    'wind_thetaes_mpvg',
    'wind_theta_w',
    'time_wind_qcld_qsn_tmp',
    'time_wind_qcld_qice_tmp',
    'wind_w_theta_spfh',
    'time_div_vort_spfh_uv',
    'time_div_vort_rh_uv',
    'time_wind_tmpadv_tmp',
    'wind_tmpadv_tmp',
    'wind_w_tmpadv_tmp',
    'time_wind_vortadv_tmp',
    'wind_vortadv_tmp',
    'wind_theta_mpv',
    'wind_theta_absv',
    'wind_theta_rh',
    'wind_theta_spfh',
    'wind_tmp_rh_vvel',
    'time_rh_uv_theta',
    'time_rh_uv_tmp_vvel',
    'wind_theta_div'
]

@date_init('init_time')
def wind_theta_wvfldiv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    #lon_mean 经向平均 当为None时不平均
    #lat_mean 纬向平均 当为None时不平均
    
    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    spfh = read_spfh_3D(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)
    wvfldiv=mdgcal.water_wapor_flux_divergence(u,v,spfh)


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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_wvfldiv = mdgcal.cross_section(wvfldiv, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'wvfldiv':cross_wvfldiv, 'theta': cross_theta, 'u': cross_u, 'v': cross_v, 'terrain':cross_terrain, 'hgt': hgt}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_theta_wvfldiv(cross_wvfldiv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def wind_theta_wvfl(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    #lon_mean 经向平均 当为None时不平均
    #lat_mean 纬向平均 当为None时不平均
    
    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    spfh = read_spfh_3D(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)
    wsp=mdgcal.wind_speed(u,v)
    wvfl=mdgcal.cal_ivt_singlelevel(wsp,spfh)


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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_wvfl = mdgcal.cross_section(wvfl, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'wvfl':cross_wvfl, 'theta': cross_theta, 'u': cross_u, 'v': cross_v, 'terrain':cross_terrain, 'hgt': hgt}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_theta_wvfl(cross_wvfl, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

if __name__ == '__main__':
    init_time=datetime.datetime(2022,7,4,8)
    wind_theta_wvfl(st_point=[33.91,115.51],
        init_time=init_time,data_name='era5',data_source='cds',fhour=0)

@date_init('init_time')
def wind_theta_wsp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    #lon_mean 经向平均 当为None时不平均
    #lat_mean 纬向平均 当为None时不平均
    
    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    wsp = mdgcal.other.wind_speed(u, v)

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_wsp = mdgcal.cross_section(wsp, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'wsp':cross_wsp, 'theta': cross_theta, 'u': cross_u, 'v': cross_v, 'terrain':cross_terrain, 'hgt': hgt}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_theta_wsp(cross_wsp, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def wind_theta_vort(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    #lon_mean 经向平均 当为None时不平均
    #lat_mean 纬向平均 当为None时不平均
    
    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    vort = mdgcal.vorticity(u, v)

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_vort = mdgcal.cross_section(vort, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'vort': cross_vort, 'u': cross_u, 'v': cross_v, 'theta': cross_theta, 'hgt': hgt, 'terrain':cross_terrain}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_theta_absv(cross_vort, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def wind_theta_fg(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    fg=fg.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_fg = mdgcal.cross_section(fg, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp, 'hgt': hgt, 'psfc': psfc}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_theta_fg(cross_u, cross_v, cross_theta, cross_fg,  cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def wind_thetaes_mpvg(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                   levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                   st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                   area='全国', is_return_data=False, is_draw=True, **products_kwargs):

    ret = {}

    # get area
    map_extent = get_map_area(area)

    theta = read_theta3d(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=map_extent)
    # mpv, _div, u, v = read_pv_div_uv(data_source=data_source, init_time=init_time, fhour=fhour,
    #                                  data_name=data_name, lvl_ana=levels, levels=levels, extent=map_extent)

    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='hgt', levels=levels, extent=map_extent)
    ug,vg=mdgcal.dynamic.geostrophic_wind(hgt)
    pressure = mdgstda.gridstda_full_like_by_levels(hgt, hgt.level.values.tolist())
    thetaes=mdgcal.thermal.saturation_equivalent_potential_temperature(pressure,tmp)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)
    mpvg=mdgcal.dynamic.potential_vorticity_baroclinic(thetaes,pressure,ug,vg)
    
    res=mpvg.stda.horizontal_resolution
    if(lon_mean is not None):
        pnts_mean_lon=int(round(lon_mean/res))
    else:
        pnts_mean_lon=1
    if(lat_mean is not None):
        pnts_mean_lat=int(round(lat_mean/res))
    else:
        pnts_mean_lat=1

    theta=theta.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    ug=ug.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    vg=vg.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    mpvg=mpvg.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()


    if is_return_data:
        dataret = {'theta': theta, 'u': u, 'v': v, 'mpvg': mpvg, 'hgt': hgt, 'psfc': psfc}
        ret.update({'data': dataret})

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(theta, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_theta = mdgcal.cross_section(theta, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_mpvg = mdgcal.cross_section(mpvg, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_theta, cross_theta['level'].values)
    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_draw:
        drawret = draw_cross.draw_wind_thetaes_mpvg(cross_mpvg, cross_theta, cross_u, cross_v, cross_terrain, hgt.sel(level=[500]),
                                      st_point=st_point, ed_point=ed_point,
                                      lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                      map_extent=map_extent, h_pos=h_pos,
                                      **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def wind_theta_w(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    # vvel = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
    #                         var_name='vvel', levels=levels, extent=map_extent)
    # spfh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
    #                         var_name='spfh', levels=levels, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

    # w = mdgcal.vertical_velocity(vvel, tmp, spfh)

    w=read_w3d(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    rh=rh.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    w=w.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_w = mdgcal.cross_section(w, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp, 'hgt': hgt, 'psfc': psfc}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_theta_w(cross_u, cross_v, cross_theta, cross_w,  cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def wind_theta_div(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                  levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                  st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                  area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    div,u,v = read_div_uv_3d(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=map_extent)

    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    div=div.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_div = mdgcal.cross_section(div, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'div':cross_div, 'theta':cross_theta, 'u':cross_u, 'v':cross_v, 'terrain':cross_terrain, 'hgt':hgt}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_theta_div(cross_div, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                     st_point=st_point, ed_point=ed_point,
                                     lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                     map_extent=map_extent, h_pos=h_pos,
                                     **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time', method=date_init.special_series_set)
def time_wind_qcld_qsn_tmp(data_source='cassandra', data_name='cma_gfs', init_time=None, fhours=range(0, 48, 3),
                         levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                         points={'lon': [118], 'lat': [34]}, mean_area=None,
                         is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                           var_name='u', levels=levels, extent=mean_area)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                          var_name='v', levels=levels, extent=mean_area)
    qcld = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                        var_name='qcld', levels=levels, extent=mean_area)
    qsn = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                        var_name='qsn', levels=levels, extent=mean_area)
    psfc = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='psfc', extent=mean_area)
    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours,
                             data_name=data_name, var_name='tmp', levels=levels, extent=mean_area)

    if(mean_area == None):
        u = u.interp(lon=points['lon'], lat=points['lat'])
        v = v.interp(lon=points['lon'], lat=points['lat'])
        qsn = qsn.interp(lon=points['lon'], lat=points['lat'])
        qcld = qcld.interp(lon=points['lon'], lat=points['lat'])
        tmp = tmp.interp(lon=points['lon'], lat=points['lat'])
        psfc = psfc.interp(lon=points['lon'], lat=points['lat'])

    _, pressure = xr.broadcast(v, v['level'])
    terrain = pressure - psfc.values
    terrain.attrs['var_units'] = ''
    if is_return_data:
        dataret = {'u': u, 'v': v, 'qsn' : qsn, 'qcld':qcld,'tmp': tmp}
        ret.update({'data': dataret})
    if is_draw:
        drawret = draw_cross.draw_time_wind_qcld_qsn_tmp(qcld,qsn, tmp, u, v, terrain, **products_kwargs)
        ret.update(drawret)
    if ret:
        return ret


@date_init('init_time', method=date_init.special_series_set)
def time_wind_qcld_qice_tmp(data_source='cassandra', data_name='cma_gfs', init_time=None, fhours=range(0, 48, 3),
                         levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                         points={'lon': [118], 'lat': [34]}, mean_area=None,
                         is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                           var_name='u', levels=levels, extent=mean_area)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                          var_name='v', levels=levels, extent=mean_area)
    qcld = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                        var_name='qcld', levels=levels, extent=mean_area)
    qice = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                        var_name='qice', levels=levels, extent=mean_area)
    psfc = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='psfc', extent=mean_area)
    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours,
                             data_name=data_name, var_name='tmp', levels=levels, extent=mean_area)

    if(mean_area == None):
        u = u.interp(lon=points['lon'], lat=points['lat'])
        v = v.interp(lon=points['lon'], lat=points['lat'])
        qice = qice.interp(lon=points['lon'], lat=points['lat'])
        qcld = qcld.interp(lon=points['lon'], lat=points['lat'])
        tmp = tmp.interp(lon=points['lon'], lat=points['lat'])
        psfc = psfc.interp(lon=points['lon'], lat=points['lat'])

    _, pressure = xr.broadcast(v, v['level'])
    terrain = pressure - psfc.values
    terrain.attrs['var_units'] = ''
    if is_return_data:
        dataret = {'u': u, 'v': v, 'qice' : qice, 'qcld':qcld,'tmp': tmp}
        ret.update({'data': dataret})
    if is_draw:
        drawret = draw_cross.draw_time_wind_qcld_qice_tmp(qcld,qice, tmp, u, v, terrain, **products_kwargs)
        ret.update(drawret)
    if ret:
        return ret

@date_init('init_time')
def wind_w_theta_spfh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    vvel = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='vvel', levels=levels, extent=map_extent)
    spfh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='spfh', levels=levels, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    vvel=vvel.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    spfh=spfh.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    w = mdgcal.vertical_velocity(vvel, tmp, spfh)

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_w = mdgcal.cross_section(w, st_point, ed_point)
    cross_t, cross_n = mdgcal.cross_section_components(cross_u, cross_v)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)
    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)
    cross_spfh = mdgcal.specific_humidity_from_dewpoint(pressure, cross_td)
    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    ratio = np.nanmax(np.abs(cross_t.values))/np.nanmax(np.abs(cross_w.values))
    if is_return_data:
        dataret = {'spfh': cross_spfh, 'wind_n': cross_n, 'wind_t': cross_t, 'wind_w': cross_w, 'terrain': cross_terrain, 'hgt': hgt}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_w_theta_spfh(cross_spfh, cross_theta, cross_t, cross_w*ratio, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time', method=date_init.special_series_set)
def time_div_vort_spfh_uv(data_source='cassandra', data_name='ecmwf', init_time=None, fhours=range(0, 48, 3),
                          levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                          points={'lon': [113], 'lat': [22]},
                          is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    div, u, v = read_div_uv_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels)
    vort, u, v = read_vort_uv_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels)
    spfh = read_spfh_4D(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels)
    psfc = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='psfc')

    if is_return_data:
        dataret = {'spfh': spfh, 'u': u, 'v': v, 'tmp': div, 'vort': vort}
        ret.update({'data': dataret})

    u = u.interp(lon=points['lon'], lat=points['lat'])
    v = v.interp(lon=points['lon'], lat=points['lat'])
    div = div.interp(lon=points['lon'], lat=points['lat'])
    vort = vort.interp(lon=points['lon'], lat=points['lat'])
    spfh = spfh.interp(lon=points['lon'], lat=points['lat'])
    psfc = psfc.interp(lon=points['lon'], lat=points['lat'])
    _, pressure = xr.broadcast(v, v['level'])
    terrain= mask_terrian(psfc, pressure,get_terrain=True)
    terrain.attrs['var_units'] = ''
    if is_draw:
        drawret = draw_cross.draw_time_div_vort_spfh_uv(div, vort, spfh, u, v, terrain, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time', method=date_init.special_series_set)
def time_div_vort_rh_uv(data_source='cassandra', data_name='ecmwf', init_time=None, fhours=range(0, 48, 3),
                        levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                        points={'lon': [90], 'lat': [30]},
                        is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    div, u, v = read_div_uv_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels)
    vort, u, v = read_vort_uv_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels)
    psfc = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='psfc')
    rh = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='rh', levels=levels)

    u = u.interp(lon=points['lon'], lat=points['lat'])
    v = v.interp(lon=points['lon'], lat=points['lat'])
    div = div.interp(lon=points['lon'], lat=points['lat'])
    vort = vort.interp(lon=points['lon'], lat=points['lat'])
    rh = rh.interp(lon=points['lon'], lat=points['lat'])
    psfc = psfc.interp(lon=points['lon'], lat=points['lat'])
    _, pressure = xr.broadcast(v, v['level'])
    terrain= mask_terrian(psfc, pressure,get_terrain=True)
    terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'div': div, 'vort': vort,'terrain':terrain}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_time_div_vort_rh_uv(div, vort, rh, u, v, terrain, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time', method=date_init.special_series_set)
def time_wind_tmpadv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhours=range(0, 48, 3),
                         levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                         points={'lon': [90], 'lat': [30]}, mean_area=None,
                         is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                           var_name='u', levels=levels, extent=mean_area)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                           var_name='v', levels=levels, extent=mean_area)
    psfc = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='psfc', extent=mean_area)
    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours,
                             data_name=data_name, var_name='tmp', levels=levels, extent=mean_area)
    tmpadv = mdgcal.var_advect(tmp, u, v)

    if(mean_area == None):
        u = u.interp(lon=points['lon'], lat=points['lat'])
        v = v.interp(lon=points['lon'], lat=points['lat'])
        tmpadv = tmpadv.interp(lon=points['lon'], lat=points['lat'])
        tmp = tmp.interp(lon=points['lon'], lat=points['lat'])
        psfc = psfc.interp(lon=points['lon'], lat=points['lat'])

    _, pressure = xr.broadcast(v, v['level'])
    terrain = pressure - psfc.values
    terrain.attrs['var_units'] = ''
    if is_return_data:
        dataret = {'u': u, 'v': v, 'tmp': tmp, 'tmpadv': tmpadv}
        ret.update({'data': dataret})
    if is_draw:
        drawret = draw_cross.draw_time_wind_tmpadv_tmp(tmpadv, tmp, u, v, terrain, **products_kwargs)
        ret.update(drawret)
    if ret:
        return ret

@date_init('init_time')
def wind_tmpadv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

    res=tmp.stda.horizontal_resolution
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
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()                          

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    tmpadv = mdgcal.var_advect(tmp, u, v)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_tmpadv = mdgcal.cross_section(tmpadv, st_point, ed_point)
    pressure = mdgstda.gridstda_full_like_by_levels(cross_tmp, cross_tmp['level'].values)
    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'tmpadv': cross_tmpadv, 'u': cross_u, 'v': cross_v, 'tmp': cross_tmp, 'hgt': hgt, 'psfc': cross_psfc}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_tmpadv_tmp(cross_tmpadv, cross_tmp, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)
    if ret:
        return ret


@date_init('init_time')
def wind_w_tmpadv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                      levels=[1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                      st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                      area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)

    w=read_w3d(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=map_extent)

    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    tmpadv = mdgcal.var_advect(tmp, u, v)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_w = mdgcal.cross_section(w, st_point, ed_point)
    cross_t, cross_n = mdgcal.cross_section_components(cross_u, cross_v)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_tmpadv = mdgcal.cross_section(tmpadv, st_point, ed_point)
    pressure = mdgstda.gridstda_full_like_by_levels(cross_tmp, cross_tmp['level'].values)
    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    ratio = np.nanmax(np.abs(cross_t.values))/np.nanmax(np.abs(cross_w.values))
    if is_return_data:
        dataret = {'tmpadv': cross_tmpadv, 'wind_n': cross_n,'wind_t': cross_t, 'w': cross_w, 'tmp': cross_tmp, 'hgt': hgt, 'psfc': cross_psfc}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_w_tmpadv_tmp(cross_tmpadv, cross_tmp, cross_t, cross_w*ratio, cross_terrain, hgt,
                                         st_point=st_point, ed_point=ed_point,
                                         lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                         map_extent=map_extent, h_pos=h_pos,
                                         **products_kwargs)
        ret.update(drawret)
    if ret:
        return ret

@date_init('init_time', method=date_init.special_series_set)
def time_wind_vortadv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhours=range(0, 48, 3),
                          levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                          points={'lon': [90], 'lat': [30]}, mean_area=None,
                          is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    vort, u, v = read_vort_uv_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=mean_area)
    psfc = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='psfc', extent=mean_area)
    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours,
                             data_name=data_name, var_name='tmp', levels=levels, extent=mean_area)
    vortadv = mdgcal.var_advect(vort, u, v)

    if(mean_area == None):
        u = u.interp(lon=points['lon'], lat=points['lat'])
        v = v.interp(lon=points['lon'], lat=points['lat'])
        vortadv = vortadv.interp(lon=points['lon'], lat=points['lat'])
        tmp = tmp.interp(lon=points['lon'], lat=points['lat'])
        psfc = psfc.interp(lon=points['lon'], lat=points['lat'])

    _, pressure = xr.broadcast(v, v['level'])
    terrain = pressure - psfc.values
    terrain.attrs['var_units'] = ''
    if is_return_data:
        dataret = {'u': u, 'v': v, 'tmp': tmp, 'vortadv': vortadv}
        ret.update({'data': dataret})
    if is_draw:
        drawret = draw_cross.draw_time_wind_vortadv_tmp(vortadv, tmp, u, v, terrain, **products_kwargs)
        ret.update(drawret)
    if ret:
        return ret

@date_init('init_time')
def wind_vortadv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                     levels=[1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                     st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                     area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

    res=tmp.stda.horizontal_resolution
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
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    vort = mdgcal.vorticity(u, v)
    vortadv = mdgcal.var_advect(vort, u, v)

    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_vortadv = mdgcal.cross_section(vortadv, st_point, ed_point)
    pressure = mdgstda.gridstda_full_like_by_levels(cross_tmp, cross_tmp['level'].values)
    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'vortadv': cross_vortadv, 'u': cross_u, 'v': cross_v, 'tmp': cross_tmp, 'hgt': hgt, 'psfc': cross_psfc}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_vortadv_tmp(cross_vortadv, cross_tmp, cross_u, cross_v, cross_terrain, hgt,
                                        st_point=st_point, ed_point=ed_point,
                                        lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                        map_extent=map_extent, h_pos=h_pos,
                                        **products_kwargs)
        ret.update(drawret)
    if ret:
        return ret


@date_init('init_time')
def wind_theta_mpv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                   levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                   st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                   area='全国', is_return_data=False, is_draw=True, **products_kwargs):

    ret = {}

    # get area
    map_extent = get_map_area(area)

    theta = read_theta3d(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=map_extent)
    mpv, _div, u, v = read_pv_div_uv(data_source=data_source, init_time=init_time, fhour=fhour,
                                     data_name=data_name, lvl_ana=levels, levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

    res=mpv.stda.horizontal_resolution
    if(lon_mean is not None):
        pnts_mean_lon=int(round(lon_mean/res))
    else:
        pnts_mean_lon=1
    if(lat_mean is not None):
        pnts_mean_lat=int(round(lat_mean/res))
    else:
        pnts_mean_lat=1

    theta=theta.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    mpv=mpv.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(theta, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_theta = mdgcal.cross_section(theta, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_mpv = mdgcal.cross_section(mpv, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_theta, cross_theta['level'].values)
    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'theta': cross_theta, 'u': cross_u, 'v': cross_v, 'mpv': cross_mpv, 'hgt': hgt, 'terrain': cross_terrain}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_theta_mpv(cross_mpv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                      st_point=st_point, ed_point=ed_point,
                                      lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                      map_extent=map_extent, h_pos=h_pos,
                                      **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def wind_theta_absv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    #lon_mean 经向平均 当为None时不平均
    #lat_mean 纬向平均 当为None时不平均
    
    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()


    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp, 'hgt': hgt, 'psfc': psfc}
        ret.update({'data': dataret})

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    absv = mdgcal.absolute_vorticity(u, v)

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)
    cross_absv = mdgcal.cross_section(absv, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_draw:
        drawret = draw_cross.draw_wind_theta_absv(cross_absv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def wind_theta_rh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                  levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                  st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                  area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_return_data:
        dataret = {'rh': cross_rh, 'u': cross_u, 'v': cross_v, 'theta': cross_theta, 'terrain':cross_terrain,'hgt': hgt}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_cross.draw_wind_theta_rh(cross_rh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                     st_point=st_point, ed_point=ed_point,
                                     lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                     map_extent=map_extent, h_pos=h_pos,
                                     **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import pandas as pd
    wind_theta_rh(data_name='cma_ra',fhour=0,data_source='cmadaas',init_time=datetime.datetime(2022,7,6,8),
        st_point=[43.4520,110.3548],ed_point=[30.7775,124.4222],area='华北',
        levels=[200,225,250,275,300,325,350,375,400,425,450 ,475,500,525,550,575,600,625,650,675,700,725,750,775,800,825,850,875,900,925,950,975,1000][::-1])
    plt.show()

@date_init('init_time')
def wind_theta_spfh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                    st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                    area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp, 'hgt': hgt, 'psfc': psfc}
        ret.update({'data': dataret})

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)

    cross_td = mdgcal.dewpoint_from_relative_humidity(cross_tmp, cross_rh)

    pressure = mdgstda.gridstda_full_like_by_levels(cross_rh, cross_tmp['level'].values)

    cross_spfh = mdgcal.specific_humidity_from_dewpoint(pressure, cross_td)

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_draw:
        drawret = draw_cross.draw_wind_theta_spfh(cross_spfh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def wind_tmp_rh_vvel(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],lon_mean=None,lat_mean=None,
                st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=map_extent)
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    vvel = read_vvel3d(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

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
    u=u.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    v=v.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    vvel=vvel.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    tmp=tmp.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()
    psfc=psfc.rolling(lon=pnts_mean_lon, lat=pnts_mean_lat, min_periods=1, center=True).mean()

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp, 'hgt': hgt, 'psfc': psfc}
        ret.update({'data': dataret})

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000  # (1, 12, 1, 1, 901, 1801)

    cross_rh = mdgcal.cross_section(rh, st_point, ed_point)
    cross_u = mdgcal.cross_section(u, st_point, ed_point)
    cross_v = mdgcal.cross_section(v, st_point, ed_point)
    cross_tmp = mdgcal.cross_section(tmp, st_point, ed_point)
    cross_vvel = mdgcal.cross_section(vvel, st_point, ed_point)
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)

    _, pressure = xr.broadcast(cross_rh, cross_tmp['level'])
    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    cross_rh = cross_rh.where(cross_rh < 100, 100)  # 大于100的赋值成100

    if is_draw:
        drawret = draw_cross.draw_wind_tmp_rh_vvel(cross_rh, cross_tmp, cross_u, cross_v, cross_vvel,cross_terrain, hgt,
                                   st_point=st_point, ed_point=ed_point,
                                   lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                   map_extent=map_extent, h_pos=h_pos,
                                   **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time', method=date_init.special_series_set)
def time_rh_uv_theta(data_source='cassandra', data_name='ecmwf', init_time=None, fhours=range(0, 48, 3),
                     levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                     points={'lon': [116.3833], 'lat': [39.9]},
                     is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='tmp', levels=levels)
    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='u', levels=levels)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='v', levels=levels)
    rh = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='rh', levels=levels)
    psfc = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='psfc')

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp}
        ret.update({'data': dataret})

    tmp = tmp.interp(lon=points['lon'], lat=points['lat'])
    u = u.interp(lon=points['lon'], lat=points['lat'])
    v = v.interp(lon=points['lon'], lat=points['lat'])
    rh = rh.interp(lon=points['lon'], lat=points['lat'])
    psfc = psfc.interp(lon=points['lon'], lat=points['lat'])

    td = mdgcal.dewpoint_from_relative_humidity(tmp, rh)
    pressure = mdgstda.gridstda_full_like_by_levels(rh, rh['level'].values)
    theta = mdgcal.equivalent_potential_temperature(pressure, tmp, td)

    _, pressure = xr.broadcast(v, v['level'])
    terrain= mask_terrian(psfc, pressure,get_terrain=True)
    terrain.attrs['var_units'] = ''

    if is_draw:
        drawret = draw_cross.draw_time_rh_uv_theta(rh, u, v, theta,terrain, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time', method=date_init.special_series_set)
def time_rh_uv_tmp_vvel(data_source='cassandra', data_name='ecmwf', init_time=None, fhours=range(0, 48, 3),
                   levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                   points={'lon': [115], 'lat': [22.3]},mean_area=None,
                   is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}
    extent=[min(points['lon'])-1,max(points['lon'])+1,min(points['lat'])-1,min(points['lat'])+1]
    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='tmp', levels=levels,extent=extent)
    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='u', levels=levels,extent=extent)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='v', levels=levels,extent=extent)
    rh = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='rh', levels=levels,extent=extent)
    # vvel = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='vvel', levels=levels,extent=extent)
    vvel = read_vvel3ds(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels,extent=extent)
    psfc = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='psfc',extent=extent)

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp, 'psfc': psfc}
        ret.update({'data': dataret})

    if (mean_area==None):
        tmp = tmp.interp(lon=points['lon'], lat=points['lat'])
        u = u.interp(lon=points['lon'], lat=points['lat'])
        v = v.interp(lon=points['lon'], lat=points['lat'])
        rh = rh.interp(lon=points['lon'], lat=points['lat'])
        vvel = vvel.interp(lon=points['lon'], lat=points['lat'])
        psfc = psfc.interp(lon=points['lon'], lat=points['lat'])

    _, pressure = xr.broadcast(v, v['level'])
    terrain= mask_terrian(psfc, pressure,get_terrain=True)
    terrain.attrs['var_units'] = ''

    rh = rh.where(rh < 100, 100)  # 大于100的赋值成100

    if is_draw:
        drawret = draw_cross.draw_time_rh_uv_tmp_vvel(rh, u, v, tmp, vvel, terrain, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret