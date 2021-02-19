# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

import metdig.metdig_graphics.pallete_set as pallete_set
import metdig.metdig_graphics.draw_method as draw_method
from metdig.metdig_graphics.lib.utility import get_imgbuf_from_fig
import datetime

def draw_compare_gh_uv(hgt_ana, u_ana, v_ana,
                      hgt_fcst, u_fcst, v_fcst,
                      map_extent=(60, 145, 15, 55),
                      add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                      output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                      hgt_contour_kwargs={}, uv_barbs_kwargs={}, prmsl_contourf_kwargs={}
                      ):

    init_time = pd.to_datetime(hgt_fcst.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u_fcst['dtime'].values[0])
    fcstTime = init_time + datetime.timedelta(hours=fhour)
    data_name = hgt_ana.attrs['data_name']
    title = '[{}] {}hPa 位势高度, {}hPa 风 预报检验'.format(
        data_name.upper(),
        hgt_ana['level'].values[0],
        u_ana['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n分析时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcstTime, fhour)

    crs = ccrs.PlateCarree()
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    uv_barbs_kwargs['zorder'] = 2
    img_uv_ana = draw_method.uv_barbs(ax, u_ana['lon'].values, v_ana['lat'].values, np.squeeze(u_ana.values) * 2.5, np.squeeze(v_ana.values) * 2.5, **uv_barbs_kwargs)

    hgt_contour_kwargs['zorder'] = 3
    img_hgt_ana, clevs_hgt_ana = draw_method.hgt_contour(ax, hgt_ana['lon'].values, hgt_ana['lat'].values, np.squeeze(hgt_ana.values), **hgt_contour_kwargs)
    plt.clabel(img_hgt_ana, inline=1, fontsize=20, fmt='%.0f', colors='black')

    uv_barbs_kwargs['zorder'] = 2
    img_uv_fcst = draw_method.uv_barbs(ax, u_fcst['lon'].values, v_fcst['lat'].values, np.squeeze(u_fcst.values) * 2.5, np.squeeze(v_fcst.values) * 2.5,color='blue', **uv_barbs_kwargs)

    hgt_contour_kwargs['zorder'] = 3
    img_hgt_fcst, clevs_hgt_fcst = draw_method.hgt_contour(ax, hgt_fcst['lon'].values, hgt_fcst['lat'].values, np.squeeze(hgt_fcst.values),colors='blue', **hgt_contour_kwargs)
    plt.clabel(img_hgt_fcst, inline=1, fontsize=20, fmt='%.0f', colors='blue')

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_位势高度_风_预报检验_分析时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:}小时.png'.format(fcstTime, fhour, data_name.upper())
    ret['png_name'] = png_name
    ret['output_dir'] = output_dir
    if output_dir:
        out_png = os.path.join(output_dir, png_name)
        ret['picpath'] = out_png
        plt.savefig(out_png, dpi=150, bbox_inches='tight')

    if is_return_imgbuf:
        ret['img_buf'] = get_imgbuf_from_fig(fig)

    if is_clean_plt:
        plt.close(fig)

    if is_return_figax:
        ret['fig'] = fig
        ret['ax'] = ax

    return ret