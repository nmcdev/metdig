# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import metdig.graphics.pallete_set as pallete_set
from metdig.graphics.lib.utility import save
from metdig.graphics.draw_compose import skewt_compose
from metdig.graphics.boxplot_method import boxplot_1D
import matplotlib.ticker as ticker
import metpy.calc as mpcalc

def draw_rain_ens_boxplot(rain,rain_boxplot_kwargs={}, **pallete_kwargs):
    """[画集合预报降水箱线图]

    Args:
        rain ([type]): [站点类型stda]
        rain_boxplot_kwargs (dict, optional): [graphics.boxplot_method.boxplot_1D的可选参数]. Defaults to {}.

    Returns:
        [type]: [description]
    """
    init_time = pd.to_datetime(rain['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    data_name = rain.stda.member[0].split('-')[0]
    title_left = '{}预报 {} [{},{}]'.format(data_name.upper(), rain['id'].values[0], rain['lon'].values[0], rain['lat'].values[0])
    title_right = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(init_time)
    png_name = '{0}_降水_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时起报.jpg'.format(rain['id'].values[0], init_time)
    rain_ylabel = str(rain.attrs['valid_time'])+'小时降水(mm)'

    fig, ax_rain, _, _ = pallete_set.time_series_left_right_bottom_v2(
        figsize=(16, 4.5),if_add_bottom=False,if_add_right=False,
        title_left=title_left,title_right=title_right,
        label_leftax=rain_ylabel,kwargs=pallete_kwargs
    )

    boxplot_1D(ax_rain,rain,kwargs=rain_boxplot_kwargs)

    ax_rain.set_ylim(0,np.ceil(np.nanmax(rain.stda.get_value()) / 5) * 5)
    plt.xticks(rotation=30)
    ax_rain.grid(axis='x', ls='--')    
    output_dir = pallete_kwargs.pop('output_dir', None)
    is_return_imgbuf = pallete_kwargs.pop('is_return_imgbuf', False)
    is_clean_plt = pallete_kwargs.pop('is_clean_plt', False)
    is_return_figax = pallete_kwargs.pop('is_return_figax', False)
    is_return_pngname = pallete_kwargs.pop('is_return_pngname', False)
    return save(fig, None, png_name, output_dir, is_return_imgbuf, is_clean_plt, is_return_figax, is_return_pngname)


def draw_t2m_ens_boxplot(t2m,t2m_boxplot_kwargs={}, **pallete_kwargs):

    init_time = pd.to_datetime(t2m['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    data_name = t2m.stda.member[0].split('-')[0]
    title_left = '{}预报 {} [{},{}]'.format(data_name.upper(), t2m['id'].values[0], t2m['lon'].values[0], t2m['lat'].values[0])
    title_right = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(init_time)
    png_name = '{0}_温度_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时起报.jpg'.format(t2m['id'].values[0], init_time)
    t2m_ylabel = '2米温度($^\circ$C)'

    fig, ax_t2m, _, _  = pallete_set.time_series_left_right_bottom_v2(
        figsize=(16, 4.5),if_add_bottom=False,if_add_right=False,
        title_left=title_left,title_right=title_right,
        label_leftax=t2m_ylabel,kwargs=pallete_kwargs
    )

    boxplot_1D(ax_t2m,t2m,kwargs=t2m_boxplot_kwargs)

    ax_t2m.set_ylim(np.floor(np.nanmin(t2m.stda.get_value()) / 5) * 5 - 2,np.ceil(np.nanmax(t2m.stda.get_value()) / 5) * 5)
    plt.xticks(rotation=30)
    ax_t2m.grid(axis='x', ls='--')    
    output_dir = pallete_kwargs.pop('output_dir', None)
    is_return_imgbuf = pallete_kwargs.pop('is_return_imgbuf', False)
    is_clean_plt = pallete_kwargs.pop('is_clean_plt', False)
    is_return_figax = pallete_kwargs.pop('is_return_figax', False)
    is_return_pngname = pallete_kwargs.pop('is_return_pngname', False)
    return save(fig, None, png_name, output_dir, is_return_imgbuf, is_clean_plt, is_return_figax, is_return_pngname)

def draw_uv_tmp_rh_rain(t2m, u10m, v10m, rh2m, rain, wsp=None, **pallete_kwargs):

    init_time = pd.to_datetime(t2m['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    hourstep = int(rain['dtime'].values[1] - rain['dtime'].values[0])

    data_name = t2m.stda.member[0]
    title_left = '{}预报 {} [{},{}]'.format(data_name.upper(), t2m['id'].values[0], t2m['lon'].values[0], t2m['lat'].values[0])
    title_right = '起报时间：{0:%Y}年{0:%m}月{0:%d}日{0:%H}时'.format(init_time)
    png_name=pallete_kwargs.pop('png_name', None)
    if(png_name is None):
        png_name = '{0}_风_温度_相对湿度_降水_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时起报.jpg'.format(t2m['id'].values[0], init_time)

    t2m_ylabel = '2米温度($^\circ$C) \n 10米风(m s$^-$$^1$) \n 逐{}小时降水(mm)'.format(hourstep)
    if(wsp is None):
        t2m_ylabel = '2米温度($^\circ$C) \n 逐{}小时降水(mm)'.format(hourstep)
    rh_ylabel = '相对湿度(%)'
    uv_ylabel = '10m风'

    fig, ax_t2m, ax_rh2m, ax_uv = pallete_set.time_series_left_right_bottom_v2(
        title_left=title_left, title_right=title_right,
        label_leftax=t2m_ylabel, label_rightax=rh_ylabel, label_bottomax=uv_ylabel,kwargs=pallete_kwargs
    )

    # t2m
    t2m_x = t2m.stda.fcst_time.values
    t2m_y = t2m.stda.values
    curve_t2m = ax_t2m.plot(t2m_x, t2m_y, c='#FF6600', linewidth=3, label='气温')
    ax_t2m.set_xlim(t2m_x[0] - pd.Timedelta(hours=1), t2m_x[-1] + pd.Timedelta(hours=1))
    bottom_t2m=np.min([np.floor(t2m_y.min() / 5) * 5 - 2, 0])
    top_t2m=np.max([np.ceil(t2m_y.max() / 5) * 5, 40])
    if(wsp is None):
        top_t2m=np.min([np.ceil(t2m_y.max() / 5) * 5, 40])
    ax_t2m.set_ylim(bottom_t2m, top_t2m)

    # wsp
    if (wsp is not None):
        wsp_x = wsp.stda.fcst_time.values
        wsp_y = wsp.stda.values
        if('var_name' in wsp.attrs.keys()):
            label_wsp=wsp.attrs['var_name']
        curve_wsp = ax_t2m.plot(wsp_x, wsp_y, c='#282C5A', linewidth=3, label=label_wsp)

    # rain
    rain_x = rain.stda.fcst_time.values
    rain_y = rain.stda.values
    bars_rn = ax_t2m.bar(rain_x, rain_y, bottom=bottom_t2m, width=0.05, color='#1E78B4', label='{}小时降水'.format(hourstep))

    def bars_autolabel(ax, rects,bottom=0):
        for rect in rects:
            height = rect.get_height()
            if(height > 0):
                ax.annotate('%.1f' % height,
                            xy=(rect.get_x() + rect.get_width() / 2, height+bottom),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
    bars_autolabel(ax_t2m, bars_rn,bottom=bottom_t2m)

    # rh2m
    rh2m_x = rh2m.stda.fcst_time.values
    rh2m_y = rh2m.stda.values
    curve_rh = ax_rh2m.plot(rh2m_x, rh2m_y, c='#067907', linewidth=3, label='相对湿度')
    ax_rh2m.set_ylim(0, 100)

    # 10米风
    uv_x = u10m.stda.fcst_time.values
    u_y = u10m.stda.values
    v_y = v10m.stda.values
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

    # save
    output_dir = pallete_kwargs.pop('output_dir', None)
    is_return_imgbuf = pallete_kwargs.pop('is_return_imgbuf', False)
    is_clean_plt = pallete_kwargs.pop('is_clean_plt', False)
    is_return_figax = pallete_kwargs.pop('is_return_figax', False)
    is_return_pngname = pallete_kwargs.pop('is_return_pngname', False)
    return save(fig, None, png_name, output_dir, is_return_imgbuf, is_clean_plt, is_return_figax, is_return_pngname)


def draw_element(*stda, draw_type='plot', color='#FF6600', linewidth=3, label='', ylim=None, **pallete_kwargs):

    data_name = stda[0].stda.member[0]
    title_left = '{} {} [{},{}]'.format(data_name.upper(), stda[0]['id'].values[0], stda[0]['lon'].values[0], stda[0]['lat'].values[0])
    png_name=pallete_kwargs.pop('png_name', None)

    fig, ax_left, ax_right, ax_bottom = pallete_set.time_series_left_right_bottom_v2(
        if_add_right=False, if_add_bottom=False,
        title_left=title_left, title_right='',
        label_leftax=label, label_rightax='', label_bottomax='',kwargs=pallete_kwargs
    )
    ax_left.yaxis.set_minor_locator(ticker.AutoLocator()) 
    ax_left.yaxis.set_major_locator(ticker.AutoLocator()) 
    
    _x = stda[0].stda.fcst_time.values
    if draw_type == 'plot':
        _y = stda[0].stda.values
        ax_left.plot(_x, _y, c=color, linewidth=linewidth)
    elif draw_type == 'bar':
        _y = stda[0].stda.values
        bars_rn = ax_left.bar(_x, _y, bottom=0, width=0.05, color=color)
        def bars_autolabel(ax, rects,bottom=0):
            for rect in rects:
                height = rect.get_height()
                if(height > 0):
                    ax.annotate('%.1f' % height,
                                xy=(rect.get_x() + rect.get_width() / 2, height+bottom),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom')
        bars_autolabel(ax_left, bars_rn,bottom=0)
    elif draw_type == 'barbs':
        _u = stda[0].stda.values
        _v = stda[1].stda.values
        _y = np.sqrt(_u**2 + _v**2)
        ax_left.barbs(_x, _y, _u, _v,
                fill_empty=True, color=color, barb_increments={'half': 2, 'full': 4, 'flag': 20},
                length=5.8, linewidth=1.5, zorder=100)

        
    
    ax_left.set_xlim(_x[0] - pd.Timedelta(hours=1), _x[-1] + pd.Timedelta(hours=1))
    if ylim is not None:
        ax_left.set_ylim(ylim[0], ylim[1])
    else:
        _y = stda[0].stda.values
        _bottom = np.floor(_y.min() / 5) * 5
        _top = np.ceil(_y.max() / 5) * 5
        ax_left.set_ylim(_bottom, _top)


    # save
    output_dir = pallete_kwargs.pop('output_dir', None)
    is_return_imgbuf = pallete_kwargs.pop('is_return_imgbuf', False)
    is_clean_plt = pallete_kwargs.pop('is_clean_plt', False)
    is_return_figax = pallete_kwargs.pop('is_return_figax', False)
    is_return_pngname = pallete_kwargs.pop('is_return_pngname', False)
    return save(fig, None, png_name, output_dir, is_return_imgbuf, is_clean_plt, is_return_figax, is_return_pngname)

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
    pres = pres.stda.quantity
    tmp = tmp.stda.quantity
    td = td.stda.quantity

    # draw
    obj = skewt_compose(title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)

    obj.skew.plot(pres, tmp, 'r')
    obj.skew.plot(pres, td, 'g')

    if u is not None and v is not None:
        u = u.stda.quantity
        v = v.stda.quantity
        obj.skew.plot_barbs(pres, u, v,barb_increments={'half': 2, 'full': 4, 'flag': 20})

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

    obj.save()
    return obj.get_mpl()
