# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.plot_method import *
from metdig.graphics.draw_compose import *


def draw_high_low_center(hgt, ids, map_extent=(60, 145, 15, 55),
                         ids_contourf_kwargs={}, hgt_contour_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, 高低压'.format(data_name.upper(), hgt['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_高低压_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    ids_contourf(obj.ax, ids,  kwargs=ids_contourf_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_vortex(u, v, ids, map_extent=(60, 145, 15, 55),
                ids_pcolormesh_kwargs={}, uv_barbs_kwargs={},
                **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    data_name = str(u['member'].values[0])

    title = '[{}] {}hPa 位势高度场, 涡旋'.format(data_name.upper(), u['level'].values[0])

    forcast_info = u.stda.description()
    png_name = '{2}_位势高度场_涡旋_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    mode_pcolormesh(obj.ax, ids, kwargs=ids_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_vortex_trace(u, v, trace, map_extent=(60, 145, 15, 55),
                trace_kwargs={}, 
                **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fcst_time = u.stda.fcst_time
    data_name = str(u['member'].values[0])
    idlist = list(trace['id'].drop_duplicates().values)

    title = '[{}] {}hPa 涡旋轨迹'.format(data_name.upper(), u['level'].values[0])

    forcast_info = '[{0}]\n开始时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n结束时间: {2:%Y}年{2:%m}月{2:%d}日{2:%H}时'.format(
         data_name.upper(), fcst_time.iloc[0], fcst_time.iloc[-1])
    png_name = '{2}_涡旋轨迹_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时.png'.format(fcst_time.iloc[0], fcst_time.iloc[-1], data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    for id in idlist:
        trace_slt = trace.loc[trace.id == id]
        if len(trace_slt) == 1:
            continue
        plot_2d(obj.ax, trace_slt, xdim='lon', ydim='lat', linewidth=3, c=None, marker='.', markersize=13)
    obj.save()
    return obj.get_mpl()


def draw_trough(hgt, graphy, map_extent=(60, 145, 15, 55),
                graphy_plot_kwargs={}, hgt_contour_kwargs={},
                **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, 槽线'.format(data_name.upper(), hgt['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_槽线_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    graphy_plot(obj.ax, graphy, kwargs=graphy_plot_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_reverse_trough(hgt, graphy, map_extent=(60, 145, 15, 55),
                        graphy_plot_kwargs={}, hgt_contour_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, 倒槽'.format(data_name.upper(), hgt['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_倒槽_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    graphy_plot(obj.ax, graphy, kwargs=graphy_plot_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_convergence_line(u, v, graphy, map_extent=(60, 145, 15, 55),
                          graphy_plot_kwargs={}, uv_barbs_kwargs={},
                          **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    data_name = str(u['member'].values[0])

    title = '[{}] {}hPa 位势高度场, 辐合线'.format(data_name.upper(), u['level'].values[0])

    forcast_info = u.stda.description()
    png_name = '{2}_位势高度场_辐合线_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    graphy_plot(obj.ax, graphy, kwargs=graphy_plot_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_shear(u, v, graphy, map_extent=(60, 145, 15, 55),
               graphy_plot_kwargs={}, uv_barbs_kwargs={},
               **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    data_name = str(u['member'].values[0])

    title = '[{}] {}hPa 位势高度场, 切变线'.format(data_name.upper(), u['level'].values[0])

    forcast_info = u.stda.description()
    png_name = '{2}_位势高度场_切变线_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    shear_plot(obj.ax, graphy, kwargs=graphy_plot_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_jet(u, v, wsp, graphy, map_extent=(60, 145, 15, 55),
             graphy_plot_kwargs={}, uv_barbs_kwargs={}, wsp_pcolormesh_kwargs={},
             **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    data_name = str(u['member'].values[0])

    title = '[{}] {}hPa 位势高度场, 急流'.format(data_name.upper(), u['level'].values[0])

    forcast_info = u.stda.description()
    png_name = '{2}_位势高度场_急流_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    wsp_pcolormesh(obj.ax, wsp, kwargs=wsp_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    graphy_plot(obj.ax, graphy, kwargs=graphy_plot_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_subtropical_high(hgt, graphy, map_extent=(60, 145, 15, 55),
                         graphy_plot_kwargs={}, hgt_contour_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, 副高'.format(data_name.upper(), hgt['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_副高_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    graphy_plot(obj.ax, graphy, kwargs=graphy_plot_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_south_asia_high(hgt, graphy, map_extent=(60, 145, 15, 55),
                         graphy_plot_kwargs={}, hgt_contour_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, 南亚高压'.format(data_name.upper(), hgt['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_南亚高压_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    graphy_plot(obj.ax, graphy, kwargs=graphy_plot_kwargs)
    obj.save()
    return obj.get_mpl()
