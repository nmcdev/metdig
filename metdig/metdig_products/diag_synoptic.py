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


def draw_hgt_uv_prmsl(hgt, u, v, prmsl, map_extent=(60, 145, 15, 55),
                      add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                      output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                      hgt_contour_kwargs={}, uv_barbs_kwargs={}, prmsl_contourf_kwargs={}
                      ):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = hgt.attrs['data_name']
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 海平面气压场'.format(
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
    prmsl_contourf_kwargs['zorder'] = 1
    img_prmsl, clevs_prmsl = draw_method.prmsl_contourf(ax, prmsl['lon'].values, prmsl['lat'].values, np.squeeze(prmsl.values), **prmsl_contourf_kwargs)

    uv_barbs_kwargs['zorder'] = 2
    img_uv = draw_method.uv_barbs(ax, u['lon'].values, u['lat'].values, np.squeeze(u.values) * 2.5, np.squeeze(v.values) * 2.5, **uv_barbs_kwargs)

    hgt_contour_kwargs['zorder'] = 3
    img_hgt, clevs_hgt = draw_method.hgt_contour(ax, hgt['lon'].values, hgt['lat'].values, np.squeeze(hgt.values), **hgt_contour_kwargs)
    plt.clabel(img_hgt, inline=1, fontsize=20, fmt='%.0f', colors='black')

    # add color bar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w, .02])
    cb = plt.colorbar(img_prmsl, cax=cax, ticks=clevs_prmsl, orientation='horizontal', extend='max', extendrect=False)
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('Mean sea level pressure (hPa)', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_位势高度场_风场_海平面气压场_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    ret['png_name'] = png_name
    ret['output_dir'] = output_dir
    if output_dir:
        out_png = os.path.join(output_dir, png_name)
        ret['picpath'] = out_png
        plt.savefig(out_png, idpi=200, bbox_inches='tight')

    if is_return_imgbuf:
        ret['img_buf'] = get_imgbuf_from_fig(fig)

    if is_clean_plt:
        plt.close(fig)

    if is_return_figax:
        ret['fig'] = fig
        ret['ax'] = ax

    return ret


def draw_hgt_uv_rain06(hgt, u, v, rain06, map_extent=(60, 145, 15, 55),
                       add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                       output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                       hgt_contour_kwargs={}, uv_barbs_kwargs={}, rain06_contourf_kwargs={}
                       ):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = hgt.attrs['data_name']
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 6小时降水'.format(
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
    rain06_contourf_kwargs['zorder'] = 1
    img_rain06, clevs_rain06 = draw_method.rain_contourf(ax, rain06['lon'].values, rain06['lat'].values, np.squeeze(rain06.values), **rain06_contourf_kwargs)

    uv_barbs_kwargs['zorder'] = 2
    img_uv = draw_method.uv_barbs(ax, u['lon'].values, u['lat'].values, np.squeeze(u.values) * 2.5, np.squeeze(v.values) * 2.5, **uv_barbs_kwargs)

    hgt_contour_kwargs['zorder'] = 3
    img_hgt, clevs_hgt = draw_method.hgt_contour(ax, hgt['lon'].values, hgt['lat'].values, np.squeeze(hgt.values), **hgt_contour_kwargs)
    plt.clabel(img_hgt, inline=1, fontsize=20, fmt='%.0f', colors='black')

    # add color bar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w, .02])
    cb = plt.colorbar(img_rain06, cax=cax, ticks=clevs_rain06, orientation='horizontal', extend='max', extendrect=False)
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('6h precipitation (mm)', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_位势高度场_风场_降水_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    ret['png_name'] = png_name
    ret['output_dir'] = output_dir
    if output_dir:
        out_png = os.path.join(output_dir, png_name)
        ret['picpath'] = out_png
        plt.savefig(out_png, idpi=200, bbox_inches='tight')

    if is_return_imgbuf:
        ret['img_buf'] = get_imgbuf_from_fig(fig)

    if is_clean_plt:
        plt.close(fig)

    if is_return_figax:
        ret['fig'] = fig
        ret['ax'] = ax

    return ret


def draw_hgt_uv_wsp(hgt, u, v, wsp, map_extent=(60, 145, 15, 55),
                    add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                    output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                    hgt_contour_kwargs={}, uv_barbs_kwargs={}, wsp_pcolormesh_kwargs={}
                    ):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = hgt.attrs['data_name']
    title = '[{}] {}hPa 位势高度场, {}hPa 风场, 风速'.format(
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
    wsp_pcolormesh_kwargs['zorder'] = 1
    img_wsp, clevs_wsp = draw_method.wsp_pcolormesh(ax, wsp['lon'].values, wsp['lat'].values, np.squeeze(wsp.values), **wsp_pcolormesh_kwargs)

    uv_barbs_kwargs['zorder'] = 2
    img_uv = draw_method.uv_barbs(ax, u['lon'].values, u['lat'].values, np.squeeze(u.values) * 2.5, np.squeeze(v.values) * 2.5, **uv_barbs_kwargs)

    hgt_contour_kwargs['zorder'] = 3
    img_hgt, clevs_hgt = draw_method.hgt_contour(ax, hgt['lon'].values, hgt['lat'].values, np.squeeze(hgt.values), **hgt_contour_kwargs)
    plt.clabel(img_hgt, inline=1, fontsize=20, fmt='%.0f', colors='black')

    # add color bar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w, .02])
    cb = plt.colorbar(img_wsp, cax=cax, ticks=clevs_wsp, orientation='horizontal', extend='max', extendrect=False)
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('Wind Speed (m/s)', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_位势高度场_风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    ret['png_name'] = png_name
    ret['output_dir'] = output_dir
    if output_dir:
        out_png = os.path.join(output_dir, png_name)
        ret['picpath'] = out_png
        plt.savefig(out_png, idpi=200, bbox_inches='tight')

    if is_return_imgbuf:
        ret['img_buf'] = get_imgbuf_from_fig(fig)

    if is_clean_plt:
        plt.close(fig)

    if is_return_figax:
        ret['fig'] = fig
        ret['ax'] = ax

    return ret


def draw_pv_div_uv(pv, div, u, v, map_extent=(60, 145, 15, 55),
                   add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                   output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                   pv_contour_kwargs={}, div_contourf_kwargs={}, uv_barbs_kwargs={},
                   ):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = u.attrs['data_name']
    title = '[{}] {}hPa 位涡扰动, 风场, 散度'.format(
        data_name.upper(),
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
    div_contourf_kwargs['zorder'] = 1
    _x, _y, _z = div['lon'].values, div['lat'].values, np.squeeze(div.values)
    _z = 1e5 * _z
    img_div, clevs_div = draw_method.div_contourf(ax, _x, _y, _z, **div_contourf_kwargs)

    uv_barbs_kwargs['zorder'] = 2
    _x, _y, _u, _v = u['lon'].values, u['lat'].values, np.squeeze(u.values) * 2.5, np.squeeze(v.values) * 2.5
    img_uv = draw_method.uv_barbs(ax, _x, _y, _u, _v, **uv_barbs_kwargs)

    pv_contour_kwargs['zorder'] = 3
    _x, _y, _z = pv['lon'].values, pv['lat'].values, np.squeeze(pv.values)
    _z = 1e6 * _z
    img_pv, clevs_pv = draw_method.pv_contour(ax, _x, _y, _z, **pv_contour_kwargs)
    plt.clabel(img_pv, inline=1, fontsize=20, fmt='%.0f', colors='black')

    # add color bar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l, b - 0.04, w, .02])
    cb = plt.colorbar(img_div, cax=cax, ticks=clevs_div, orientation='horizontal', extend='both', extendrect=False)
    cb.ax.tick_params(labelsize='x-large')
    cb.set_label('divergence ($10^-5$ s$^{-1}$)', size=20)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_位涡_风场_散度_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    ret['png_name'] = png_name
    ret['output_dir'] = output_dir
    if output_dir:
        out_png = os.path.join(output_dir, png_name)
        ret['picpath'] = out_png
        plt.savefig(out_png, idpi=200, bbox_inches='tight')

    if is_return_imgbuf:
        ret['img_buf'] = get_imgbuf_from_fig(fig)

    if is_clean_plt:
        plt.close(fig)

    if is_return_figax:
        ret['fig'] = fig
        ret['ax'] = ax

    return ret
