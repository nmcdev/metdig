# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import cartopy.crs as ccrs

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.draw_compose import *

def draw_cref(cref,map_extent=(60, 145, 15, 55),
                ref_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={},
                **pallete_kwargs):

    cref_time = cref.stda.time[0]

    title = '天气雷达组合反射率观测'
    forcast_info = '观测时间: {0:%m}月{0:%d}日{0:%H}时{0:%M}分（BJT）\nwww.nmc.cn'.format(
        cref_time)
    png_name = '天气雷达组合反射率_{0:%m}月{0:%d}日{0:%H}时{0:%M}分.png'.format(cref_time)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    cref_contourf(obj.ax, cref,  kwargs=ref_pcolormesh_kwargs)
    return obj.save()


def draw_cref_sounding_hgt(cref, hgt, sounding_u, sounding_v, map_extent=(60, 145, 15, 55),
                           ref_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={},
                           **pallete_kwargs):

    cref_time = cref.stda.time[0]
    hgt_time = hgt.stda.fcst_time[0]
    sounding_time = sounding_u.stda.time[0]

    title = '天气雷达组合反射率观测  探空观测 高度场'
    forcast_info = '雷达观测时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n探空观测时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n高度场时间: {2:%Y}年{2:%m}月{2:%d}日{2:%H}时'.format(
        cref_time, sounding_time, hgt_time)
    png_name = '天气雷达组合反射率_位势高度_探空风_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时.png'.format(cref_time)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    cref_pcolormesh(obj.ax, cref,  kwargs=ref_pcolormesh_kwargs)
    barbs_2d(obj.ax, sounding_u, sounding_v, length=7, lw=1.5, sizes=dict(emptybarb=0.0), regrid_shape=None, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    hgt_contour(obj.ax, hgt, levels=[588], linewidths=4, kwargs=hgt_contour_kwargs)
    return obj.save()
