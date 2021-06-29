
import datetime
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

from metdig.graphics import pallete_set
from metdig.graphics import draw_compose

from metdig.graphics.lib.utility import save

from metdig.graphics.barbs_method import *


def draw_wind_profiler(u, v, id, st_time, ed_time, uv_barbs_kwargs={}, **pallete_kwargs):
    times = u.stda.time

    title = '风廓线雷达时间剖面图'
    forcast_info = '站号: {2}\n开始时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时{0:%M}分\n结束时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时{1:%M}分'.format(
        st_time, ed_time, id)
    png_name = '{2}_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时{0:%M}分_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时{1:%M}分风廓线雷达时间剖面图.png'.format(st_time, ed_time, id)

    obj = draw_compose.cross_timeheight_compose(None, times, title=title, description=forcast_info, png_name=png_name, **pallete_kwargs)
    barbs_2d(obj.ax, u, v, xdim='time', ydim='level', color='k', length=5, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)

    return obj.save()
