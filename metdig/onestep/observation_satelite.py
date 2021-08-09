# -*- coding: utf-8 -*-

import datetime
import numpy as np

from metdig.io.cassandra import get_model_grid
from metdig.io.cassandra import get_obs_stations
from metdig.io.cassandra import get_fy_awx

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.products import observation_satelite as draw_obssate

import metdig.cal as mdgcal

__all__ = [
    'fy4air_sounding_hgt',
]


def fy4air_sounding_hgt(ir_obs_time=None, ir_channel=9,
                        sounding_obs_time=None,
                        hgt_init_time=None, hgt_fhour=24,
                        is_mask_terrain=True,
                        area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=ir_channel, extent=map_extent)
    hgt = get_model_grid(init_time=hgt_init_time, fhour=hgt_fhour, data_name='ecmwf', var_name='hgt', level=500, extent=map_extent)
    sounding_wsp = get_obs_stations(obs_time=sounding_obs_time, data_name='plot_high', var_name='wsp', level=500, extent=map_extent)
    sounding_wdir = get_obs_stations(obs_time=sounding_obs_time, data_name='plot_high', var_name='wdir', level=500, extent=map_extent)

    # 计算uv
    sounding_u, sounding_v = mdgcal.wind_components(sounding_wsp, sounding_wdir)
    # 过滤超过100的uv
    sounding_u.stda.where((sounding_u.stda.values < 100) & (sounding_v.stda.values < 100), np.nan)
    sounding_v.stda.where((sounding_u.stda.values < 100) & (sounding_v.stda.values < 100), np.nan)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'sounding_u': sounding_u, 'sounding_v': sounding_v}
        ret.update({'data': dataret})

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

    # plot
    if is_draw:
        drawret = draw_obssate.draw_fy4air_sounding_hgt(ir, hgt, sounding_u, sounding_v, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
