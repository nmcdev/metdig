# -*- coding: utf-8 -*-

from metdig.io import get_model_points
from metdig.io import get_obs_stations_multitime

from metdig.onestep.lib.utility import date_init

from metdig.products import observation_station as draw_obsstation

import metdig.cal as mdgcal
from metdig.io.cassandra import get_tlogp

__all__ = [
    'obs_uv_tmp_rh_rain',
    'blowup_sounding'
]

@date_init('obs_time')
def blowup_sounding(data_source='cassandra',data_name='ecmwf',id_selected=54511,
    obs_time=None, is_return_data=False,is_draw=True,**products_kwargs):
    ret={}

    tmp_sounding=get_tlogp(obs_time=obs_time,data_name='tlogp',var_name='tmp',id_selected=id_selected).drop_duplicates()
    td_sounding=get_tlogp(obs_time=obs_time,data_name='tlogp',var_name='td',id_selected=id_selected).drop_duplicates()
    wsp_sounding=get_tlogp(obs_time=obs_time,data_name='tlogp',var_name='wsp',id_selected=id_selected).drop_duplicates()
    wdir_sounding=get_tlogp(obs_time=obs_time,data_name='tlogp',var_name='wdir',id_selected=id_selected).drop_duplicates()
    pres_sounding = tmp_sounding.copy(deep=True)
    pres_sounding.stda.set_values(tmp_sounding.level, var_name='pres')

    if is_return_data:
        dataret = {'tmp': tmp_sounding, 'td': td_sounding, 'wsp': wsp_sounding, 'wdir': wdir_sounding}
        ret.update({'data': dataret})

    if is_draw:
        theta_sounding=mdgcal.thermal.equivalent_potential_temperature(pres=pres_sounding,tmp=tmp_sounding,td=td_sounding)
        thetaes_sounding=mdgcal.thermal.saturation_equivalent_potential_temperature(pres=pres_sounding,tmp=tmp_sounding)
        thta_sounding=mdgcal.thermal.potential_temperature(pres=pres_sounding,tmp=tmp_sounding)
        u_sounding,v_sounding=mdgcal.other.wind_components(wsp_sounding,wdir_sounding)
        draw_obsstation.draw_blowup_sounding(pres_sounding,thta_sounding,theta_sounding,thetaes_sounding,u_sounding,v_sounding,**products_kwargs)
    if ret:
        return ret

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    blowup_sounding()
    plt.show()


@date_init('obs_times', method=date_init.series_1_36_set)
def obs_uv_tmp_rh_rain(data_source='cassandra', data_name='sfc_chn_hor', obs_times=None, id_selected=54511,
                       is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    rain01 = get_obs_stations_multitime(obs_times=obs_times,data_source=data_source, data_name=data_name, var_name='rain01', id_selected=id_selected)
    tmp = get_obs_stations_multitime(obs_times=obs_times,data_source=data_source, data_name=data_name, var_name='tmp', id_selected=id_selected)
    rh = get_obs_stations_multitime(obs_times=obs_times,data_source=data_source, data_name=data_name,  var_name='rh', id_selected=id_selected)
    wsp = get_obs_stations_multitime(obs_times=obs_times,data_source=data_source, data_name=data_name, var_name='wsp', id_selected=id_selected)
    wdir = get_obs_stations_multitime(obs_times=obs_times,data_source=data_source, data_name=data_name, var_name='wdir', id_selected=id_selected)

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
