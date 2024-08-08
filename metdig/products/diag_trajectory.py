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


def draw_trajectory(u, v, trajectories, dt=None, **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fcst_time = u.stda.fcst_time
    data_name = str(u['member'].values[0])

    title = '质点追踪路径'
    forcast_info = '[{0}]\n开始时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n结束时间: {2:%Y}年{2:%m}月{2:%d}日{2:%H}时'.format(
         data_name.upper(), fcst_time.iloc[0], fcst_time.iloc[-1])
    if dt is not None:
        if abs(dt) < 60 or dt % 60 != 0:
            forcast_info += '\n追踪步长: {}秒'.format(dt)
        else:
            forcast_info += '\n追踪步长: {}分钟'.format(dt // 60)
    
    png_name = '{2}_质点追踪路径_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时.png'.format(init_time, fcst_time.iloc[0], fcst_time.iloc[-1])
    map_extent = ( # 数据区域
        np.nanmin(trajectories.lon.values) - 5,
        np.nanmax(trajectories.lon.values) + 5,
        np.nanmin(trajectories.lat.values) - 5,
        np.nanmax(trajectories.lat.values) + 5,
    )
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)

    for id in list(set(trajectories.id)):
        trajectories_slt = trajectories.loc[trajectories.id == id]

        lonst = trajectories_slt.lon.values[0]
        latst = trajectories_slt.lat.values[0]
        if not np.isnan(lonst) and not np.isnan(latst):
            # 标记起点
            t = obj.ax.text(lonst, latst, f'P{id}', ha='left', va='top', size=13)
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                mpatheffects.Normal()])
            # obj.ax.scatter(lonst, latst, c='black', s=50, marker='^')

        obj.ax.plot(trajectories_slt.lon.values, trajectories_slt.lat.values, linewidth=6)


    obj.save()
    return obj.get_mpl()