# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.lines as lines
from pint import unit

import metdig.graphics.pallete_set as pallete_set
from metdig.graphics.lib.utility import save

from metdig.graphics.draw_compose import skewt_compose

import metdig.cal as mdgcal
import metpy.calc as mpcalc
from metpy.units import units


def draw_uv_tmp_rh_rain(t2m, u10m, v10m, rh2m, rain, wsp, output_dir=None,
                        is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):

    init_time = pd.to_datetime(t2m['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    hourstep = int(rain['dtime'].values[1] - rain['dtime'].values[0])

    data_name = t2m.stda.member[0]
    title_left = '{}预报 {} [{},{}]'.format(data_name.upper(), t2m['id'].values[0], t2m['lon'].values[0], t2m['lat'].values[0])
    title_right = '起报时间：{0:%Y}年{0:%m}月{0:%m}日{0:%H}时'.format(init_time)

    t2m_ylabel = '2米温度($^\circ$C) \n 10米风(m s$^-$$^1$) \n 逐{}小时降水(mm)'.format(hourstep)
    rh_ylabel = '相对湿度(%)'
    uv_ylabel = '10m风'

    fig, ax_t2m, ax_rh2m, ax_uv = pallete_set.time_series_left_right_bottom(
        (16, 4.5),
        title_left=title_left, title_right=title_right,
        label_leftax=t2m_ylabel, label_rightax=rh_ylabel, label_bottomax=uv_ylabel
    )

    # t2m
    t2m_x = t2m.stda.fcst_time.values
    t2m_y = t2m.stda.get_value()
    curve_t2m = ax_t2m.plot(t2m_x, t2m_y, c='#FF6600', linewidth=3, label='气温')
    ax_t2m.set_xlim(t2m_x[0] - pd.Timedelta(hours=1), t2m_x[-1] + pd.Timedelta(hours=1))
    ax_t2m.set_ylim(
        np.min([np.floor(t2m_y.min() / 5) * 5 - 2, 0]),
        np.max([np.ceil(t2m_y.max() / 5) * 5, 40])
    )

    # wsp
    wsp_x = wsp.stda.fcst_time.values
    wsp_y = wsp.stda.get_value()
    curve_wsp = ax_t2m.plot(wsp_x, wsp_y, c='#282C5A', linewidth=3, label='10米风')

    # rain
    rain_x = rain.stda.fcst_time.values
    rain_y = rain.stda.get_value()
    bars_rn = ax_t2m.bar(rain_x, rain_y, width=0.1, color='#1E78B4', label='{}小时降水'.format(hourstep))

    def bars_autolabel(ax, rects):
        for rect in rects:
            height = rect.get_height()
            if(height > 0):
                ax.annotate('%.2f' % height,
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
    bars_autolabel(ax_t2m, bars_rn)

    # rh2m
    rh2m_x = rh2m.stda.fcst_time.values
    rh2m_y = rh2m.stda.get_value()
    curve_rh = ax_rh2m.plot(rh2m_x, rh2m_y, c='#067907', linewidth=3, label='相对湿度')
    ax_rh2m.set_ylim(0, 100)

    # 10米风
    uv_x = u10m.stda.fcst_time.values
    u_y = u10m.stda.get_value()
    v_y = v10m.stda.get_value()
    ax_uv.barbs(uv_x, np.zeros(len(uv_x)), u_y, v_y,
                fill_empty=True, color='gray', barb_increments={'half': 2, 'full': 4, 'flag': 20},
                length=5.8, linewidth=1.5, zorder=100)
    ax_uv.set_ylim(-1, 1)
    ax_uv.set_xlim(uv_x[0] - pd.Timedelta(hours=1), uv_x[-1] + pd.Timedelta(hours=1))
    for label in ax_uv.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment('center')

    # add legend
    ax_t2m.legend(fontsize=15, loc='upper right')

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    png_name = '{0}_风_温度_相对湿度_降水_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时起报.jpg'.format(t2m['id'].values[0], init_time)
    return save(fig, None, png_name, output_dir, is_return_imgbuf, is_clean_plt, is_return_figax)



def draw_SkewT(pres, tmp, td, u, v,  **pallete_kwargs):
    init_time = tmp.stda.time[0]
    fhour = tmp.stda.dtime[0]
    point_lon = tmp.stda.lon[0]
    point_lat = tmp.stda.lat[0]
    data_name = tmp.stda.member[0].upper()


    title = ''
    if(fhour != 0):
        png_name = '{2}_探空_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)
    else:
        png_name = '{1}_探空_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时分析.png'.format(init_time, data_name)

    forcast_info = tmp.stda.description_point(describe='探空')

    # 获取带单位的数据
    pres = pres.stda.get_value(xunits=True)
    tmp = tmp.stda.get_value(xunits=True) 
    td = td.stda.get_value(xunits=True)
    u = u.stda.get_value(xunits=True)
    v = v.stda.get_value(xunits=True)

    # draw
    obj = skewt_compose(title=title, description=forcast_info, png_name=png_name, **pallete_kwargs)

    obj.skew.plot(pres, tmp, 'r')
    obj.skew.plot(pres, td, 'g')
    obj.skew.plot_barbs(pres, u, v)
    
    lcl_pres, lcl_tmp = mpcalc.lcl(pres, tmp[0], td[0])
    obj.skew.plot(lcl_pres[0], lcl_tmp[0], 'ko', markerfacecolor='black')

    prof = mpcalc.parcel_profile(pres, tmp[0], td[0])
    obj.skew.plot(pres, prof, 'k', linewidth=2)
    
    obj.skew.shade_cin(pres, tmp, prof)
    obj.skew.shade_cape(pres, tmp, prof)

    obj.skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

    obj.skew.plot_dry_adiabats()
    obj.skew.plot_moist_adiabats()
    obj.skew.plot_mixing_lines()

    td_line = lines.Line2D([], [], color='g', label='露点温度')
    tmp_line = lines.Line2D([], [], color='r', label='温度')
    leg = obj.skew.ax.legend(handles=[td_line, tmp_line], title=None, framealpha=1)

    return obj.save()