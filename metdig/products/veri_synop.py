# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

import datetime

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.draw_compose import *

def draw_veri_heatwave(tmx24_2m_fcst, tmx24_2m_obs,
                      map_extent=(60, 145, 15, 55),
                      heatwave_scatter_kwargs={}, heatwave_contourf_kwargs={},
                      **pallete_kwargs
                      ):
    # tmx24_2m_obs['level']=2
    # tmx24_2m_fcst_sta=meb.interp_gs_linear(tmx24_2m_fcst,tmx24_2m_obs)
    # tmx24_2m_obs_fcst=meb.combine_on_obTime_id(tmx24_2m_obs,tmx24_2m_fcst_sta)

    init_time = pd.to_datetime(tmx24_2m_fcst.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(tmx24_2m_fcst['dtime'].values[0])
    fcstTime = init_time + datetime.timedelta(hours=fhour)
    data_name = tmx24_2m_fcst['member'].values[0]
    title = '[{}] 高温天气预报检验'.format(data_name.upper())

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n观测时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时'.format(init_time, fcstTime, fhour)
    png_name = '{2}_高温天气_预报检验_分析时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:}小时.png'.format(fcstTime, fhour, data_name.upper())

    
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    heatwave_contourf(obj.ax, tmx24_2m_fcst, kwargs=heatwave_contourf_kwargs)

    col_data=tmx24_2m_obs.attrs['data_start_columns']
    _x = tmx24_2m_obs[tmx24_2m_obs.iloc[:,col_data] >= 33]['lon'].values
    _y = tmx24_2m_obs[tmx24_2m_obs.iloc[:,col_data] >= 33]['lat'].values
    _z = tmx24_2m_obs[tmx24_2m_obs.iloc[:,col_data] >= 33].iloc[:,col_data].values
    cmap, norm = cm_collected.get_cmap('YlOrBr', extend='max', levels=[33,35,37,40])
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)
    obj.ax.scatter(_x,_y,c=_z,s=(_z-33)*3+3,cmap=cmap,transform=ccrs.PlateCarree(), norm=norm,alpha=0.5)

    return obj.save()

def draw_compare_gh_uv(hgt_ana, u_ana, v_ana,
                      hgt_fcst, u_fcst, v_fcst,
                      map_extent=(60, 145, 15, 55),
                      hgt_contour_kwargs={}, uv_barbs_kwargs={},
                      **pallete_kwargs
                      ):

    init_time = pd.to_datetime(hgt_fcst.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u_fcst['dtime'].values[0])
    fcstTime = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt_ana['member'].values[0])
    title = '[{}] {}hPa 位势高度, {}hPa 风 预报检验'.format(
        data_name.upper(),
        hgt_ana['level'].values[0],
        u_ana['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n分析时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时'.format(init_time, fcstTime, fhour)
    png_name = '{2}_位势高度_风_预报检验_分析时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:}小时.png'.format(fcstTime, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    
    uv_barbs(obj.ax, u_ana, v_ana, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt_ana, kwargs=hgt_contour_kwargs)
    uv_barbs(obj.ax, u_fcst, v_fcst, color='blue', kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt_fcst, colors='blue', kwargs=hgt_contour_kwargs)

    return obj.save()