# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import math
import numpy as np

from metdig.io import get_model_points
from metdig.io.cassandra import get_obs_stations_multitime

from metdig.onestep.lib.utility import date_init

from metdig.products import observation_station as draw_obsstation

import metdig.cal as mdgcal
import metdig.utl as mdgstda

__all__ = [
    'obs_uv_tmp_rh_rain',
]


@date_init('obs_times', method=date_init.series_1_36_set)
def obs_uv_tmp_rh_rain(data_source='cassandra', data_name='sfc_chn_hor', obs_times=None, id_selected=54511,
                       is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    rain01 = get_obs_stations_multitime(obs_times=obs_times, data_name=data_name, var_name='rain01', id_selected=id_selected)
    tmp = get_obs_stations_multitime(obs_times=obs_times, data_name=data_name, var_name='tmp', id_selected=id_selected)
    rh = get_obs_stations_multitime(obs_times=obs_times, data_name=data_name,  var_name='rh', id_selected=id_selected)
    wsp = get_obs_stations_multitime(obs_times=obs_times, data_name=data_name, var_name='wsp', id_selected=id_selected)
    wdir = get_obs_stations_multitime(obs_times=obs_times, data_name=data_name, var_name='wdir', id_selected=id_selected)

    # calcu
    u, v = mdgcal.wind_components(wsp, wdir)

    if is_return_data:
        dataret = {'tmp': tmp, 'u': u, 'v': v, 'rh': rh, 'rain01': rain01, 'wsp': wsp}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_obsstation.draw_obs_uv_tmp_rh_rain(tmp, u, v, rh, rain01, wsp, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    obs_uv_tmp_rh_rain(label_bottomax='平均风',wsp_plot_kwargs={'label':'阵风'})
    plt.show()

