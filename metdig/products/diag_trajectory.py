# -*- coding: utf-8 -*-

import os
import datetime
import math
import numpy as np
import pandas as pd

from matplotlib.gridspec import GridSpec
import matplotlib.patheffects as mpatheffects

from metdig.graphics.plot_method import *
from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.draw_compose import *


import metdig.graphics.lib.utl_plotmap as utl_plotmap

def draw_trajectory(u, v, trajectories, var_diag=None, dt=None, **products_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fcst_time = u.stda.fcst_time
    data_name = str(u['member'].values[0])
    idlist = list(trajectories['id'].drop_duplicates().values)

    title = '质点追踪路径'
    forcast_info = '[{0}]\n开始时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n结束时间: {2:%Y}年{2:%m}月{2:%d}日{2:%H}时'.format(
         data_name.upper(), fcst_time.iloc[0], fcst_time.iloc[-1])
    if dt is not None:
        forcast_info += '\n追踪步长: {}秒'.format(dt)
    
    png_name = '{2}_质点追踪路径_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时.png'.format(init_time, fcst_time.iloc[0], fcst_time.iloc[-1])
    # 区域放大，使其满足长宽比要求
    map_extent = ( # 数据区域
        np.nanmin(trajectories.lon.values) - 5,
        np.nanmax(trajectories.lon.values) + 5,
        np.nanmin(trajectories.lat.values) - 5,
        np.nanmax(trajectories.lat.values) + 5,
    )
    map_extent = utl_plotmap.adjust_extent_to_aspect_ratio(map_extent, 1.6)
    # 层次放大，到整100层
    levels = np.arange(
        math.ceil(np.nanmax(trajectories.level.values) / 100) * 100,
        math.floor(np.nanmin(trajectories.level.values) / 100) * 100 - 0.1,
        -100,
        dtype='int32',
    )

    ################## 绘图 ##############
    fig = plt.figure(figsize=(16, 16))
    gs = GridSpec(3, 1, height_ratios=[0.55, 0.05, 0.4])  # 定义高度比例
    ax_horizontal = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree()) # 空间分布
    ax_colorbar = fig.add_subplot(gs[1, 0]) # colorbar预留位置
    ax_colorbar.axis('off')
    ax_timepres = fig.add_subplot(gs[2, 0]) # 时间剖面
    # 空间剖面暂时不画，因为每根线的位置不一样
    
    ################## 时间剖面 ##############
    obj = cross_timepres_compose(levels, fcst_time, fig=fig, ax=ax_timepres, title="", description="", png_name=png_name)

    for id in  idlist:
        trajectories_slt = trajectories.loc[trajectories.id == id]
        idx_mark = int(len(trajectories_slt) * 0.20) # 统一标记在20%位置
        x_mark = trajectories_slt.stda.get_dim_value('fcst_time')[idx_mark]
        y_mark = trajectories_slt.stda.get_dim_value('level')[idx_mark]
        if True:
            # 标记点
            t = obj.ax.text(x_mark, y_mark, f'P{id}', ha='left', va='center', size=13)
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                mpatheffects.Normal()])
        if var_diag == 'vvel':
            vvel_lccm_2d(obj.ax, trajectories_slt, xdim='fcst_time', ydim='level', linewidth=3, add_colorbar=False)
        elif var_diag == 'rh':
            rh_lccm_2d(obj.ax, trajectories_slt, xdim='fcst_time', ydim='level', linewidth=3, add_colorbar=False)
        elif var_diag == 'tmp':
            tmp_lccm_2d(obj.ax, trajectories_slt, xdim='fcst_time', ydim='level', linewidth=3, add_colorbar=False)
        elif var_diag == 'theta':
            theta_lccm_2d(obj.ax, trajectories_slt, xdim='fcst_time', ydim='level', linewidth=3, add_colorbar=False)
        else:
            plot_2d(obj.ax, trajectories_slt, xdim='fcst_time', ydim='level', linewidth=3, c=None)

    ################## 空间分布 #################
    obj = horizontal_compose(fig=fig, ax=ax_horizontal, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=products_kwargs)
    # obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=products_kwargs)

    for id in idlist:
        trajectories_slt = trajectories.loc[trajectories.id == id]
        x_mark = trajectories_slt.lon.values[0]
        y_mark = trajectories_slt.lat.values[0]
        if not np.isnan(x_mark) and not np.isnan(y_mark):
            # 标记点
            t = obj.ax.text(x_mark, y_mark, f'P{id}', ha='center', va='center', size=13)
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                mpatheffects.Normal()])
        if var_diag == 'vvel':
            vvel_lccm_2d(obj.ax, trajectories_slt, xdim='lon', ydim='lat', linewidth=6)
        elif var_diag == 'rh':
            rh_lccm_2d(obj.ax, trajectories_slt, xdim='lon', ydim='lat', linewidth=6)
        elif var_diag == 'tmp':
            tmp_lccm_2d(obj.ax, trajectories_slt, xdim='lon', ydim='lat', linewidth=6)
        elif var_diag == 'theta':
            theta_lccm_2d(obj.ax, trajectories_slt, xdim='lon', ydim='lat', linewidth=6)
        else:
            plot_2d(obj.ax, trajectories_slt, xdim='lon', ydim='lat', linewidth=6, c=None)
        
    
    fig.tight_layout() # 调整整体空白
    fig.subplots_adjust(wspace=0.01, hspace=0.01) # 调整子图间距

    obj.save() # 只返回空间图的对象，所以空间图最后画
    return obj.get_mpl()


