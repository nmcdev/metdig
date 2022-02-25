# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib as mpl
import meteva.base as meb

import datetime
from metdig.graphics import barbs_method
from metdig.graphics import contour_method
from metdig.graphics import contourf_method
from metdig.graphics import pcolormesh_method
import metdig.utl.utl_stda_station as utl_stda_station
from metdig.cal.other import wind_components

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.draw_compose import *
import metdig.graphics.lib.utility as utl

def draw_veri_tmp(tmp_fcst,tmp_bias,
                map_extent=(60, 145, 15, 55),
                tmp_bias_contourf_kwargs={},tmp_bias_contour_kwargs={},tmp_fcst_contour_kwargs={}, 
                **pallete_kwargs):

    init_time = pd.to_datetime(tmp_fcst.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(tmp_fcst['dtime'].values[0])
    fcstTime = init_time + datetime.timedelta(hours=fhour)
    data_name = tmp_fcst['member'].values[0]
    title = '[{0:}] {1:}hPa气温预报检验预报检验'.format(data_name.upper(),tmp_fcst['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n观测时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时'.format(init_time, fcstTime, fhour)
    png_name = '{2:}_{3:}hPa_气温_预报检验_分析时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:}小时.png'.format(fcstTime, fhour, data_name.upper(),tmp_fcst['level'].values[0])
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    contourf_method.contourf_2d(obj.ax,tmp_bias,levels=np.arange(-5,5.1,0.25),cmap='ncl/BlueYellowRed',cb_label='温度偏差 (degC)',kwargs=tmp_bias_contourf_kwargs)
    contour_method.contour_2d(obj.ax,tmp_bias,levels=np.arange(-5.,5.,1),linewidths=0.5,colors='red',cb_colors='red',cb_fontsize=10,kwargs=tmp_bias_contour_kwargs)
    contour_method.contour_2d(obj.ax,tmp_fcst,levels=np.arange(-40,30,2),linewidths=1,kwargs=tmp_fcst_contour_kwargs)

    return obj.save()

def draw_veri_gust10m(gust10m_fcst,gust10m_obs,gustdir10m_obs,
                      map_extent=(60, 145, 15, 55),
                      gust10m_barb_kwargs={},gust10m_pcolormesh_kwargs={},colorbar_kwargs={},
                      **pallete_kwargs
                      ):
    # tmx24_2m_obs['level']=2
    # tmx24_2m_fcst_sta=meb.interp_gs_linear(tmx24_2m_fcst,tmx24_2m_obs)
    # tmx24_2m_obs_fcst=meb.combine_on_obTime_id(tmx24_2m_obs,tmx24_2m_fcst_sta)

    init_time = pd.to_datetime(gust10m_fcst.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(gust10m_fcst['dtime'].values[0])
    fcstTime = init_time + datetime.timedelta(hours=fhour)
    data_name = gust10m_fcst['member'].values[0]
    # title = '[{}] 阵风天气预报检验'.format(data_name.upper())
    title = '[{0:}] {1:}预报检验'.format(data_name.upper(),gust10m_obs.attrs['var_cn_name'])


    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n观测时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时'.format(init_time, fcstTime, fhour)
    png_name = '{2}_阵风天气_预报检验_分析时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:}小时.png'.format(fcstTime, fhour, data_name.upper())

    
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    gust10m_obs=gust10m_obs.where(gust10m_obs['id'].isin(list(set(gust10m_obs['id']).intersection(gustdir10m_obs['id'])))).dropna().reset_index(drop=True)
    gustdir10m_obs=gustdir10m_obs.where(gustdir10m_obs['id'].isin(list(set(gust10m_obs['id']).intersection(gustdir10m_obs['id'])))).dropna().reset_index(drop=True)
    gust10m_fcst_sta=utl_stda_station.gridstda_to_stastda(gust10m_fcst,
                    points={'id':gust10m_obs.stda.get_dim_value('id'),'lon': gust10m_obs.stda.get_dim_value('lon'), 'lat': gust10m_obs.stda.get_dim_value('lat')})
    u_obs,v_obs=wind_components(gust10m_obs,gustdir10m_obs)
    ####绘制模式预报阵风
    pcolormesh_method.gust_pcolormesh(obj.ax,gust10m_fcst,alpha=0.5,colorbar_kwargs={'pos':'right','label':'预报风速 (m/s)'},kwargs=gust10m_pcolormesh_kwargs)

    ####绘制误差
    levels=np.arange(-10,10.5,0.5)
    cmap, norm = cm_collected.get_cmap('ncl/ncl_default', extend='both', levels=levels)
    for ilev,level in enumerate(levels[0:-1]):
        cond=(((gust10m_fcst_sta.iloc[:,6]-gust10m_obs.iloc[:,6])>=levels[ilev]) & ((gust10m_fcst_sta.iloc[:,6]-gust10m_obs.iloc[:,6])<levels[ilev+1]))
        barbs_2d(obj.ax, u_obs.where(cond).dropna(), v_obs.where(cond).dropna(), length=5, lw=0.5, sizes=dict(emptybarb=0.0), regrid_shape=None,
                color=cmap.colors[ilev], kwargs=gust10m_barb_kwargs)
    cond_min=((gust10m_fcst_sta.iloc[:,6]-gust10m_obs.iloc[:,6])>=levels[-1])
    barbs_2d(obj.ax, u_obs.where(cond_min).dropna(), v_obs.where(cond_min).dropna(), length=5, lw=0.5, sizes=dict(emptybarb=0.0), regrid_shape=None,
        color=cmap.colors[-1],kwargs=gust10m_barb_kwargs)
    cond_max=((gust10m_fcst_sta.iloc[:,6]-gust10m_obs.iloc[:,6])<levels[0])
    barbs_2d(obj.ax, u_obs.where(cond_max).dropna(), v_obs.where(cond_max).dropna(), length=5, lw=0.5, sizes=dict(emptybarb=0.0), regrid_shape=None,
                color=cmap.colors[0], kwargs=gust10m_barb_kwargs)
    utl.add_colorbar(obj.ax,mpl.cm.ScalarMappable(norm=norm,cmap=cmap),extend='both',label='deviation (m/s)', kwargs=colorbar_kwargs)

    return obj.save()

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

    
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
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

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    
    uv_barbs(obj.ax, u_ana, v_ana, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt_ana, kwargs=hgt_contour_kwargs)
    uv_barbs(obj.ax, u_fcst, v_fcst, color='blue', kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt_fcst, colors='blue', kwargs=hgt_contour_kwargs)

    return obj.save()