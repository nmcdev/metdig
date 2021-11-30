# -*- coding: utf-8 -*-

from metdig import utl
import matplotlib.pyplot as plt
import math
import numpy as np

from metdig.io import get_model_points

from metdig.onestep.lib.utility import date_init
from metdig.onestep.complexgrid_var.get_rain import read_points_rain

from metdig.products import diag_station as draw_station

import metdig.cal as mdgcal

__all__ = [
    'uv_tmp_rh_rain',
    'sta_SkewT',
    't2m_ens_boxplot',
    'rain_ens_boxplot'
]

@date_init('init_time')
def rain_ens_boxplot(data_source='cassandra', data_name='ecmwf_ens', init_time=None, fhours=np.arange(0, 72, 3), atime=3, points={'lon': [110], 'lat': [20],'id':['任意点']},
                   is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get data
    rain = read_points_rain(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, points=points,atime=atime)

    # calcu
    if is_return_data:
        dataret = {'t2m': rain}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_station.draw_rain_ens_boxplot(rain, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def t2m_ens_boxplot(data_source='cassandra', data_name='ecmwf_ens', init_time=None, fhours=np.arange(0, 72, 3), points={'lon': [110], 'lat': [20],'id':['任意点']},
                   is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get data
    t2m = get_model_points(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='t2m', points=points)

    # calcu
    if is_return_data:
        dataret = {'t2m': t2m}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_station.draw_t2m_ens_boxplot(t2m, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    t2m_ens_boxplot(init_time='2021090708', fhours=np.arange(0, 243, 3),t2m_boxplot_kwargs=dict(medianline=True,label_gap=3))
    plt.show()

@date_init('init_time')
def uv_tmp_rh_rain(data_source='cassandra', data_name='ecmwf', init_time=None, fhours=np.arange(3, 36, 3), points={'lon': [110], 'lat': [20] ,'id':['任意点']},
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
              points={'lon': [116.3833], 'lat': [39.9] ,'id':['任意点']},
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
    pres.stda.set_values(levels, var_name='pres')

    if is_return_data:
        dataret = {'pres': pres, 'tmp': tmp, 'td': td, 'u': u, 'v': v, 'rh': rh}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_station.draw_SkewT(pres, tmp, td, u, v, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

