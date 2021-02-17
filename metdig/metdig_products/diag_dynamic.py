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
import metdig.metdig_graphics.cmap.cm as cm_collected

def draw_hgt_uv_vvel(hgt, u, v, vvel, map_extent=(60, 145, 15, 55),
                     add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                     output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                     hgt_contour_kwargs={}, uv_barbs_kwargs={}, vvel_pcolormesh_kwargs={}
                     ):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = hgt.attrs['data_name']
    title = '[{}] {}hPa 位势高度场, {}hPa 风场和垂直气压速度'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    # ccrs setting
    # crs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2] + map_extent[3]) / 2.,
    #                            central_longitude=(map_extent[0] + map_extent[1]) / 2.,
    #                            standard_parallels=[30., 60.])
    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    # plot
    _x = vvel['lon'].values
    _y = vvel['lat'].values
    _z = vvel.values.squeeze()
    vvel_pcolormesh_kwargs['zorder'] = 1
    _z = _z * 10  # pa/s => 0.1pa/s
    img_vvel, clevs_vvel = draw_method.vvel_pcolormesh(ax, _x, _y, _z, **vvel_pcolormesh_kwargs)

    _x = u['lon'].values
    _y = u['lat'].values
    _u = u.values.squeeze() * 2.5
    _v = v.values.squeeze() * 2.5
    img_uv = draw_method.uv_barbs(ax, _x, _y, _u, _v, **uv_barbs_kwargs)

    _x = hgt['lon'].values
    _y = hgt['lat'].values
    _z = hgt.values.squeeze()
    hgt_contour_kwargs['zorder'] = 3
    img_hgt, clevs_hgt = draw_method.hgt_contour(ax, _x, _y, _z, **hgt_contour_kwargs)
    plt.clabel(img_hgt, inline=1, fontsize=20, fmt='%.0f', colors='black')

    # add color bar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - h * 0.05, w, h * 0.02])
    cb = plt.colorbar(img_vvel, cax=cax, ticks=clevs_vvel, orientation='horizontal', extend='max', extendrect=False)
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('Vertical Velocity (0.1Pa/s)', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_位势高度场_风场_垂直气压速度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
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


def draw_hgt_uv_div(hgt, u, v, div, map_extent=(60, 145, 15, 55),
                     add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                     output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                     hgt_contour_kwargs={}, uv_barbs_kwargs={}, div_pcolormesh_kwargs={}
                     ):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = hgt.attrs['data_name']
    title = '[{}] {}hPa 位势高度场, {}hPa风,水平散度'.format(
        data_name.upper(),
        hgt['level'].values[0],
        u['level'].values[0])

    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    # ccrs setting
    # crs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2] + map_extent[3]) / 2.,
    #                            central_longitude=(map_extent[0] + map_extent[1]) / 2.,
    #                            standard_parallels=[30., 60.])
    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9), crs=crs, map_extent=map_extent, title=title, forcast_info=forcast_info,
        add_china=add_china, add_city=add_city, add_background=add_background, add_south_china_sea=add_south_china_sea,
    )

    # plot
    _x = div['lon'].values
    _y = div['lat'].values
    _z = div.values.squeeze()
    div_pcolormesh_kwargs['zorder'] = 1
    _z = _z * 1e5
    cmap = cm_collected.get_cmap('Blues_r')
    levels=np.arange(-10,-1)
    img_div, clevs_div = draw_method.div_contourf(ax, _x, _y, _z,alpha=0.8,cmap=cmap,levels=levels,extend='min',**div_pcolormesh_kwargs)

    _x = u['lon'].values
    _y = u['lat'].values
    _u = u.values.squeeze() * 2.5
    _v = v.values.squeeze() * 2.5
    img_uv = draw_method.uv_barbs(ax, _x, _y, _u, _v, **uv_barbs_kwargs)

    _x = hgt['lon'].values
    _y = hgt['lat'].values
    _z = hgt.values.squeeze()
    hgt_contour_kwargs['zorder'] = 3
    img_hgt, clevs_hgt = draw_method.hgt_contour(ax, _x, _y, _z, **hgt_contour_kwargs)
    plt.clabel(img_hgt, inline=1, fontsize=20, fmt='%.0f', colors='black')

    # add color bar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - h * 0.05, w, h * 0.02])
    cb = plt.colorbar(img_div, cax=cax, ticks=clevs_div, orientation='horizontal', extend='max', extendrect=False)
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('Divergence 10'+'$^{-6}$s$^{-1}$', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_位势高度场_风场_水平散度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
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