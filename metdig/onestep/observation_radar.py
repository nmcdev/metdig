# -*- coding: utf-8 -*-

import datetime
import numpy as np

from metdig.io.cassandra import get_model_grid
from metdig.io.cassandra import get_obs_stations
from metdig.io.cassandra import get_radar_mosaic

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.products import observation_radar as draw_obsradar

import metdig.cal as mdgcal

__all__ = [
    'cref_sounding_hgt',
]


def cref_sounding_hgt(cref_obs_time=None,
                      sounding_obs_time=None,
                      hgt_init_time=None, hgt_fhour=24,
                      is_mask_terrain=True,
                      area='全国', is_return_data=False, is_draw=True, **products_kwargs):

    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    cref = get_radar_mosaic(obs_time=cref_obs_time, data_name='achn', var_name='cref',  extent=map_extent)
    hgt = get_model_grid(init_time=hgt_init_time, fhour=hgt_fhour, data_name='ecmwf', var_name='hgt', level=500, extent=map_extent)
    sounding_wsp = get_obs_stations(obs_time=sounding_obs_time, data_name='plot_high', var_name='wsp', level=500, extent=map_extent)
    sounding_wdir = get_obs_stations(obs_time=sounding_obs_time, data_name='plot_high', var_name='wdir', level=500, extent=map_extent)

    # cref = cref[..., ::4, ::4]

    # 计算uv
    sounding_u, sounding_v = mdgcal.wind_components(sounding_wsp, sounding_wdir)
    # 过滤超过100的uv
    sounding_u.stda.where((sounding_u.stda.data < 100) & (sounding_v.stda.data < 100), np.nan)
    sounding_v.stda.where((sounding_u.stda.data < 100) & (sounding_v.stda.data < 100), np.nan)

    if is_return_data:
        dataret = {'cref': cref, 'hgt': hgt, 'sounding_u': sounding_u, 'sounding_v': sounding_v}
        ret.update({'data': dataret})

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

    # plot
    if is_draw:
        drawret = draw_obsradar.draw_cref_sounding_hgt(cref, hgt, sounding_u, sounding_v, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
