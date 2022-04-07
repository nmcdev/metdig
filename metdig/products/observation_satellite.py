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


def draw_fy4a_c009_hgt_uv_wsp(ir, hgt, u, v, wsp, map_extent=(60, 145, 15, 55),
                             ir_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={}, wsp_contour_kwargs={},
                             **pallete_kwargs):

    ir_time = ir.stda.time[0]
    hgt_time = hgt.stda.time[0]
    fhour = hgt.stda.dtime[0]
    data_name = hgt.stda.member[0]
    ir_channel = ir.stda.level[0]  # 卫星数据level代表通道号

    ir_name = '水汽(6.25微米)'
    ir_cmap = 'met/wv_enhancement_r'

    title = '[FY4A] {0:}观测 [{1:}] {2:}hPa高度场 {3:}hPa风场 {4:}hPa风速'.format(ir_name,data_name.upper(),hgt.stda.level[0],u.stda.level[0],wsp.stda.level[0])
    forcast_info = '卫星观测时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n模式起报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2:}小时'.format(
        ir_time, hgt_time, fhour)
    png_name = 'FY4A卫星观测{0:}_观测时间_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时_模式起报时间_{2:%Y}年{2:%m}月{2:%d}日{2:%H}时_预报时效_{3:}小时.png'.format(
        ir_name,ir_time, hgt_time, fhour)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    ir_pcolormesh(obj.ax, ir, cmap=ir_cmap, levels=np.arange(159.3,299.7),kwargs=ir_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, regrid_shape=15, length=5.2, color='black' ,kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, colors='orange' ,kwargs=hgt_contour_kwargs)
    ulj_contour(obj.ax, wsp,colors='red', kwargs=wsp_contour_kwargs)
    return obj.save()


def draw_fy4a_c012_hgt_uv_cape(ir, hgt, u, v, cape, map_extent=(60, 145, 15, 55),
                             ir_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={}, pv_contour_kwargs={},
                             **pallete_kwargs):

    ir_time = ir.stda.time[0]
    hgt_time = hgt.stda.time[0]
    fhour = hgt.stda.dtime[0]
    data_name = hgt.stda.member[0]
    ir_channel = ir.stda.level[0]  # 卫星数据level代表通道号

    ir_name = '红外(10.8微米)'
    ir_cmap = 'met/ir_enhancement1'

    title = '[FY4A] {0:}观测 [{1:}] {2:}hPa高度场 {3:}hPa风场 对流有效位能'.format(ir_name,data_name.upper(),hgt.stda.level[0],u.stda.level[0])
    forcast_info = '卫星观测时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n模式起报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2:}小时'.format(
        ir_time, hgt_time, fhour)
    png_name = 'FY4A卫星观测{0:}_观测时间_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时_模式起报时间_{2:%Y}年{2:%m}月{2:%d}日{2:%H}时_预报时效_{3:}小时.png'.format(
        ir_name,ir_time, hgt_time, fhour)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    ir_pcolormesh(obj.ax, ir, cmap=ir_cmap, levels=np.arange(121.6,336.2),kwargs=ir_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, regrid_shape=15, length=5.2, color='white' ,kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, colors='orange' ,kwargs=hgt_contour_kwargs)
    cape_contour(obj.ax, cape , cb_fontsize=10,kwargs=pv_contour_kwargs)
    return obj.save()

def draw_fy4a_c012_hgt_uv_pv(ir, hgt, u, v, pv, map_extent=(60, 145, 15, 55),
                             ir_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={}, pv_contour_kwargs={},
                             **pallete_kwargs):

    ir_time = ir.stda.time[0]
    hgt_time = hgt.stda.time[0]
    fhour = hgt.stda.dtime[0]
    data_name = hgt.stda.member[0]
    ir_channel = ir.stda.level[0]  # 卫星数据level代表通道号

    ir_name = '红外(10.8微米)'
    ir_cmap = 'met/ir_enhancement1'

    title = '[FY4A] {0:}观测 [{1:}] {2:}hPa高度场 {3:}hPa风场 {4:}hPa位涡'.format(ir_name,data_name.upper(),hgt.stda.level[0],u.stda.level[0],pv.stda.level[0])
    forcast_info = '卫星观测时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n模式起报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2:}小时'.format(
        ir_time, hgt_time, fhour)
    png_name = 'FY4A卫星观测{0:}_观测时间_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时_模式起报时间_{2:%Y}年{2:%m}月{2:%d}日{2:%H}时_预报时效_{3:}小时.png'.format(
        ir_name,ir_time, hgt_time, fhour)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    ir_pcolormesh(obj.ax, ir, cmap=ir_cmap, levels=np.arange(121.6,336.2),kwargs=ir_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, regrid_shape=15, length=5.2, color='white' ,kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, colors='orange' ,kwargs=hgt_contour_kwargs)
    levels=np.arange(5, 31, 5)
    cmap, norm = cm_collected.get_cmap('summer_r', extend='max', levels=levels, isLinear=True)

    pv_contour(obj.ax, pv ,colors=None, levels=levels,linewidths=[0.8,0.8,1.1,1.4,1.7,2.0], cb_fontsize=10,
                cmap=cmap,norm=norm,kwargs=pv_contour_kwargs) #'#86FB0A'
    return obj.save()

def draw_fy4a_c012_hgt_uv_div(ir, hgt, u, v, div, map_extent=(60, 145, 15, 55),
                             ir_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={}, div_contour_kwargs={},
                             **pallete_kwargs):

    ir_time = ir.stda.time[0]
    hgt_time = hgt.stda.time[0]
    fhour = hgt.stda.dtime[0]
    data_name = hgt.stda.member[0]
    ir_channel = ir.stda.level[0]  # 卫星数据level代表通道号

    ir_name = '红外(10.8微米)'
    ir_cmap = 'met/ir_enhancement1'

    title = '[FY4A] {0:}观测 [{1:}] {2:}hPa高度场 {3:}hPa风场 {4:}hPa散度'.format(ir_name,data_name.upper(),hgt.stda.level[0],u.stda.level[0],div.stda.level[0])
    forcast_info = '卫星观测时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n模式起报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2:}小时'.format(
        ir_time, hgt_time, fhour)
    png_name = 'FY4A卫星观测{0:}_观测时间_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时_模式起报时间_{2:%Y}年{2:%m}月{2:%d}日{2:%H}时_预报时效_{3:}小时.png'.format(
        ir_name,ir_time, hgt_time, fhour)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    ir_pcolormesh(obj.ax, ir, cmap=ir_cmap, levels=np.arange(121.6,336.2),kwargs=ir_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, regrid_shape=15, length=5.2, color='white' ,kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, colors='orange' ,kwargs=hgt_contour_kwargs)
    div_contourf(obj.ax, div, levels=np.arange(-12, -1, 2),alpha=0.3,colorbar_kwargs={'pos':'right'},kwargs=div_contour_kwargs)
    return obj.save()


def draw_fy4a_c012_hgt_uv_spfh(ir, hgt, u, v, spfh, map_extent=(60, 145, 15, 55),
                             ir_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={}, spfh_contour_kwargs={},
                             **pallete_kwargs):

    ir_time = ir.stda.time[0]
    hgt_time = hgt.stda.time[0]
    fhour = hgt.stda.dtime[0]
    data_name = hgt.stda.member[0]
    ir_channel = ir.stda.level[0]  # 卫星数据level代表通道号

    ir_name = '红外(10.8微米)'
    ir_cmap = 'met/ir_enhancement1'

    title = '[FY4A] {0:}观测 [{1:}] {2:}hPa高度场 {3:}hPa风场 {4:}hPa比湿'.format(ir_name,data_name.upper(),hgt.stda.level[0],u.stda.level[0],spfh.stda.level[0])
    forcast_info = '卫星观测时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n模式起报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2:}小时'.format(
        ir_time, hgt_time, fhour)
    png_name = 'FY4A卫星观测{0:}_观测时间_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时_模式起报时间_{2:%Y}年{2:%m}月{2:%d}日{2:%H}时_预报时效_{3:}小时.png'.format(
        ir_name,ir_time, hgt_time, fhour)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    ir_pcolormesh(obj.ax, ir, cmap=ir_cmap, levels=np.arange(121.6,336.2),kwargs=ir_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, regrid_shape=15, length=5.2, color='white' ,kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, colors='orange' ,kwargs=hgt_contour_kwargs)
    spfh_contourf(obj.ax, spfh,colorbar_kwargs={'pos':'right'}, kwargs=spfh_contour_kwargs)
    return obj.save()

def draw_fy4a_ir1_hgt_uv_wsp(ir, hgt, u, v, wsp, map_extent=(60, 145, 15, 55),
                             ir_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={}, wsp_contour_kwargs={},
                             **pallete_kwargs):

    ir_time = ir.stda.time[0]
    hgt_time = hgt.stda.time[0]
    fhour = hgt.stda.dtime[0]
    data_name = hgt.stda.member[0]
    ir_channel = ir.stda.level[0]  # 卫星数据level代表通道号

    ir_name = '红外(10.8微米)'
    ir_cmap = 'met/ir_enhancement1'

    title = '[FY4A] {0:}观测 [{1:}] {2:}hPa高度场 {3:}hPa风场 {4:}hPa高空急流'.format(ir_name,data_name.upper(),hgt.stda.level[0],u.stda.level[0],wsp.stda.level[0])
    forcast_info = '卫星观测时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n模式起报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2:}小时'.format(
        ir_time, hgt_time, fhour)
    png_name = 'FY4A卫星观测{0:}_观测时间_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时_模式起报时间_{2:%Y}年{2:%m}月{2:%d}日{2:%H}时_预报时效_{3:}小时.png'.format(
        ir_name,ir_time, hgt_time, fhour)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    ir_pcolormesh(obj.ax, ir, cmap=ir_cmap, levels=np.arange(121.6,336.2),kwargs=ir_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, regrid_shape=15, length=5.2, color='white' ,kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, colors='orange' ,kwargs=hgt_contour_kwargs)
    ulj_contour(obj.ax, wsp, kwargs=wsp_contour_kwargs)
    return obj.save()

def draw_fy2g_ir1_hgt_uv_wsp(ir, hgt, u, v, wsp, map_extent=(60, 145, 15, 55),
                             ir_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={}, wsp_contour_kwargs={},
                             **pallete_kwargs):

    ir_time = ir.stda.time[0]
    hgt_time = hgt.stda.time[0]
    fhour = hgt.stda.dtime[0]
    data_name = hgt.stda.member[0]
    ir_channel = ir.stda.level[0]  # 卫星数据level代表通道号

    ir_name = 'IR1'
    ir_cmap = 'met/ir_enhancement1'

    title = '[FY2G] {0:}观测 [{1:}] {2:}hPa高度场 {3:}hPa风场 {4:}hPa高空急流'.format(ir_name,data_name.upper(),hgt.stda.level[0],u.stda.level[0],wsp.stda.level[0])
    forcast_info = '卫星观测时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n模式起报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2:}小时'.format(
        ir_time, hgt_time, fhour)
    png_name = 'FY2G卫星观测{0:}_观测时间_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时_模式起报时间_{2:%Y}年{2:%m}月{2:%d}日{2:%H}时_预报时效_{3:}小时.png'.format(
        ir_name,ir_time, hgt_time, fhour)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    ir_pcolormesh(obj.ax, ir, cmap=ir_cmap, levels=np.arange(121.6,336.2),kwargs=ir_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, regrid_shape=15, length=5.2, color='white' ,kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, colors='orange' ,kwargs=hgt_contour_kwargs)
    ulj_contour(obj.ax, wsp, kwargs=wsp_contour_kwargs)
    return obj.save()


def draw_fy4air_sounding_hgt(ir, hgt, sounding_u, sounding_v, map_extent=(60, 145, 15, 55),
                             ir_pcolormesh_kwargs={},  hgt_contour_kwargs={}, uv_barbs_kwargs={},
                             **pallete_kwargs):

    ir_time = ir.stda.time[0]
    hgt_time = hgt.stda.fcst_time[0]
    sounding_time = sounding_u.stda.time[0]
    ir_channel = ir.stda.level[0]  # 卫星数据level代表通道号

    if ir_channel == 9:
        ir_name = '水汽图像'
        ir_cmap = 'met/wv_enhancement_r'
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
