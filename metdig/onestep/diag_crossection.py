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
from metdig.onestep.complexgrid_var.div_uv import read_div_uv_4d
from metdig.onestep.complexgrid_var.vort_uv import read_vort_uv_4d
from metdig.onestep.complexgrid_var.spfh import read_spfh_4D,read_spfh_3D
from metdig.onestep.complexgrid_var.theta import read_theta3d

from metdig.products.diag_crossection import draw_wind_tmp_rh
from metdig.products.diag_crossection import draw_wind_theta_absv
from metdig.products.diag_crossection import draw_wind_theta_rh
from metdig.products.diag_crossection import draw_wind_theta_spfh
from metdig.products.diag_crossection import draw_time_rh_uv_tmp
from metdig.products.diag_crossection import draw_time_rh_uv_theta
from metdig.products.diag_crossection import draw_wind_theta_mpv
from metdig.products.diag_crossection import draw_wind_vortadv_tmp
from metdig.products.diag_crossection import draw_wind_tmpadv_tmp, draw_time_div_vort_rh_uv, draw_time_div_vort_spfh_uv, draw_time_wind_vortadv_tmp, draw_time_wind_tmpadv_tmp, draw_wind_w_tmpadv_tmp,draw_time_wind_qcld_qice_tmp
from metdig.products import diag_crossection


import metdig.cal as mdgcal
from metdig.utl import mdgstda

@date_init('init_time', method=date_init.special_series_set)
def time_wind_qcld_qsn_tmp(data_source='cassandra', data_name='grapes_gfs', init_time=None, fhours=range(0, 48, 3),
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
        drawret = diag_crossection.draw_time_wind_qcld_qsn_tmp(qcld,qsn, tmp, u, v, terrain, **products_kwargs)
        ret.update(drawret)
    return ret


@date_init('init_time', method=date_init.special_series_set)
def time_wind_qcld_qice_tmp(data_source='cassandra', data_name='grapes_gfs', init_time=None, fhours=range(0, 48, 3),
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
        drawret = draw_time_wind_qcld_qice_tmp(qcld,qice, tmp, u, v, terrain, **products_kwargs)
        ret.update(drawret)
    return ret

@date_init('init_time')
def wind_w_theta_spfh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
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

    w = mdgcal.vertical_velocity(vvel, tmp, spfh)

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

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp, 'hgt': hgt, 'psfc': psfc}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_wind_theta_spfh(cross_spfh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

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
    terrain = pressure - psfc.values.repeat(pressure['level'].size, axis=1)
    terrain.attrs['var_units'] = ''
    if is_draw:
        drawret = draw_time_div_vort_spfh_uv(div, vort, spfh, u, v, terrain, **products_kwargs)
        ret.update(drawret)

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

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': div, 'vort': vort}
        ret.update({'data': dataret})

    u = u.interp(lon=points['lon'], lat=points['lat'])
    v = v.interp(lon=points['lon'], lat=points['lat'])
    div = div.interp(lon=points['lon'], lat=points['lat'])
    vort = vort.interp(lon=points['lon'], lat=points['lat'])
    rh = rh.interp(lon=points['lon'], lat=points['lat'])
    psfc = psfc.interp(lon=points['lon'], lat=points['lat'])
    _, pressure = xr.broadcast(v, v['level'])
    terrain = pressure - psfc.values.repeat(pressure['level'].size, axis=1)
    terrain.attrs['var_units'] = ''
    if is_draw:
        drawret = draw_time_div_vort_rh_uv(div, vort, rh, u, v, terrain, **products_kwargs)
        ret.update(drawret)

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
        drawret = draw_time_wind_tmpadv_tmp(tmpadv, tmp, u, v, terrain, **products_kwargs)
        ret.update(drawret)
    return ret


@date_init('init_time')
def wind_tmpadv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
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
        drawret = draw_wind_tmpadv_tmp(cross_tmpadv, cross_tmp, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)
    return ret


@date_init('init_time')
def wind_w_tmpadv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                      levels=[1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                      st_point=[20, 120.0], ed_point=[50, 130.0], h_pos=[0.125, 0.665, 0.25, 0.2],
                      area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=map_extent)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=map_extent)
    vvel = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                             var_name='vvel', levels=levels, extent=map_extent)
    spfh = read_spfh_3D(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels,extent=map_extent)

    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=500, extent=map_extent)
    psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='psfc', extent=map_extent)

    # +form 3D psfc
    _, psfc_bdcst = xr.broadcast(tmp, psfc.squeeze())
    psfc_bdcst = psfc_bdcst.where(psfc_bdcst > -10000, drop=True)  # 去除小于-10000

    tmpadv = mdgcal.var_advect(tmp, u, v)
    w = mdgcal.vertical_velocity(vvel, tmp, spfh)
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

    ratio = np.abs(cross_n.values).max()/np.abs(cross_w.values).max()
    if is_return_data:
        dataret = {'tmpadv': cross_tmpadv, 'wind_n': cross_n, 'w': cross_w, 'tmp': cross_tmp, 'hgt': hgt, 'psfc': cross_psfc}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_wind_w_tmpadv_tmp(cross_tmpadv, cross_tmp, cross_t, cross_w*ratio, cross_terrain, hgt,
                                         st_point=st_point, ed_point=ed_point,
                                         lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                         map_extent=map_extent, h_pos=h_pos,
                                         **products_kwargs)
        ret.update(drawret)
    return ret

if __name__ == '__main__':
    wind_w_tmpadv_tmp(init_time='2020111708',st_point=[20, 117.5], ed_point=[50, 117.6],
                        fhour=0,data_source='era5')

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
        drawret = draw_time_wind_vortadv_tmp(vortadv, tmp, u, v, terrain, **products_kwargs)
        ret.update(drawret)
    return ret

@date_init('init_time')
def wind_vortadv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                     levels=[1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
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
        drawret = draw_wind_vortadv_tmp(cross_vortadv, cross_tmp, cross_u, cross_v, cross_terrain, hgt,
                                        st_point=st_point, ed_point=ed_point,
                                        lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                        map_extent=map_extent, h_pos=h_pos,
                                        **products_kwargs)
        ret.update(drawret)
    return ret


@date_init('init_time')
def wind_theta_mpv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                   levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
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

    if is_return_data:
        dataret = {'theta': theta, 'u': u, 'v': v, 'pv': mpv, 'hgt': hgt, 'psfc': psfc}
        ret.update({'data': dataret})

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

    if is_draw:
        drawret = draw_wind_theta_mpv(cross_mpv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                      st_point=st_point, ed_point=ed_point,
                                      lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                      map_extent=map_extent, h_pos=h_pos,
                                      **products_kwargs)
        ret.update(drawret)

    return ret


@date_init('init_time')
def wind_theta_absv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
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
        drawret = draw_wind_theta_absv(cross_absv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    return ret

@date_init('init_time')
def wind_theta_rh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                  levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
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

    cross_theta = mdgcal.equivalent_potential_temperature(pressure, cross_tmp, cross_td)

    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    if is_draw:
        drawret = draw_wind_theta_rh(cross_rh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                     st_point=st_point, ed_point=ed_point,
                                     lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                     map_extent=map_extent, h_pos=h_pos,
                                     **products_kwargs)
        ret.update(drawret)

    return ret


@date_init('init_time')
def wind_theta_spfh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                    levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
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
        drawret = draw_wind_theta_spfh(cross_spfh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                                       st_point=st_point, ed_point=ed_point,
                                       lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                       map_extent=map_extent, h_pos=h_pos,
                                       **products_kwargs)
        ret.update(drawret)

    return ret

@date_init('init_time')
def wind_tmp_rh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
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
    cross_psfc = mdgcal.cross_section(psfc_bdcst, st_point, ed_point)

    cross_u_t, cross_v_n = mdgcal.cross_section_components(cross_u, cross_v)

    _, pressure = xr.broadcast(cross_rh, cross_tmp['level'])
    cross_terrain = pressure - cross_psfc
    cross_terrain.attrs['var_units'] = ''

    cross_rh = cross_rh.where(cross_rh < 100, 100)  # 大于100的赋值成100

    if is_draw:
        drawret = draw_wind_tmp_rh(cross_rh, cross_tmp, cross_u, cross_v, cross_u_t, cross_v_n, cross_terrain, hgt,
                                   st_point=st_point, ed_point=ed_point,
                                   lon_cross=cross_u['lon_cross'].values, lat_cross=cross_u['lat_cross'].values,
                                   map_extent=map_extent, h_pos=h_pos,
                                   **products_kwargs)
        ret.update(drawret)

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

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp}
        ret.update({'data': dataret})

    tmp = tmp.interp(lon=points['lon'], lat=points['lat'])
    u = u.interp(lon=points['lon'], lat=points['lat'])
    v = v.interp(lon=points['lon'], lat=points['lat'])
    rh = rh.interp(lon=points['lon'], lat=points['lat'])

    td = mdgcal.dewpoint_from_relative_humidity(tmp, rh)
    pressure = mdgstda.gridstda_full_like_by_levels(rh, rh['level'].values)
    theta = mdgcal.equivalent_potential_temperature(pressure, tmp, td)

    if is_draw:
        drawret = draw_time_rh_uv_theta(rh, u, v, theta, **products_kwargs)
        ret.update(drawret)

    return ret


@date_init('init_time', method=date_init.special_series_set)
def time_rh_uv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhours=range(0, 48, 3),
                   levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200],
                   points={'lon': [116.3833], 'lat': [39.9]},mean_area=None,
                   is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='tmp', levels=levels,extent=mean_area)
    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='u', levels=levels,extent=mean_area)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='v', levels=levels,extent=mean_area)
    rh = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='rh', levels=levels,extent=mean_area)
    psfc = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='psfc',extent=mean_area)

    if is_return_data:
        dataret = {'rh': rh, 'u': u, 'v': v, 'tmp': tmp, 'psfc': psfc}
        ret.update({'data': dataret})

    if (mean_area==None):
        tmp = tmp.interp(lon=points['lon'], lat=points['lat'])
        u = u.interp(lon=points['lon'], lat=points['lat'])
        v = v.interp(lon=points['lon'], lat=points['lat'])
        rh = rh.interp(lon=points['lon'], lat=points['lat'])
        psfc = psfc.interp(lon=points['lon'], lat=points['lat'])

    _, pressure = xr.broadcast(v, v['level'])
    terrain = pressure - psfc.values.repeat(pressure['level'].size, axis=1)
    terrain.attrs['var_units'] = ''

    rh = rh.where(rh < 100, 100)  # 大于100的赋值成100

    if is_draw:
        drawret = draw_time_rh_uv_tmp(rh, u, v, tmp, terrain, **products_kwargs)
        ret.update(drawret)

    return ret
