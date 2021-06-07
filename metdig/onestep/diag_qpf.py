# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import datetime

from metdig.io import get_model_grid
from metdig.io import get_model_grids

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import date_init

from metdig.products import diag_qpf as draw_qpf

import metdig.cal as mdgcal


@date_init('init_time')
def hgt_rain(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, atime=6, hgt_lev=500, area='全国',
             is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}
    map_extent = get_map_area(area)

    if atime > 3:
        fhour_gh = int(fhour - atime / 2)
    else:
        fhour_gh = fhour

    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour_gh, data_name=data_name, level=hgt_lev,
                         var_name='hgt', extent=map_extent)

    rain = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='rain{:02d}'.format(atime), extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt, 'rain': rain}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_qpf.draw_hgt_rain(hgt, rain, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def mslp_rain_snow(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, atime=6, area='全国',
                   is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    map_extent = get_map_area(area)

    rain_data = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                               var_name='rain{:02d}'.format(atime), extent=map_extent)
    snow_data = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                               var_name='snow{:02d}'.format(atime), extent=map_extent)
    prmsl = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='prmsl', extent=map_extent)

    snow, sleet, rain = mdgcal.cal_snow_sleet_rain(rain_data, snow_data)
    snow.attrs['data_name'] = data_name
    snow.attrs['valid_time'] = atime
    sleet.attrs['data_name'] = data_name
    sleet.attrs['valid_time'] = atime
    rain.attrs['data_name'] = data_name
    rain.attrs['valid_time'] = atime

    if is_return_data:
        dataret = {'rain': rain, 'snow': snow, 'sleet': sleet, 'prmsl': prmsl}
        ret.update({'data': dataret})

    prmsl = mdgcal.gaussian_filter(prmsl, 5)
    
    if is_draw:
        drawret = draw_qpf.draw_mslp_rain_snow(rain, snow, sleet, prmsl, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


'''
def cumulated_precip(data_source='cassandra', data_name='ecmwf', init_time=None, t_gap=6, t_range=[6, 36], area='全国', **products_kwargs):
    map_extent = get_map_area(area)

    fhours = np.arange(t_range[0], t_range[1] + 1, t_gap)
    rain_data = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                                var_name='rain{:02d}'.format(t_gap), extent=map_extent)

    rain = rain_data.copy(deep=True)
    valid_time = []
    for itime in range(1, len(rain_data['dtime'].values)):
        rain.values[:, :, :, itime, :, :] = np.sum(rain_data.values[:, :, :, 0:itime + 1, :, :], axis=3)
    rain.attrs['var_name'] = 'rain'
    rain.attrs['var_cn_name'] = ''
    rain.attrs['valid_time'] = ''
    
    # ret = draw_qpf.draw_cumulated_precip(rain, map_extent=map_extent, **products_kwargs)
    # if ret:
        # return ret

def rain_evo(data_source='cassandra', data_name='ecmwf', init_time=None, t_gap=6, t_range=[6, 36], fcs_lvl=4, area='全国', **products_kwargs):

    map_extent = get_map_area(area)

    fhours = np.arange(t_range[0], t_range[1] + 1, t_gap)
    rain = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                           var_name='rain{:02d}'.format(t_gap), extent=map_extent)
    
    ret = draw_qpf.draw_rain_evo(rain, map_extent=map_extent, **products_kwargs)

    if ret:
        return ret

'''
