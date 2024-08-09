# -*- coding: utf-8 -*-

import os
import datetime
import math
import numpy as np
import pandas as pd

from matplotlib.gridspec import GridSpec

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.draw_compose import *


import metdig.graphics.lib.utl_plotmap as utl_plotmap

def draw_trajectory(u, v, trajectories, dt=None, **products_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fcst_time = u.stda.fcst_time
    data_name = str(u['member'].values[0])
    levels = u['level'].values

    title = '质点追踪路径'
    forcast_info = '[{0}]\n开始时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n结束时间: {2:%Y}年{2:%m}月{2:%d}日{2:%H}时'.format(
         data_name.upper(), fcst_time.iloc[0], fcst_time.iloc[-1])
    if dt is not None:
        forcast_info += '\n追踪步长: {}秒'.format(dt)
    
    png_name = '{2}_质点追踪路径_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时.png'.format(init_time, fcst_time.iloc[0], fcst_time.iloc[-1])
    map_extent = ( # 数据区域
        np.nanmin(trajectories.lon.values) - 5,
        np.nanmax(trajectories.lon.values) + 5,
        np.nanmin(trajectories.lat.values) - 5,
        np.nanmax(trajectories.lat.values) + 5,
    )
    map_extent = utl_plotmap.adjust_extent_to_aspect_ratio(map_extent, 1.6) # 区域放大，使其满足长宽比要求

    ################## 绘图 ##############
    fig = plt.figure(figsize=(16, 16))
    gs = GridSpec(2, 1, height_ratios=[0.6, 0.4])  # 定义高度比例
    
    ################## 时间剖面 ##############
    ax = fig.add_subplot(gs[1, 0])
    obj = cross_timepres_compose(levels, fcst_time, fig=fig, ax=ax, title="", description="", png_name=png_name)

    for id in list(set(trajectories.id)):
        trajectories_slt = trajectories.loc[trajectories.id == id]
        x = trajectories_slt.stda.get_dim_value('fcst_time')
        y = trajectories_slt.stda.get_dim_value('level')
        # v = trajectories_slt.stda.values
        obj.ax.plot(x, y, linewidth=3, label=f'P{id}')

    obj.ax.legend(fontsize=15, loc='upper right')

    ################## 空间分布 #################
    ax = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
    obj = horizontal_compose(fig=fig, ax=ax, title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=products_kwargs)
    # obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=products_kwargs)

    for id in list(set(trajectories.id)):
        trajectories_slt = trajectories.loc[trajectories.id == id]
        lonst = trajectories_slt.lon.values[0]
        latst = trajectories_slt.lat.values[0]
        if not np.isnan(lonst) and not np.isnan(latst):
            # 标记起点
            t = obj.ax.text(lonst, latst, f'P{id}', ha='left', va='top', size=13)
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                mpatheffects.Normal()])
        obj.ax.plot(trajectories_slt.lon.values, trajectories_slt.lat.values, linewidth=6)
    
    fig.tight_layout() # 调整整体空白
    fig.subplots_adjust(wspace=0.01, hspace=0.01) # 调整子图间距

    obj.save() # 只返回空间图的对象
    return obj.get_mpl()


