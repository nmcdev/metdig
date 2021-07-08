# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as lines

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.quiver_method import *
from metdig.graphics.text_method import *
from metdig.graphics.draw_compose import *



def draw_syn_composite(
        hgt500, vort500, u850, v850, wsp200, prmsl, tcwv, map_extent=(60, 145, 15, 55),
        is_return_figax=True,
        tcwv_contourf_kwargs={},
        uv_quiver_kwargs={},
        ulj_contourf_kwargs={},
        vort_contourf_kwargs={},
        hgt_contour_kwargs={},
        prmsl_contour_kwargs={},
        **pallete_kwargs):
    init_time = pd.to_datetime(hgt500.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt500['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt500['member'].values[0])
    title = '[{}] 天气尺度综合分析图'.format(data_name.upper())

    forcast_info = hgt500.stda.description()
    png_name = '{2}_天气尺度综合分析图_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    tcwv_contourf(obj.ax, tcwv, alpha=1, cmap='ncl/WhiteGreen', levels=np.arange(20, 70, 4),
                  colorbar_kwargs={'pos': 'right center', 'orientation': 'vertical', 'tick_size':10,'label_size': 10}, kwargs=tcwv_contourf_kwargs)
    uv_quiver(obj.ax, u850, v850, color='#404040', label='850hPa wind', kwargs=uv_quiver_kwargs)
    ulj_contourf(obj.ax, wsp200, alpha=0.6, colorbar_kwargs={'pos': 'right top',
                                                             'orientation': 'vertical','tick_size':10, 'label_size': 10}, kwargs=ulj_contourf_kwargs)
    vort_contourf(obj.ax, vort500, alpha=0.4, colorbar_kwargs={'pos': 'right bottom', 'tick_size':10,
                                                               'orientation': 'vertical','tick_size':10, 'label_size': 10}, kwargs=vort_contourf_kwargs)
    hgt_contour(obj.ax, hgt500, kwargs=hgt_contour_kwargs)
    prmsl_contour(obj.ax, prmsl, colors='red', linewidths=0.7, levels=np.arange(950, 1100, 4), kwargs=prmsl_contour_kwargs)
    uv_label = obj.ax.get_legend_handles_labels()
    red_line = lines.Line2D([], [], color='red', label='mean sea leve pressure')
    black_line = lines.Line2D([], [], color='black', label='500hPa geopotential height')
    leg = obj.ax.legend(handles=uv_label[0]+[red_line, black_line], loc=3, title=None, framealpha=1)
    leg.set_zorder(100)
    return obj.save()


def draw_hgt_uv_prmsl(hgt, u, v, prmsl, map_extent=(60, 145, 15, 55),
                      prmsl_contourf_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                      **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 海平面气压场'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_海平面气压场_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    prmsl_contourf(obj.ax, prmsl, kwargs=prmsl_contourf_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    mslp_highlower_center_text(obj.ax, prmsl, map_extent)
    return obj.save()


def draw_hgt_uv_wsp(hgt, u, v, wsp, map_extent=(60, 145, 15, 55),
                    wsp_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 风速'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    wsp_pcolormesh(obj.ax, wsp, kwargs=wsp_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()


def draw_pv_div_uv(pv, div, u, v, map_extent=(60, 145, 15, 55),
                   div_contourf_kwargs={}, uv_barbs_kwargs={}, pv_contour_kwargs={},
                   **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(u['member'].values[0])
    title = '[{}] {}hPa 位涡扰动, 风场, 散度'.format(
        data_name.upper(),
        u['level'].values[0])

    forcast_info = u.stda.description()
    png_name = '{2}_位涡_风场_散度_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    div_contourf(obj.ax, div, levels=np.arange(-10, 11, 1), cmap='PuOr', extend='both', alpha=0.5, kwargs=div_contourf_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    pv_contour(obj.ax, pv, kwargs=pv_contour_kwargs)
    return obj.save()


def draw_hgt_uv_rain06(hgt, u, v, rain06, map_extent=(60, 145, 15, 55),
                       rain_contourf_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                       **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 6小时降水'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_降水_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    rain_contourf(obj.ax, rain06, kwargs=rain_contourf_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()
