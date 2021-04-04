# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

import metdig.metdig_graphics.pallete_set as pallete_set
import metdig.metdig_graphics.draw_method as draw_method
import metdig.metdig_graphics.lib.utl_plotmap as utl_plotmap
from metdig.metdig_graphics.lib.utility import get_imgbuf_from_fig

from scipy.ndimage import gaussian_filter

from metdig.metdig_graphics.bars_method import *
from metdig.metdig_graphics.contour_method import *
from metdig.metdig_graphics.contourf_method import *
from metdig.metdig_graphics.pcolormesh_method import *
from metdig.metdig_graphics.draw_compose import *
from metdig.metdig_graphics.text_method import *

import metdig.metdig_cal as mdgcal


def draw_tmx(t, map_extent=(60, 145, 15, 55), **products_kwargs):
    init_time = pd.to_datetime(t.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(t['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(t['member'].values[0])
    var_cn_name = t.attrs['var_cn_name']
    title = '[{}] {}'.format(data_name.upper(), var_cn_name)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{1}_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时观测_分析的{2}.png'.format(init_time, data_name.upper(), var_cn_name)

    t_filter = mdgcal.gaussian_filter(t, 5)
    draw_argv = [(t, tmx_pcolormesh), (t, city_text), (t_filter, tmx_contour), (t_filter, tmx_contour, {'levels': [0], 'colors': ['#232B99']})]
    return horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **products_kwargs)


def draw_mslp_gust(gust, prmsl, map_extent=(60, 145, 15, 55), **products_kwargs):
    init_time = pd.to_datetime(gust.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(gust['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(gust['member'].values[0])
    var_cn_name = gust.attrs['var_cn_name']
    title = '[{}] 海平面气压 {}'.format(data_name.upper(), var_cn_name)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{2}_海平面气压_{3}_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper(), var_cn_name)

    draw_argv = [(gust, gust_pcolormesh), (prmsl, prmsl_contour)]
    return horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **products_kwargs)


def draw_dt2m(dt2m, map_extent=(60, 145, 15, 55), **products_kwargs):
    init_time = pd.to_datetime(dt2m.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(dt2m['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(dt2m['member'].values[0])
    var_cn_name = dt2m.attrs['var_cn_name']
    title = '[{}] {}'.format(data_name.upper(), var_cn_name)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)
    png_name = '{2}_{3}_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper(), var_cn_name)

    dt2m_filter = mdgcal.gaussian_filter(dt2m, 5)
    draw_argv = [(dt2m, dt2m_pcolormesh), (dt2m_filter, dt2m_contour)]
    return horizontal_compose(draw_argv, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **products_kwargs)
