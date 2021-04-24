# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl

import metdig.graphics.pallete_set as pallete_set


def draw_uv_tmp_rh_rain(t2m, u10m, v10m, rh2m, rain, wsp, output_dir=None,
                        is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):

    init_time = pd.to_datetime(t2m['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    hourstep = int(rain['dtime'].values[1] - rain['dtime'].values[0])

    data_name = t2m.stda.member_name[0]
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
    t2m_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), t2m['time'].values, t2m['dtime'].values))
    t2m_y = t2m.iloc[:, t2m.attrs['data_start_columns']]
    curve_t2m = ax_t2m.plot(t2m_x, t2m_y, c='#FF6600', linewidth=3, label='气温')
    ax_t2m.set_xlim(t2m_x[0] - pd.Timedelta(hours=1), t2m_x[-1] + pd.Timedelta(hours=1))
    ax_t2m.set_ylim(
        np.min([np.floor(t2m_y.min() / 5) * 5 - 2, 0]),
        np.max([np.ceil(t2m_y.max() / 5) * 5, 40])
    )

    # wsp
    wsp_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), wsp['time'].values, wsp['dtime'].values))
    wsp_y = wsp.iloc[:, wsp.attrs['data_start_columns']]
    curve_wsp = ax_t2m.plot(wsp_x, wsp_y, c='#282C5A', linewidth=3, label='10米风')

    # rain
    rain_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), rain['time'].values, rain['dtime'].values))
    rain_y = rain.iloc[:, rain.attrs['data_start_columns']]
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
    rh2m_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), rh2m['time'].values, rh2m['dtime'].values))
    rh2m_y = rh2m.iloc[:, rh2m.attrs['data_start_columns']]
    curve_rh = ax_rh2m.plot(rh2m_x, rh2m_y, c='#067907', linewidth=3, label='相对湿度')
    ax_rh2m.set_ylim(0, 100)

    # 10米风
    uv_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), u10m['time'].values, u10m['dtime'].values))
    u_y = u10m.iloc[:, u10m.attrs['data_start_columns']]
    v_y = v10m.iloc[:, v10m.attrs['data_start_columns']]
    ax_uv.barbs(uv_x, np.zeros(len(uv_x)), u_y, v_y,
                fill_empty=True, color='gray', barb_increments={'half': 2, 'full': 4, 'flag': 20},
                length=5.8, linewidth=1.5, zorder=100)
    ax_uv.set_ylim(-1, 1)
    ax_uv.set_xlim(uv_x[0] - datetime.timedelta(hours=1), uv_x[-1] + datetime.timedelta(hours=1))
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
    ret['png_name'] = png_name
    ret['output_dir'] = output_dir

    if output_dir:
        out_png = os.path.join(output_dir, png_name)
        ret['pic_path'] = out_png
        plt.savefig(out_png, idpi=200, bbox_inches='tight')

    if is_return_imgbuf:
        ret['img_buf'] = get_imgbuf_from_fig(fig)

    if is_clean_plt:
        plt.close(fig)

    if is_return_figax:
        ret['fig'] = fig
        ret['ax'] = ax

    return ret


def draw_obs_uv_tmp_rh_rain(tmp, u, v, rh, rain, wsp, output_dir=None,
                            is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):
    init_time = pd.to_datetime(tmp['time'].values[0]).replace(tzinfo=None).to_pydatetime()

    title_left = '{} [{:.2f},{:.2f}]'.format(tmp['id'].values[0], tmp['lon'].values[0], tmp['lat'].values[0])
    title_right = '起报时间：{0:%Y}年{0:%m}月{0:%m}日{0:%H}时'.format(init_time)
    title_right = ''

    t2m_ylabel = '气温($^\circ$C) \n 风速(m s$^-$$^1$) \n 降水(mm)'
    rh_ylabel = '相对湿度(%)'
    uv_ylabel = '风'

    fig, ax_tmp, ax_rh, ax_uv = pallete_set.time_series_left_right_bottom(
        (16, 4.5),
        title_left=title_left, title_right=title_right,
        label_leftax=t2m_ylabel, label_rightax=rh_ylabel, label_bottomax=uv_ylabel
    )

    # tmp
    tmp_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), tmp['time'].values, tmp['dtime'].values))
    tmp_y = tmp.iloc[:, tmp.attrs['data_start_columns']]
    curve_t2m = ax_tmp.plot(tmp_x, tmp_y, c='#FF6600', linewidth=3, label='气温')
    ax_tmp.set_xlim(tmp_x[0] - pd.Timedelta(hours=1), tmp_x[-1] + pd.Timedelta(hours=1))
    ax_tmp.set_ylim(
        np.min([np.floor(tmp_y.min() / 5) * 5 - 2, 0]),
        np.max([np.ceil(tmp_y.max() / 5) * 5, 40])
    )

    # wsp
    wsp_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), wsp['time'].values, wsp['dtime'].values))
    wsp_y = wsp.iloc[:, wsp.attrs['data_start_columns']]
    curve_wsp = ax_tmp.plot(wsp_x, wsp_y, c='#282C5A', linewidth=3, label='风')

    if(rain is not None):
        # rain
        rain_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), rain['time'].values, rain['dtime'].values))
        rain_y = rain.iloc[:, rain.attrs['data_start_columns']]
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
    rh_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), rh['time'].values, rh['dtime'].values))
    rh_y = rh.iloc[:, rh.attrs['data_start_columns']]
    curve_rh = ax_rh.plot(rh_x, rh_y, c='#067907', linewidth=3, label='相对湿度')
    ax_rh.set_ylim(0, 100)

    # 10米风
    uv_x = list(map(lambda a, b: a + pd.Timedelta(hours=b), u['time'].values, u['dtime'].values))
    u_y = u.iloc[:, u.attrs['data_start_columns']]
    v_y = v.iloc[:, v.attrs['data_start_columns']]
    ax_uv.barbs(uv_x, np.zeros(len(uv_x)), u_y, v_y,
                fill_empty=True, color='gray', barb_increments={'half': 2, 'full': 4, 'flag': 20},
                length=5.8, linewidth=1.5, zorder=100)
    ax_uv.set_ylim(-1, 1)
    ax_uv.set_xlim(uv_x[0] - datetime.timedelta(hours=1), uv_x[-1] + datetime.timedelta(hours=1))
    for label in ax_uv.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment('center')

    # add legend
    ax_tmp.legend(fontsize=15, loc='upper right')

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    png_name = '观测_{0}_风_温度_相对湿度_降水_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时起报.jpg'.format(tmp['id'].values[0], init_time)
    ret['png_name'] = png_name
    ret['output_dir'] = output_dir

    if output_dir:
        out_png = os.path.join(output_dir, png_name)
        ret['pic_path'] = out_png
        plt.savefig(out_png, idpi=200, bbox_inches='tight')

    if is_return_imgbuf:
        ret['img_buf'] = get_imgbuf_from_fig(fig)

    if is_clean_plt:
        plt.close(fig)

    if is_return_figax:
        ret['fig'] = fig
        ret['ax'] = ax

    return ret
