# -*- coding: utf-8 -*-

from metdig.io import get_model_grid,get_model_grids,get_obs_stations

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.products import veri_synop as draw_veri_synop
import metdig.cal as mdgcal

import datetime
import numpy as np

__all__ = [
    'compare_gh_uv',
    'veri_heatwave',
    'veri_gust10m',
    'veri_wsp',

]


@date_init('anl_time')
def compare_gh_uv(data_source='cassandra',
                anl_time=None,anamodel='cma_gfs',
                data_name='cma_gfs',fhour=24,
                hgt_lev=500, uv_lev=850,
                is_mask_terrain=True,area='全国', is_return_data=False, is_draw=True,
                **products_kwargs):
    
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt_ana = get_model_grid(data_source=data_source, init_time=anl_time, fhour=0, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u_ana = get_model_grid(data_source=data_source, init_time=anl_time, fhour=0, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v_ana = get_model_grid(data_source=data_source, init_time=anl_time, fhour=0, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)

    init_time_fcst=anl_time-datetime.timedelta(hours=fhour)
    hgt_fcst = get_model_grid(data_source=data_source, init_time=init_time_fcst, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u_fcst = get_model_grid(data_source=data_source, init_time=init_time_fcst, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v_fcst = get_model_grid(data_source=data_source, init_time=init_time_fcst, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)

    if is_return_data:
        dataret = {'hgt_ana': hgt_ana , 'u_ana': u_ana, 'v_ana': v_ana,
                    'hgt_fcst': hgt_fcst , 'u_fcst': u_fcst, 'v_fcst': v_fcst}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc_ana = get_model_grid(data_source=data_source, init_time=anl_time, fhour=0, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt_ana = mask_terrian(psfc_ana, hgt_ana)
        u_ana = mask_terrian(psfc_ana, u_ana)
        v_ana = mask_terrian(psfc_ana, v_ana)

        psfc_fcst = get_model_grid(data_source=data_source, init_time=init_time_fcst, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt_fcst = mask_terrian(psfc_fcst, hgt_fcst)
        u_fcst = mask_terrian(psfc_fcst, u_fcst)
        v_fcst = mask_terrian(psfc_fcst, v_fcst)

    if is_draw:
        drawret = draw_veri_synop.draw_compare_gh_uv(
                    hgt_ana, u_ana, v_ana,
                    hgt_fcst, u_fcst, v_fcst,
                    map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
        
@date_init('obs_time')
def veri_heatwave(data_source='cassandra',
                obs_time=None,
                data_name='cma_gfs',fhour=24,
                area='全国', is_return_data=False, is_draw=True,
                **products_kwargs):
    

    ret = {}
    # get area
    map_extent = get_map_area(area)
    init_time=obs_time-datetime.timedelta(hours=fhour)
    tmx24_2m_fcst = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                              var_name='tmx24_2m', throwexp=False)
    if tmx24_2m_fcst is None:
        fhours = np.arange(fhour - 21, fhour + 1, 3)
        t2m = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                              var_name='tmx3_2m', throwexp=False)
        if t2m is None:
            t2m = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                                  var_name='t2m', throwexp=False)
            if t2m is None:
                raise Exception('can not get any data')

        tmx24_2m_fcst = t2m.isel(dtime=[-1]).copy()
        tmx24_2m_fcst.values[:, :, :, 0, :, :] = t2m.max(dim='dtime').values
        tmx24_2m_fcst.attrs['var_name'] = 'tmx24_2m'
        tmx24_2m_fcst.attrs['var_cn_name'] = '过去24小时最高温度'
        tmx24_2m_fcst.attrs['valid_time'] = 24

    tmx24_2m_obs = get_obs_stations(obs_time=obs_time,data_name='sfc_chn_hor',var_name='tmx24_2m',data_source=data_source,level=None,is_save_other_info=None).dropna()

    if is_return_data:
        dataret = {'tmx24_2m_fcst': tmx24_2m_fcst,
                    'tmx24_2m_obs': tmx24_2m_obs}
        ret.update({'data': dataret})
    if is_draw:
        drawret = draw_veri_synop.draw_veri_heatwave(
                    tmx24_2m_fcst,tmx24_2m_obs,
                    map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def veri_gust10m(data_source='cassandra',
                init_time=None,
                obs_time=None,
                data_name='ecmwf',fhour=24,
                area='全国', 
                md_ver='gust10m',obs_ver='gust10m',obsdir_ver='gustdir10m',
                mingust_obs=0,
                is_return_data=False, is_draw=True,
                **products_kwargs):
    

    ret = {}
    # get area
    map_extent = get_map_area(area)
    gust10m_fcst = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                              var_name=md_ver, throwexp=False)
    if(gust10m_fcst is None):                              
        gust10m_fcst = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                                var_name=md_ver+'_3h', throwexp=False)
    if(gust10m_fcst is None):
        gust10m_fcst = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                                var_name=md_ver+'_6h', throwexp=False)
    if(gust10m_fcst is None):
        print('no fcst data got')
        return

    for ivld in range(0,gust10m_fcst.attrs['valid_time']):
        obs_time=init_time+datetime.timedelta(hours=fhour-ivld)
        temp = get_obs_stations(obs_time=obs_time,data_name='sfc_chn_hor',var_name=obs_ver,data_source=data_source,level=None,extent=map_extent,is_save_other_info=None).dropna()
        tempdir = get_obs_stations(obs_time=obs_time,data_name='sfc_chn_hor',var_name=obsdir_ver,data_source=data_source,level=None,extent=map_extent,is_save_other_info=None).dropna()
        if (ivld==0):
            gust10m_obs=temp
            gustdir10m_obs=tempdir
        else:
            gust10m_obs=gust10m_obs.where(gust10m_obs['id'].isin(list(set(gust10m_obs['id']).intersection(temp['id'])))).dropna().sort_values('lon').reset_index(drop=True)
            temp=temp.where(temp['id'].isin(list(set(temp['id']).intersection(gust10m_obs['id'])))).dropna().sort_values('lon').reset_index(drop=True)

            gustdir10m_obs=gustdir10m_obs.where(gustdir10m_obs['id'].isin(list(set(gustdir10m_obs['id']).intersection(temp['id'])))).dropna().sort_values('lon').reset_index(drop=True)
            tempdir=tempdir.where(tempdir['id'].isin(list(set(tempdir['id']).intersection(temp['id'])))).dropna().sort_values('lon').reset_index(drop=True)

            cond=(temp.iloc[:,6]>gust10m_obs.iloc[:,6])
            gust10m_obs.iloc[:,6][cond]=temp.iloc[:,6][cond]
            gustdir10m_obs.iloc[:,6][cond]=tempdir.iloc[:,6][cond]

    gustdir10m_obs.attrs['valid_time']=gust10m_fcst.attrs['valid_time']
    gustdir10m_obs.attrs['var_cn_name']=str(gust10m_fcst.attrs['valid_time'])+'小时阵风风向'
    gust10m_obs.attrs['valid_time']=gust10m_fcst.attrs['valid_time']
    gust10m_obs.attrs['var_cn_name']=str(gust10m_fcst.attrs['valid_time'])+'小时阵风风速'

    gust10m_obs=gust10m_obs.where(gust10m_obs.iloc[:,6]>mingust_obs).dropna()

    if is_return_data:
        dataret = {'md_ver': gust10m_fcst,
                    'obs_ver': gust10m_obs,
                    'obsdir_ver':gustdir10m_obs}
        ret.update({'data': dataret})
    if is_draw:
        drawret = draw_veri_synop.draw_veri_gust10m(
                    gust10m_fcst,gust10m_obs,gustdir10m_obs,
                    map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def veri_wsp(data_source='cassandra',
                init_time=None,
                obs_time=None,
                data_name='ecmwf',fhour=24,
                area='全国', 
                obs_ver='wsp',obsdir_ver='wdir',
                mingust_obs=0,
                is_return_data=False, is_draw=True,
                **products_kwargs):
    

    ret = {}
    # get area
    map_extent = get_map_area(area)
    u10m_fcst = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                              var_name='u10m', throwexp=False)
    v10m_fcst = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                              var_name='v10m', throwexp=False)                              
    
    if((u10m_fcst is None) or (v10m_fcst is None)):
        print('no fcst data got')
        return

    wsp_fcst=mdgcal.other.wind_speed(u10m_fcst,v10m_fcst)

    obs_time=init_time+datetime.timedelta(hours=fhour)
    wsp_obs = get_obs_stations(obs_time=obs_time,data_name='sfc_chn_hor',var_name=obs_ver,data_source=data_source,level=None,extent=map_extent,is_save_other_info=None).dropna()
    wspdir_obs = get_obs_stations(obs_time=obs_time,data_name='sfc_chn_hor',var_name=obsdir_ver,data_source=data_source,level=None,extent=map_extent,is_save_other_info=None).dropna()
    wsp_obs=wsp_obs.where(wsp_obs['id'].isin(list(set(wsp_obs['id']).intersection(wsp_obs['id'])))).dropna().sort_values('lon').reset_index(drop=True)
    wspdir_obs=wspdir_obs.where(wspdir_obs['id'].isin(list(set(wspdir_obs['id']).intersection(wsp_obs['id'])))).dropna().sort_values('lon').reset_index(drop=True)

    wsp_obs=wsp_obs.where(wsp_obs.iloc[:,6]>mingust_obs).dropna()

    if is_return_data:
        dataret = {'wsp_fcst': wsp_fcst,
                    'obs_ver': wsp_obs,
                    'obsdir_ver':wspdir_obs}
        ret.update({'data': dataret})
    if is_draw:
        drawret = draw_veri_synop.draw_veri_gust10m(
                    wsp_fcst,wsp_obs,wspdir_obs,
                    map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


if __name__ == '__main__':
    import datetime
    import matplotlib.pyplot as plt
    # anl_time=datetime.datetime(2020,7,16,8)
    # output_dir = './test_output'
    veri_wsp(init_time='2021110608',fhour=24,area='华北',data_source='cmadaas',data_name='ecmwf',title='test',
                add_city=False,obs_ver='wsp10min',obsdir_ver='wdir10min'
            )
    plt.show()        