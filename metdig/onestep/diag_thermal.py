# -*- coding: utf-8 -*

from metdig.io import get_model_grid
import metdig.cal as mdgcal

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.onestep.complexgrid_var.theta import read_theta


from metdig.products.diag_thermal import *

@date_init('init_time')
def hgt_uv_theta(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                 hgt_lev=500, uv_lev=850, theta_lev=850, is_mask_terrain=True,
                 area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='v', level=uv_lev, extent=map_extent)
    theta = read_theta(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       level=theta_lev, extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'theta': theta}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt_lev, hgt)
        u = mask_terrian(psfc, uv_lev, u)
        v = mask_terrian(psfc, uv_lev, v)
        theta = mask_terrian(psfc, theta_lev, theta)

    # plot
    if is_draw:
        drawret = draw_hgt_uv_theta(hgt, u, v, theta, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    return ret


@date_init('init_time')
def hgt_uv_tmp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
               hgt_lev=500, uv_lev=850, tmp_lev=850, is_mask_terrain=True,
               area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    tmp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='tmp', level=tmp_lev, extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'tmp': tmp}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt_lev, hgt)
        u = mask_terrian(psfc, uv_lev, u)
        v = mask_terrian(psfc, uv_lev, v)
        tmp = mask_terrian(psfc, tmp_lev, tmp)

    # plot
    if is_draw:
        drawret = draw_hgt_uv_tmp(hgt, u, v, tmp, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    return ret

@date_init('init_time')
def hgt_uv_tmpadv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                  hgt_lev=500, tmp_lev=850, is_mask_terrain=True,
                  area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=tmp_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=tmp_lev, extent=map_extent)
    tmp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='tmp', level=tmp_lev, extent=map_extent)
    tmpadv = mdgcal.var_advect(tmp, u, v)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'tmpadv': tmpadv}
        ret.update({'data': dataret})

    tmp = mdgcal.gaussian_filter(tmp, 1)
    tmpadv = mdgcal.gaussian_filter(tmpadv, 1)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt_lev, hgt)
        u = mask_terrian(psfc, tmp_lev, u)
        v = mask_terrian(psfc, tmp_lev, v)
        tmpadv = mask_terrian(psfc, tmp_lev, tmpadv)
        tmp = mask_terrian(psfc, tmp_lev, tmp)

    # plot
    if is_draw:
        drawret = draw_hgt_uv_tmpadv(hgt, u, v, tmp, tmpadv, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    return ret