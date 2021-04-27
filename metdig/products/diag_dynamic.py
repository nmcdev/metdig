# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.draw_compose import *


def draw_hgt_uv_vvel(hgt, u, v, vvel, map_extent=(60, 145, 15, 55),
                     vvel_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                     **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, {}hPa 风场和垂直气压速度'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0])
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_垂直气压速度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    vvel_pcolormesh(obj.ax, vvel, kwargs=vvel_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()


def draw_hgt_uv_div(hgt, u, v, div, map_extent=(60, 145, 15, 55),
                    div_contourf_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, {}hPa风,水平散度'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_水平散度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    div_contourf(obj.ax, div, levels=np.arange(-10, -1), cmap='Blues_r', extend='min', kwargs=div_contourf_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()

def draw_hgt_uv_vortadv(hgt, u, v, vortadv, map_extent=(60, 145, 15, 55),
                        vortadv_contourf_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, {}hPa风,涡度平流'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0])
    
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_涡度平流_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    vortadv_contourf(obj.ax, vortadv, levels=np.arange(-10, 11, 1), kwargs=vortadv_contourf_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()

def draw_hgt_uv_tmpadv(hgt, u, v, tmpadv, map_extent=(60, 145, 15, 55),
                        tmpadv_contourf_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, {}hPa风,温度平流'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0])
    
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_温度平流_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    tmpadv_contourf(obj.ax, tmpadv, levels=np.arange(-10, 10.1, 1), kwargs=tmpadv_contourf_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()

def draw_uv_fg_thta(u, v, thta, fg, map_extent=(60, 145, 15, 55),
                    thta_contour_kwargs={}, uv_barbs_kwargs={}, fg_pcolormesh_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(u['member'].values[0])

    title = '[{}] {}hPa 锋生函数, 风场和位温'.format(data_name.upper(), u['level'].values[0], u['level'].values[0])
    
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_锋生函数_风场_位温_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    fg_pcolormesh(obj.ax, fg, kwargs=fg_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    contour_2d(obj.ax, thta, levels=np.arange(-60,60,4), colors='red', kwargs=thta_contour_kwargs)
    return obj.save()