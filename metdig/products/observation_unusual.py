
import datetime
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

from metdig.graphics import pallete_set

from metdig.graphics.lib.utility import save

from metdig.graphics.barbs_method import *


def draw_wind_profiler(u, v, id, st_time, ed_time, **pallete_kwargs):

    title = '风廓线雷达时间剖面图'
    forcast_info = '站号: {2}\n开始时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时{0:%M}分\n结束时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时{1:%M}分\n'.format(st_time, ed_time, id)
    png_name = '{2}_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时{0:%M}分_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时{1:%M}分风廓线雷达时间剖面图.png'.format(st_time, ed_time, id)

    pallete_set.plt_base_env()  # 初始化字体中文等

    fig = plt.figure(figsize=(10, 9))
    ax = plt.axes()

    ax.set_title(title, loc='right', fontsize=25)

    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d\n%H:%M'))

    ax.set_ylabel('高度/m', fontsize=15)
    ax.set_yticklabels([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])
    ax.set_xlim(st_time, ed_time)

    barbs_2d(ax, u, v, xdim='time', ydim='level', color='k', length=5, transform=None, regrid_shape=None)

    if forcast_info:
        l, b, w, h = ax.get_position().bounds
        bax = plt.axes([l, b + h, .25, .1], facecolor='#FFFFFFCC')
        bax.axis('off')
        bax.set_yticks([])
        bax.set_xticks([])
        bax.axis([0, 10, 0, 10])
        bax.text(1.5, 0.4, forcast_info, size=11)

    # save
    output_dir = pallete_kwargs.pop('output_dir', None)
    is_return_imgbuf = pallete_kwargs.pop('is_return_imgbuf', False)
    is_clean_plt = pallete_kwargs.pop('is_clean_plt', False)
    is_return_figax = pallete_kwargs.pop('is_return_figax', False)
    is_return_pngname = pallete_kwargs.pop('is_return_pngname', False)
    return save(fig, None, png_name, output_dir, is_return_imgbuf, is_clean_plt, is_return_figax, is_return_pngname)
