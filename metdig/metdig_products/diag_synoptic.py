# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as lines

from metdig.metdig_graphics.bars_method import *
from metdig.metdig_graphics.contour_method import *
from metdig.metdig_graphics.contourf_method import *
from metdig.metdig_graphics.pcolormesh_method import *
from metdig.metdig_graphics.quiver_method import *
from metdig.metdig_graphics.draw_compose import *

def draw_syn_composite(hgt500, vort500, u850, v850, wsp200, prmsl, tcwv,
    map_extent=(60, 145, 15, 55), is_return_figax=True, **products_kwargs):
    init_time = pd.to_datetime(hgt500.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt500['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt500['member'].values[0])
    title = '[{}] 天气尺度综合分析图'.format(
        data_name.upper())

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{2}_天气尺度综合分析图_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    
    draw_argv = [(tcwv, tcwv_contourf,{'alpha':1,'cmap':'ncl/WhiteGreen','levels':np.arange(20,70,4),'colorbar_kwargs':{'pos':'right center','orientation':'vertical','label_size':15}}),
                ((u850,v850), uv_quiver,{'color':'#404040'}),
                (wsp200, ulj_contourf,{'alpha':0.6,'colorbar_kwargs':{'pos':'right top','orientation':'vertical','label_size':15}}),
                (vort500, vort_contourf,{'alpha':0.4,'colorbar_kwargs':{'pos':'right bottom','orientation':'vertical','label_size':15}}),
                (hgt500, hgt_contour), (prmsl, prmsl_contour,{'colors':'red','linewidths':0.7,'levels':np.arange(950,1100,4)})]
    # draw_argv = [((u850,v850), uv_barbs,{'label':'850-hPa Jet Core Winds (m/s)'})]


    save = horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent,is_return_figax=is_return_figax, **products_kwargs)

    # save['fig'].axes[5].clabel(fontsize=10, inline=1, inline_spacing=7,fmt='%i', rightside_up=True, use_clabeltext=True)
    # save['fig'].axes[6].clabel(fontsize=10, inline=1, inline_spacing=7,
    #         fmt='%i', rightside_up=True, use_clabeltext=True)

    red_line = lines.Line2D([], [], color='red', label='mean sea leve pressure')
    black_line = lines.Line2D([], [], color='black', label='500hPa geopotential height')
    leg = save['fig'].axes[0].legend(handles=[red_line,black_line], loc=3, title=' ',framealpha=1)
    leg.set_zorder(100)
    return save

def draw_hgt_uv_prmsl(hgt, u, v, prmsl, map_extent=(60, 145, 15, 55), **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 海平面气压场'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_海平面气压场_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    
    draw_argv = [(prmsl, prmsl_contourf), ((u,v), uv_barbs), (hgt, hgt_contour)]
    return horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **products_kwargs)


def draw_hgt_uv_wsp(hgt, u, v, wsp, map_extent=(60, 145, 15, 55), **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 风速'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    
    draw_argv = [(wsp, wsp_pcolormesh), ((u,v), uv_barbs), (hgt, hgt_contour)]
    return horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **products_kwargs)


def draw_pv_div_uv(pv, div, u, v, map_extent=(60, 145, 15, 55), **products_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(u['member'].values[0])
    title = '[{}] {}hPa 位涡扰动, 风场, 散度'.format(
        data_name.upper(),
        u['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{2}_位涡_风场_散度_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    
    draw_argv = [
        (div, div_contourf, {'levels': np.arange(-10, 11, 1), 'cmap': 'PuOr', 'extend':'both', 'alpha':0.5}), 
        ((u,v), uv_barbs), 
        (pv, pv_contour),
        ]
    return horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **products_kwargs)


def draw_hgt_uv_rain06(hgt, u, v, rain06, map_extent=(60, 145, 15, 55), **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 6小时降水'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_降水_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    
    draw_argv = [(rain06, rain_contourf), ((u,v), uv_barbs), (hgt, hgt_contour)]
    return horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **products_kwargs)
