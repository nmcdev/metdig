# -*- coding: utf-8 -*-
import pandas as pd

from metdig.io import get_model_grid
from metdig.io import get_model_grids

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.products import diag_identify as draw_identify

import metdig.cal as mdgcal


__all__ = [
    'high_low_center',
    'vortex',
    'trough',
    'reverse_trough',
    'convergence_line',
    'shear',
    'jet',
    'subtropical_high',
    'south_asia_high',
]


@date_init('init_time')
def high_low_center(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, hgt_lev=1000, is_mask_terrain=True,
                    area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)

    smooth_times = identify_kwargs.pop('smooth_times', 10)
    caldata = mdgcal.high_low_center(hgt, smooth_times=smooth_times, **identify_kwargs)
    ids = caldata['ids']

    hgt = mdgcal.smooth_n_point(hgt, 5)

    if is_return_data:
        dataret = {'hgt': hgt, 'ids': ids, 'graphy': caldata['graphy']}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        # ids = mask_terrian(psfc, ids)

    # plot
    if is_draw:
        drawret = draw_identify.draw_high_low_center(hgt, ids, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def vortex(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, uv_lev=850, is_mask_terrain=True,
           area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)

    caldata = mdgcal.vortex(u, v, **identify_kwargs)
    ids = caldata['ids']

    if is_return_data:
        dataret = {'u': u, 'v': v, 'ids': ids, 'graphy': caldata['graphy']}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        # ids = mask_terrian(psfc, ids)

    # plot
    if is_draw:
        drawret = draw_identify.draw_vortex(u, v, ids, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def vortex_trace(data_source='cassandra', data_name='ecmwf', init_time=None,  fhours=range(0, 72, 3), uv_lev=850, is_mask_terrain=True,
           area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)

    trace = mdgcal.vortex_trace(u, v, **identify_kwargs)

    if is_return_data:
        dataret = {'u': u, 'v': v, 'trace': trace}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_identify.draw_vortex_trace(u, v, trace, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def trough(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, hgt_lev=500, is_mask_terrain=True,
           area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)

    smooth_times = identify_kwargs.pop('smooth_times', 10)
    min_size = identify_kwargs.pop('min_size', 500)
    caldata = mdgcal.trough(hgt, smooth_times=smooth_times, min_size=min_size, **identify_kwargs)
    graphy = caldata['graphy']

    hgt = mdgcal.smooth_n_point(hgt, 5)

    if is_return_data:
        dataret = {'hgt': hgt, 'graphy': caldata['graphy']}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)

    # plot
    if is_draw:
        drawret = draw_identify.draw_trough(hgt, graphy, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def reverse_trough(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, hgt_lev=500, is_mask_terrain=True,
                   area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)

    smooth_times = identify_kwargs.pop('smooth_times', 10)
    caldata = mdgcal.reverse_trough(hgt, smooth_times=smooth_times, **identify_kwargs)
    graphy = caldata['graphy']

    hgt = mdgcal.smooth_n_point(hgt, 5)

    if is_return_data:
        dataret = {'hgt': hgt, 'graphy': caldata['graphy']}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)

    # plot
    if is_draw:
        drawret = draw_identify.draw_reverse_trough(hgt, graphy, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def convergence_line(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, uv_lev=850, is_mask_terrain=True,
                     area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)

    min_size = identify_kwargs.pop('min_size', 300)
    caldata = mdgcal.convergence_line(u, v, min_size=min_size, **identify_kwargs)
    graphy = caldata['graphy']

    if is_return_data:
        dataret = {'u': u, 'v': v, 'graphy': caldata['graphy']}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)

    # plot
    if is_draw:
        drawret = draw_identify.draw_convergence_line(u, v, graphy, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def shear(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, uv_lev=850, is_mask_terrain=True,
          area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)

    min_size = identify_kwargs.pop('min_size', 400)
    caldata = mdgcal.shear(u, v, min_size=min_size, **identify_kwargs)
    graphy = caldata['graphy']

    if is_return_data:
        dataret = {'u': u, 'v': v, 'graphy': caldata['graphy']}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)

    # plot
    if is_draw:
        drawret = draw_identify.draw_shear(u, v, graphy, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def jet(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, uv_lev=850, is_mask_terrain=True,
        area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)

    wsp = mdgcal.wind_speed(u, v)

    min_size = identify_kwargs.pop('min_size', 300)
    only_south_jet = identify_kwargs.pop('only_south_jet', True)
    caldata = mdgcal.jet(u, v, min_size=min_size, only_south_jet=only_south_jet, **identify_kwargs)
    graphy = caldata['graphy']

    if is_return_data:
        dataret = {'u': u, 'v': v, 'wsp': wsp, 'graphy': caldata['graphy']}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)

    # plot
    if is_draw:
        drawret = draw_identify.draw_jet(u, v, wsp, graphy, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
if __name__ == '__main__':
    jet(data_source='cmadaas', data_name='ecmwf_hr', init_time='2023050408', fhour=24, uv_lev=850, 
                     is_mask_terrain=False)

@date_init('init_time')
def subtropical_high(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, hgt_lev=500, is_mask_terrain=True,
                     area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)

    smooth_times = identify_kwargs.pop('smooth_times', 20)
    caldata = mdgcal.subtropical_high(hgt, smooth_times=smooth_times, **identify_kwargs)
    graphy = caldata['graphy']

    hgt = mdgcal.smooth_n_point(hgt, 5)

    if is_return_data:
        dataret = {'hgt': hgt, 'graphy': caldata['graphy']}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        # ids = mask_terrian(psfc, ids)

    # plot
    if is_draw:
        drawret = draw_identify.draw_subtropical_high(hgt, graphy, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def south_asia_high(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, hgt_lev=100, is_mask_terrain=True,
                    area='全国', is_return_data=False, is_draw=True, identify_kwargs={}, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)

    smooth_times = identify_kwargs.pop('smooth_times', 20)
    sn_height = identify_kwargs.pop('sn_height', 16680)
    caldata = mdgcal.south_asia_high(hgt, smooth_times=smooth_times, sn_height=sn_height, **identify_kwargs)
    graphy = caldata['graphy']

    hgt = mdgcal.smooth_n_point(hgt, 5)

    if is_return_data:
        dataret = {'hgt': hgt, 'graphy': caldata['graphy']}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        # ids = mask_terrian(psfc, ids)

    # plot
    if is_draw:
        drawret = draw_identify.draw_south_asia_high(hgt, graphy, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
