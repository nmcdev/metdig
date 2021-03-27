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


def draw_hgt_uv_theta(hgt, u, v, theta, map_extent=(60, 145, 15, 55), **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度, {}hPa 风, {}hPa 相当位温'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
        theta['level'].values[0],
    )
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{2}_位势高度_风_相当位温_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    draw_argv = [(theta, theta_pcolormesh), ((u,v), uv_barbs), (hgt, hgt_contour)]
    return horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **products_kwargs)


def draw_hgt_uv_tmp(hgt, u, v, tmp, map_extent=(60, 145, 15, 55), **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, {}hPa 风场, {}hPa 温度'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
        tmp['level'].values[0],
    )
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_温度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    
    draw_argv = [(tmp, tmp_pcolormesh), ((u,v), uv_barbs), (hgt, hgt_contour)]
    return horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **products_kwargs)

