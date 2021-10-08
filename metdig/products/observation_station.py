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

import metdig.cal as mdgcal
import metpy.calc as mpcalc
from metpy.units import units


def draw_obs_uv_tmp_rh_rain(tmp, u, v, rh, rain, wsp,
                            **pallete_kwargs):
    init_time = pd.to_datetime(tmp['time'].values[0]).replace(tzinfo=None).to_pydatetime()

    title_left = '{} [{:.2f},{:.2f}]'.format(tmp['id'].values[0], tmp['lon'].values[0], tmp['lat'].values[0])
    title_right = '起报时间：{0:%Y}年{0:%m}月{0:%m}日{0:%H}时'.format(init_time)
    title_right = ''
    png_name = '观测_{0}_风_温度_相对湿度_降水_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时起报.jpg'.format(tmp['id'].values[0], init_time)

    t2m_ylabel = '气温($^\circ$C) \n 风速(m s$^-$$^1$) \n 降水(mm)'
    rh_ylabel = '相对湿度(%)'
    uv_ylabel = '风'

    fig, ax_tmp, ax_rh, ax_uv = pallete_set.time_series_left_right_bottom(
        (16, 4.5),
        title_left=title_left, title_right=title_right,
        label_leftax=t2m_ylabel, label_rightax=rh_ylabel, label_bottomax=uv_ylabel
    )

    # tmp
    tmp_x = tmp.stda.fcst_time.values
    tmp_y = tmp.stda.values
    curve_t2m = ax_tmp.plot(tmp_x, tmp_y, c='#FF6600', linewidth=3, label='气温')
    ax_tmp.set_xlim(tmp_x[0] - pd.Timedelta(hours=1), tmp_x[-1] + pd.Timedelta(hours=1))
    ax_tmp.set_ylim(
        np.min([np.floor(tmp_y.min() / 5) * 5 - 2, 0]),
        np.max([np.ceil(tmp_y.max() / 5) * 5, 40])
    )

    # wsp
    wsp_x = wsp.stda.fcst_time.values
    wsp_y = wsp.stda.values
    curve_wsp = ax_tmp.plot(wsp_x, wsp_y, c='#282C5A', linewidth=3, label='风速')

    if(rain is not None):
        # rain
        rain_x = rain.stda.fcst_time.values
        rain_y = rain.stda.values
        bars_rn = ax_tmp.bar(rain_x, rain_y, width=0.1, color='#1E78B4', label='降水')

    def bars_autolabel(ax, rects):
        for rect in rects:
            height = rect.get_height()
            if(height > 0):
                ax.annotate('%.2f' % height,
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
    if(rain is not None):
        bars_autolabel(ax_tmp, bars_rn)
        bars_autolabel(ax_tmp)

    # rh2m
    rh_x = rh.stda.fcst_time.values
    rh_y = rh.stda.values
    curve_rh = ax_rh.plot(rh_x, rh_y, c='#067907', linewidth=3, label='相对湿度')
    ax_rh.set_ylim(0, 100)

    # 10米风
    if(u is None or v is None):
        ax_uv.set_axis_off()
    else:
        uv_x = u.stda.fcst_time.values
        u_y = u.stda.values
        v_y = v.stda.values
        
        ax_uv.barbs(uv_x, np.zeros(len(uv_x)), u_y, v_y,
                    fill_empty=True, color='gray', barb_increments={'half': 2, 'full': 4, 'flag': 20},
                    length=5.8, linewidth=1.5, zorder=100)
        ax_uv.set_ylim(-1, 1)
        ax_uv.set_xlim(uv_x[0] - pd.Timedelta(hours=1), uv_x[-1] + pd.Timedelta(hours=1))
        for label in ax_uv.get_xticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment('center')

    # add legend
    ax_tmp.legend(fontsize=15, loc='upper right')

    # save
    output_dir = pallete_kwargs.pop('output_dir', None)
    is_return_imgbuf = pallete_kwargs.pop('is_return_imgbuf', False)
    is_clean_plt = pallete_kwargs.pop('is_clean_plt', False)
    is_return_figax = pallete_kwargs.pop('is_return_figax', False)
    is_return_pngname = pallete_kwargs.pop('is_return_pngname', False)
    return save(fig, [ax_tmp, ax_rh, ax_uv], png_name, output_dir, is_return_imgbuf, is_clean_plt, is_return_figax, is_return_pngname)
    
