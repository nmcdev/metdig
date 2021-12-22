# -*- coding: utf-8 -*-

from metdig.io import get_model_grid
from metdig.io import get_model_3D_grids

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.onestep.complexgrid_var.div_uv import read_div_uv
from metdig.onestep.complexgrid_var.vort_uv import read_vort_uv
from metdig.onestep.complexgrid_var.theta import read_theta

from metdig.products import diag_dynamic as draw_dynamic

import metdig.cal as mdgcal
import metdig.utl.utl_stda_grid as utl_stda_grid

__all__ = [
    'hgt_uv_vvel',
    'hgt_uv_div',
    'hgt_uv_vortadv',
    'uv_fg_thta',
]


@date_init('init_time')
def hgt_uv_vvel(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                hgt_lev=500, uv_lev=500, vvel_lev=500, smth_step=3, is_mask_terrain=True,
                area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    vvel = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                          data_name=data_name, var_name='vvel', level=vvel_lev, extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'vvel': vvel}
        ret.update({'data': dataret})

    vvel = mdgcal.gaussian_filter(vvel, smth_step)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        vvel = mask_terrian(psfc, vvel)

    # plot
    if is_draw:
        drawret = draw_dynamic.draw_hgt_uv_vvel(hgt, u, v, vvel, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def hgt_uv_div(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
               hgt_lev=500, div_lev=850, is_mask_terrain=True,
               area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    div, u, v = read_div_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=div_lev, extent=map_extent)

    div_attrs = div.attrs
    div = div.rolling(lon=5, lat=5, min_periods=1, center=True).mean()
    div.attrs = div_attrs

    # 隐藏被地形遮挡地区
    psfc=None
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        div = mask_terrian(psfc, div)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'div': div, 'psfc': psfc}
        ret.update({'data': dataret})
    # plot
    if is_draw:
        drawret = draw_dynamic.draw_hgt_uv_div(hgt, u, v, div, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def hgt_uv_vortadv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                   hgt_lev=500, vort_lev=500, smth_step=1, is_mask_terrain=True,
                   area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    vort, u, v = read_vort_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=vort_lev, extent=map_extent)
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    vortadv = mdgcal.var_advect(vort, u, v)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'vortadv': vortadv}
        ret.update({'data': dataret})

    vortadv = mdgcal.gaussian_filter(vortadv, smth_step)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        vortadv = mask_terrian(psfc, vortadv)

    # plot
    if is_draw:
        drawret = draw_dynamic.draw_hgt_uv_vortadv(hgt, u, v, vortadv, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def uv_fg_thta(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
               fg_lev=500, is_mask_terrain=True,
               area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=fg_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=fg_lev, extent=map_extent)
    tmp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='tmp', level=fg_lev, extent=map_extent)

    pres = utl_stda_grid.gridstda_full_like(tmp, fg_lev, var_name='pres')
    thta = mdgcal.potential_temperature(pres, tmp)
    fg = mdgcal.frontogenesis(thta, u, v)
    thta = mdgcal.gaussian_filter(thta, 1)
    if is_return_data:
        dataret = {'u': u, 'v': v, 'thta': thta, 'fg': fg}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        thta = mask_terrian(psfc, thta)
        fg = mask_terrian(psfc, fg)

    # plot
    if is_draw:
        drawret = draw_dynamic.draw_uv_fg_thta(u, v, thta, fg, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
