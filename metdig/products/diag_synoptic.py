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
from metdig.graphics.streamplot_method import *
from metdig.graphics.text_method import *
from metdig.graphics.draw_compose import *

def draw_vpbt(irbt, map_extent=(60, 145, 15, 55),
                    irbt_pcolormesh_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(irbt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(irbt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(irbt['member'].values[0])
    title = '[{}] 模拟卫星水汽图像'.format(
        data_name.upper())

    forcast_info = irbt.stda.description()
    png_name = '{2}_模拟卫星水汽图像_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['vpbt'] = ir_pcolormesh(obj.ax, irbt, cmap='met/wv_enhancement_r', levels=np.arange(121.6,336.2),kwargs=irbt_pcolormesh_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_irbt(irbt, map_extent=(60, 145, 15, 55),
                    irbt_pcolormesh_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(irbt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(irbt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(irbt['member'].values[0])
    title = '[{}] 模拟卫星亮温图像'.format(
        data_name.upper())

    forcast_info = irbt.stda.description()
    png_name = '{2}_模拟卫星亮温图像_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['irbt'] = ir_pcolormesh(obj.ax, irbt, cmap='met/ir_enhancement1', levels=np.arange(121.6,336.2),kwargs=irbt_pcolormesh_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_uvstream_wsp(u, v, wsp, map_extent=(60, 145, 15, 55),
                    wsp_pcolormesh_kwargs={}, uv_streamplot_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(u['member'].values[0])
    title = '[{}] {}hPa 流线, 风速'.format(
        data_name.upper(),
        u['level'].values[0])

    forcast_info = u.stda.description()
    png_name = '{2}_流线_风速_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['wsp'] = wsp_pcolormesh(obj.ax, wsp,levels=np.arange(30,70,4) ,kwargs=wsp_pcolormesh_kwargs)
    obj.img['uv'] = uv_streamplot(obj.ax, u, v, kwargs=uv_streamplot_kwargs)
    obj.save()
    return obj.get_mpl()


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

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['tcwv'] = tcwv_contourf(obj.ax, tcwv, alpha=0.6, cmap='ncl/WhiteGreen', levels=np.arange(20, 70, 4),
                                    colorbar_kwargs={'pos': 'right center', 'orientation': 'vertical', 'tick_size':10,'label_size': 10}, kwargs=tcwv_contourf_kwargs)
    obj.img['uv'] = uv_quiver(obj.ax, u850, v850, color='#404040', label=str(u850.stda.level[0])+'hPa wind', kwargs=uv_quiver_kwargs)
    obj.img['wsp'] = ulj_contourf(obj.ax, wsp200, alpha=0.6, colorbar_kwargs={'pos': 'right top',
                                   'orientation': 'vertical','tick_size':10, 'label_size': 10}, kwargs=ulj_contourf_kwargs)
    obj.img['vort'] = vort_contourf(obj.ax, vort500, alpha=0.4, colorbar_kwargs={'pos': 'right bottom', 'tick_size':10,
                                    'orientation': 'vertical','tick_size':10, 'label_size': 10}, kwargs=vort_contourf_kwargs)
    obj.img['hgt'] = hgt_contour(obj.ax, hgt500, kwargs=hgt_contour_kwargs)
    obj.img['prmsl'] = prmsl_contour(obj.ax, prmsl, colors='red', linewidths=0.7, levels=np.arange(950, 1100, 4), kwargs=prmsl_contour_kwargs)
    uv_label = obj.ax.get_legend_handles_labels()
    red_line = lines.Line2D([], [], color='red', label='mean sea leve pressure')
    black_line = lines.Line2D([], [], color='black', label=str(hgt500.stda.level[0])+'hPa geopotential height')
    leg = obj.ax.legend(handles=uv_label[0]+[red_line, black_line], loc=1, title=None, framealpha=1)
    leg.set_zorder(100)
    obj.save()
    return obj.get_mpl()


def draw_hgt_uv_prmsl(hgt, u, v, prmsl, map_extent=(60, 145, 15, 55),marke_hl=True,
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

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['prmsl'] = prmsl_contourf(obj.ax, prmsl, kwargs=prmsl_contourf_kwargs)
    obj.img['uv'] = uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    obj.img['hgt'] = hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    if(marke_hl):
        mslp_highlower_center_text(obj.ax, prmsl, map_extent)
    obj.save()
    return obj.get_mpl()


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
    png_name = '{2}_位势高度场_风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.jpg'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['wsp'] = wsp_pcolormesh(obj.ax, wsp, kwargs=wsp_pcolormesh_kwargs)
    obj.img['uv'] = uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    obj.img['hgt'] = hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    obj.save()
    return obj.get_mpl()


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

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['div'] = div_contourf(obj.ax, div, levels=np.arange(-10, 11, 1), cmap='PuOr', extend='both', alpha=0.5, kwargs=div_contourf_kwargs)
    obj.img['uv'] = uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    obj.img['pv'] = pv_contour(obj.ax, pv, kwargs=pv_contour_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_hgt_uv_rain06(hgt, u, v, rain06, map_extent=(60, 145, 15, 55),
                       rain_contourf_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                       **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, {}小时降水'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
        rain06.attrs['valid_time'])

    forcast_info = rain06.stda.description()+'(形势场:{}小时)'.format(hgt.stda.dtime[0])
    png_name = '{2}_位势高度场_风场_降水_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['rain'] = rain_contourf(obj.ax, rain06, kwargs=rain_contourf_kwargs)
    obj.img['uv'] = uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    obj.img['hgt'] = hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    obj.save()
    return obj.get_mpl()
