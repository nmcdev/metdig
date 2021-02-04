# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.patches as mpatches

import metdig.metdig_graphics.pallete_set as pallete_set
import metdig.metdig_graphics.draw_method as draw_method
import metdig.metdig_graphics.lib.utl_plotmap as utl_plotmap
from metdig.metdig_graphics.lib.utility import get_imgbuf_from_fig

from scipy.ndimage import gaussian_filter


def draw_hgt_rain(hgt, rain, map_extent=(60, 145, 15, 55),
                  add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                  output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):
    init_time = pd.to_datetime(rain.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(rain['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    level = hgt['level'].values[0]

    valid_time = rain.attrs['valid_time']
    data_name = rain.attrs['data_name']
    var_cn_name = rain.attrs['var_cn_name']
    title = '[{}] {}hPa 位势高度场，{}'.format(data_name.upper(), level, var_cn_name)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时(降水{3}小时)\nwww.nmc.cn'.format(init_time, fcst_time, fhour, fhour + 12)

    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    x = rain['lon'].values
    y = rain['lat'].values
    z = rain.values.squeeze()
    z = np.where(z < 0.1, np.nan, z)
    rain_img = draw_method.qpf_pcolormesh(ax, x,y,z,valid_time=valid_time, zorder=3)

    x = hgt['lon'].values
    y = hgt['lat'].values
    z = hgt.values.squeeze()
    hgt_img, _ = draw_method.hgt_contour(ax, x, y, z, zorder=3)
    plt.clabel(hgt_img, inline=2, fontsize=20, fmt='%.0f', colors='black')

    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w, .02])
    cb = plt.colorbar(rain_img, cax=cax, orientation='horizontal', extend='max')
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('{}h precipitation (mm)'.format(valid_time), size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_高度场_{3}_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper(), var_cn_name)
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


def draw_mslp_rain_snow(rain, snow, sleet, prmsl, map_extent=(60, 145, 15, 55),
                        add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                        output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):
    init_time = pd.to_datetime(rain.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(rain['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    valid_time = rain.attrs['valid_time']
    data_name = rain.attrs['data_name']
    title = '[{}] 海平面气压 {}小时降水'.format(data_name.upper(), valid_time)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    x = rain['lon'].values
    y = rain['lat'].values
    z = rain.values.squeeze()
    rain_img = draw_method.rain_pcolormesh(ax, x, y, z, valid_time=valid_time, zorder=3)

    x = snow['lon'].values
    y = snow['lat'].values
    z = snow.values.squeeze()
    snow_img = draw_method.snow_pcolormesh(ax, x, y, z, valid_time=valid_time, zorder=3)

    x = sleet['lon'].values
    y = sleet['lat'].values
    z = sleet.values.squeeze()
    sleet_img = draw_method.sleet_pcolormesh(ax, x, y, z, valid_time=valid_time, zorder=3)

    x = prmsl['lon'].values
    y = prmsl['lat'].values
    z = prmsl.values.squeeze()
    z = gaussian_filter(z, 5)
    prmsl_img = ax.contour(x, y, z, np.arange(900, 1100, 2.5), colors='black', linewidths=1, transform=ccrs.PlateCarree(), zorder=3)
    plt.clabel(prmsl_img, inline=1, fontsize=20, fmt='%.0f', colors='black')

    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w * 0.25, .02])
    cb = plt.colorbar(sleet_img, cax=cax, orientation='horizontal', extend='max')
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('雨夹雪 (mm)', size=20)

    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l + w * 0.38, b - 0.04, w * 0.25, .02])
    cb = plt.colorbar(snow_img, cax=cax, orientation='horizontal', extend='max')
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('雪 (mm)', size=20)

    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l + w * 0.75, b - 0.04, w * 0.25, .02])
    cb = plt.colorbar(rain_img, cax=cax, orientation='horizontal')
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('雨 (mm)', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_海平面气压_{3}小时降水_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper(), valid_time)
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


'''
def draw_cumulated_precip(rain, map_extent=(60, 145, 15, 55),
                          add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                          output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):
    init_time = pd.to_datetime(rain.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour_st = int(rain['dtime'].values[0])
    fhour_ed = int(rain['dtime'].values[-1])
    fcst_time_st = init_time + datetime.timedelta(hours=fhour_st)
    fcst_time_ed = init_time + datetime.timedelta(hours=fhour_ed)

    valid_time = rain.attrs['valid_time']
    data_name = rain.attrs['data_name']
    title = '[{}] {}-{}时效累积降水预报 '.format(data_name.upper(), fhour_st, fhour_ed)

    forcast_info = '起始时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n截止时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(fcst_time_st, fcst_time_ed, fhour_ed)

    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    x = rain['lon'].values
    y = rain['lat'].values
    z = rain.values.squeeze()
    znan = np.full_like(z, np.nan, dtype=np.float)
    cmap, norm, _ = dk_ctables.cm_rain_nws(atime=24)
    rain_img = ax.pcolormesh(x, y, znan, norm=norm, cmap=cmap, zorder=1, transform=ccrs.PlateCarree(), alpha=0.5)

    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w, .02])
    cb = plt.colorbar(rain_img, cax=cax, orientation='horizontal')
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('Precipitation (mm)', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{1}_{2}至{3}时效累积降水预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时.png'.format(init_time, data_name.upper(), fhour_st, fhour_ed)
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


def draw_rain_evo(rain, fcs_lvl=4, map_extent=(60, 145, 15, 55),
                  add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                  output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False):

    init_time = pd.to_datetime(rain.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rain['dtime'].values
    fhour_st = int(rain['dtime'].values[0])
    fhour_ed = int(rain['dtime'].values[-1])
    fcst_time_st = init_time + datetime.timedelta(hours=fhour_st)
    fcst_time_ed = init_time + datetime.timedelta(hours=fhour_ed)

    valid_time = rain.attrs['valid_time']
    data_name = rain.attrs['data_name']
    title = '[{}] 预报逐{}小时{}mm降水范围演变'.format(data_name.upper(), valid_time, fcs_lvl)

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n起始时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n终止时间: {2:%Y}年{2:%m}月{2:%d}日{2:%H}时\nwww.nmc.cn'.format(init_time, fcst_time_st, fcst_time_ed)

    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    x = rain['lon'].values
    y = rain['lat'].values
    label_handles = []
    alphas = np.linspace(0.2, 1, len(fhours))
    for itime, fhour in enumerate(fhours):
        z = rain.values.squeeze()[itime, :, :]
        z[z <= 0.1] = np.nan
        per_color = cm_collected.get_part_clev_and_cmap(cmap=mpl.cm.jet, clev_range=[0, len(fhours)], clev_slt=itime)
        ax.contourf(x, y, z, levels=[fcs_lvl, 800], colors=per_color, zorder=3, transform=ccrs.PlateCarree(), alpha=alphas[itime])
        labels = (init_time + datetime.timedelta(hours=int(fhour))).strftime("%m月%d日%H时")
        label_handles.append(mpatches.Patch(color=per_color.reshape(4), alpha=alphas[itime], label=labels))
    ax.legend(handles=label_handles, loc=3, framealpha=1)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{1}_{2}至{3}时效{4}mm降水范围演变_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时.png'.format(init_time, data_name.upper(), fhour_st, fhour_ed, fcs_lvl)
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
'''
