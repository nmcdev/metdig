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


def draw_hgt_rain(hgt, rain, map_extent=(60, 145, 15, 55),
                  hgt_contour_kwargs={},
                  **pallete_kwargs):
    init_time = pd.to_datetime(rain.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(rain['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    level = hgt['level'].values[0]

    valid_time = rain.attrs['valid_time']
    data_name = str(rain['member'].values[0])
    var_cn_name = rain.attrs['var_cn_name']
    title = '[{}] {}hPa 位势高度场，{}'.format(data_name.upper(), level, var_cn_name)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时(降水{3}小时)'.format(
        init_time, fcst_time, fhour, fhour + 12)
    png_name = '{2}_高度场_{3}_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper(), var_cn_name)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    qpf_pcolormesh(obj.ax, rain, valid_time=valid_time)
    return obj.save()


def draw_mslp_rain_snow(rain, snow, sleet, prmsl, map_extent=(60, 145, 15, 55),
                        prmsl_contour_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(rain.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(rain['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    valid_time = rain.attrs['valid_time']
    data_name = str(rain['member'].values[0])
    title = '[{}] 海平面气压 {}小时降水'.format(data_name.upper(), valid_time)

    forcast_info = rain.stda.description()
    png_name = '{2}_海平面气压_{3}小时降水_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper(), valid_time)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, **pallete_kwargs)
    rain_snow_sleet_pcolormesh(obj.ax, (rain, snow, sleet), valid_time=valid_time)
    prmsl_contour(obj.ax, prmsl, kwargs=prmsl_contour_kwargs)
    return obj.save()
    