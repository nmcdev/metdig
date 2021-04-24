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


def draw_hgt_uv_tcwv(hgt, u, v, tcwv, map_extent=(60, 145, 15, 55),
                     tcwv_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                     **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 整层可降水量'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_整层可降水量_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    tcwv_pcolormesh(obj.ax, tcwv, kwargs=tcwv_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()


def draw_hgt_uv_rh(hgt, u, v, rh, map_extent=(60, 145, 15, 55),
                   rh_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                   **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, {}hPa 相对湿度'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0], rh['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_相对湿度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    rh_pcolormesh(obj.ax, rh, kwargs=rh_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()


def draw_hgt_uv_spfh(hgt, u, v, spfh, map_extent=(60, 145, 15, 55),
                     spfh_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                     **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度, {}hPa 风, {}hPa 绝对湿度'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0], spfh['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_位势高度_风_绝对湿度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    spfh_pcolormesh(obj.ax, spfh, kwargs=spfh_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()


def draw_hgt_uv_wvfl(hgt, u, v, wvfl, map_extent=(60, 145, 15, 55),
                     wvfl_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                     **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度, {}hPa 风, {}hPa 水汽通量'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0], wvfl['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_位势高度场_风场_水汽通量_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    wvfl_pcolormesh(obj.ax, wvfl, kwargs=wvfl_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()
