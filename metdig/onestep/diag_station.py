# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import math
import numpy as np

from metdig.io import get_model_points

from metdig.onestep.lib.utility import date_init

from metdig.products import diag_station as draw_station

import metdig.cal as mdgcal


@date_init('init_time')
def uv_tmp_rh_rain(data_source='cassandra', data_name='ecmwf', init_time=None, fhours=np.arange(3, 36, 3), points={'lon': [110], 'lat': [20]},
                   is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get data
    t2m = get_model_points(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='t2m', points=points)
    u10m = get_model_points(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='u10m', points=points)
    v10m = get_model_points(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='v10m', points=points)
    rh2m = get_model_points(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='rh2m', points=points)
    rain03 = get_model_points(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='rain03', points=points)

    # calcu
    wsp = mdgcal.wind_speed(u10m, v10m)

    if is_return_data:
        dataret = {'t2m': t2m, 'u10m': u10m, 'v10m': v10m, 'rh2m': rh2m, 'rain03': rain03, 'wsp': wsp}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_station.draw_uv_tmp_rh_rain(t2m, u10m, v10m, rh2m, rain03, wsp, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def sta_SkewT(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
              levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150, 100],
              points={'lon': [116.3833], 'lat': [39.9]},
              is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    tmp = get_model_points(data_source=data_source, init_time=init_time, fhours=[
                           fhour], data_name=data_name, var_name='tmp', levels=levels, points=points)
    u = get_model_points(data_source=data_source, init_time=init_time, fhours=[
                         fhour], data_name=data_name, var_name='u', levels=levels, points=points)
    v = get_model_points(data_source=data_source, init_time=init_time, fhours=[
                         fhour], data_name=data_name, var_name='v', levels=levels, points=points)
    rh = get_model_points(data_source=data_source, init_time=init_time, fhours=[
                          fhour], data_name=data_name, var_name='rh', levels=levels, points=points)

    td = mdgcal.dewpoint_from_relative_humidity(tmp, rh)

    pres = tmp.copy(deep=True)
    pres.stda.reset_value(levels, var_name='pres')

    if is_return_data:
        dataret = {'pres': pres, 'tmp': tmp, 'td': td, 'u': u, 'v': v, 'rh': rh}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_station.draw_SkewT(pres, tmp, td, u, v, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


'''
def station_synthetical_forecast_from_cassandra(init_time=None,  fhours=np.arange(3, 36, 3), points={'lon': [110], 'lat': [20]}, **products_kwargs):

    t2m = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='t2m', points=points)
    rh2m = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='rh2m', points=points)
    td2m = mdgcal.dewpoint_from_relative_humidity(t2m, rh2m)

    p_vapor = mdgcal.cal_p_vapor(t2m, rh2m)  # 计算水汽压

    u10m = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='u10m', points=points)
    v10m = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='v10m', points=points)
    wsp10m = mdgcal.wind_speed(u10m, v10m)  # 计算10m风

    at = mdgcal.apparent_temperature(t2m, wsp10m, p_vapor)  # 计算体感温度

    rain03 = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='rain03', points=points)

    tcdc = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='tcdc', points=points)
    lcdc = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='lcdc', points=points)
    u100m = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='u100m', points=points)
    v100m = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='v100m', points=points)
    wsp100m = mdgcal.wind_speed(u100m, v100m)  # 计算100m风

    vis = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours, data_name='ecmwf', var_name='vis', points=points)

    gust10m_3h = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours,
                                  data_name='ecmwf', var_name='gust10m_3h', points=points)
    gust10m_6h = get_model_points(data_source='cassandra', init_time=init_time, fhours=fhours,
                                  data_name='ecmwf', var_name='gust10m_6h', points=points)

    # draw_vis = True
    # drw_thr = True
    # draw_station_synthetical_forecast_from_cassandra(
    #     t2m, td2m, at, u10m, v10m, u100m, v100m,
    #     gust10m, wsp10m, wsp100m, rain03, tcdc, lcdc,
    #     draw_vis=draw_vis, vis=vis, drw_thr=drw_thr,
    #     output_dir=output_dir)


def station_snow_synthetical_forecast_from_cassandra():
    pass
'''
