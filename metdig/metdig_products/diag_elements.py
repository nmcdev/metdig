# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

import metdig.metdig_graphics.pallete_set as pallete_set
import metdig.metdig_graphics.draw_method as draw_method
import metdig.metdig_graphics.lib.utl_plotmap as utl_plotmap
from metdig.metdig_graphics.lib.utility import get_imgbuf_from_fig

from scipy.ndimage import gaussian_filter


def draw_tmx(t, map_extent=(60, 145, 15, 55),
             add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
             output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):
    init_time = pd.to_datetime(t.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(t['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = t.attrs['data_name']
    var_cn_name = t.attrs['var_cn_name']
    title = '[{}] {}'.format(data_name.upper(), var_cn_name)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    x = t['lon'].values
    y = t['lat'].values
    z = t.values.squeeze()
    tmx_img = draw_method.tmx_pcolormesh(ax, x, y, z, zorder=1)

    z = gaussian_filter(z, 5)
    draw_method.tmx_contour(ax, x, y, z, zorder=2)
    draw_method.tmx_contour(ax, x, y, z, colors=['#232B99'], levels=[0], zorder=3)

    if add_city:
        utl_plotmap.add_city_values_on_map(ax, t, map_extent=map_extent, zorder=5)

    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w, .02])
    cb = plt.colorbar(tmx_img, cax=cax, orientation='horizontal', extend='both', extendrect=False)
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('°C', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{1}_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时观测_分析的{2}.png'.format(init_time, data_name.upper(), var_cn_name)
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


def draw_mslp_gust(gust, prmsl, map_extent=(60, 145, 15, 55),
                   add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                   output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):
    init_time = pd.to_datetime(gust.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(gust['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = gust.attrs['data_name']
    var_cn_name = gust.attrs['var_cn_name']
    title = '[{}] 海平面气压 {}'.format(data_name.upper(), var_cn_name)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    x = gust['lon'].values
    y = gust['lat'].values
    z = gust.values.squeeze()
    z = np.where(z < 7.9, np.nan, z)
    gust_img = draw_method.gust_pcolormesh(ax, x, y, z, zorder=1)

    x = prmsl['lon'].values
    y = prmsl['lat'].values
    z = prmsl.values.squeeze()
    z = gaussian_filter(z, 5)
    prmsl_img = ax.contour(x, y, z, np.arange(900, 1100, 2.5), colors='black', linewidths=1, transform=ccrs.PlateCarree(), zorder=2)
    plt.clabel(prmsl_img, inline=1, fontsize=15, fmt='%.0f', colors='black')

    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w, .02])
    cb = plt.colorbar(gust_img, cax=cax, orientation='horizontal', extend='max',
                      ticks=[8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7, 37, 41.5, 46.2, 51.0, 56.1, 61.3])
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('风速 (m/s)', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_海平面气压_{3}_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper(), var_cn_name)
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


def draw_dt2m(dt2m, map_extent=(60, 145, 15, 55),
              add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
              output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):
    init_time = pd.to_datetime(dt2m.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(dt2m['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = dt2m.attrs['data_name']
    var_cn_name = dt2m.attrs['var_cn_name']
    title = '[{}] {}'.format(data_name.upper(), var_cn_name)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    x = dt2m['lon'].values
    y = dt2m['lat'].values
    z = dt2m.values.squeeze()
    dt2m_img = draw_method.dt2m_pcolormesh(ax, x, y, z, alpha=1, vmin=-16, vmax=16, zorder=1)

    z = gaussian_filter(z, 5)
    draw_method.dt2m_contour(ax, x, y, z, alpha=0.5, vmin=-16, vmax=16, zorder=3)

    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w, .02])
    cb = plt.colorbar(dt2m_img, cax=cax, orientation='horizontal', extend='both',
                      ticks=[-16, -12, -10, -8, -6, -4, 0, 4, 6, 8, 10, 12, 16])
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('°C', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_{3}_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper(), var_cn_name)
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
