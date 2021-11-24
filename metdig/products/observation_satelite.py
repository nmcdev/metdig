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


def draw_fy4air_sounding_hgt(ir, hgt, sounding_u, sounding_v, map_extent=(60, 145, 15, 55),
                             ir_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={},
                             **pallete_kwargs):

    ir_time = ir.stda.time[0]
    hgt_time = hgt.stda.fcst_time[0]
    sounding_time = sounding_u.stda.time[0]
    ir_channel = ir.stda.level[0]  # 卫星数据level代表通道号

    if ir_channel == 9:
        ir_name = '水汽图像'
        ir_cmap = 'met/wv_enhancement'
        uv_color = 'black'
    elif ir_channel == 12:
        ir_name = '红外(10.8微米)'
        ir_cmap = 'met/ir_enhancement1'
        uv_color = 'white'

    title = 'FY4A{}观测 探空观测 高度场'.format(ir_name)
    forcast_info = '卫星观测时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n探空观测时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n高度场时间: {2:%Y}年{2:%m}月{2:%d}日{2:%H}时'.format(
        ir_time, sounding_time, hgt_time)
    png_name = '卫星观测{1}_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时.png'.format(ir_time, ir_name)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    ir_pcolormesh(obj.ax, ir, cmap=ir_cmap, kwargs=ir_pcolormesh_kwargs)
    barbs_2d(obj.ax, sounding_u, sounding_v, length=7, lw=1.5, sizes=dict(emptybarb=0.0), regrid_shape=None, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    hgt_contour(obj.ax, hgt, levels=[588], linewidths=4, kwargs=hgt_contour_kwargs)
    return obj.save()
