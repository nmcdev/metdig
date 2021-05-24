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


def draw_hgt_uv_theta(hgt, u, v, theta, map_extent=(60, 145, 15, 55),
                      theta_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                      **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度, {}hPa 风, {}hPa 相当位温'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
        theta['level'].values[0],
    )
    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度_风_相当位温_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    theta_pcolormesh(obj.ax, theta, kwargs=theta_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()


def draw_hgt_uv_tmp(hgt, u, v, tmp, map_extent=(60, 145, 15, 55),
                    tmp_pcolormesh_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, {}hPa 风场, {}hPa 温度'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0],
        tmp['level'].values[0],
    )
    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_温度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    tmp_pcolormesh(obj.ax, tmp, kwargs=tmp_pcolormesh_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()

def draw_hgt_uv_tmpadv(hgt, u, v, tmp, tmpadv, map_extent=(60, 145, 15, 55),
                        tmpadv_contourf_kwargs={}, uv_barbs_kwargs={}, hgt_contour_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0])

    title = '[{}] {}hPa 位势高度场, {}hPa风,温度平流'.format(data_name.upper(), hgt['level'].values[0], u['level'].values[0])
    
    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_温度平流_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    tmpadv_contourf(obj.ax, tmpadv, levels=np.arange(-10, 10.1, 1), kwargs=tmpadv_contourf_kwargs)
    tmp_contour(obj.ax, tmp, levels=np.arange(-60,40,2),colors='red',linestyle='dashed', kwargs=tmpadv_contourf_kwargs)
    uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    return obj.save()
