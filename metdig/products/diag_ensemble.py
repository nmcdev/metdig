
import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as lines

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.quiver_method import *
from metdig.graphics.streamplot_method import *
from metdig.graphics.text_method import *
from metdig.graphics.draw_compose import *


def draw_hgt_spaghetti(hgt,hgt_contour_kwargs={}, map_extent=(60, 145, 15, 55), **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度场 集合预报面条图'.format(
        data_name.upper(),
        hgt['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_集合预报面条图_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    hgt_spaghetti_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)

    control_line = lines.Line2D([], [], color='black',linestyle='dashed', label='控制预报')
    mean_line = lines.Line2D([], [], color='black', label='集合平均')
    leg = obj.ax.legend(handles=[control_line, mean_line], loc=1, framealpha=1)
    leg.set_zorder(100)    
    return obj.save()