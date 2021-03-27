# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

from metdig.metdig_graphics.bars_method import *
from metdig.metdig_graphics.contour_method import *
from metdig.metdig_graphics.contourf_method import *
from metdig.metdig_graphics.pcolormesh_method import *
from metdig.metdig_graphics.draw_compose import *


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
