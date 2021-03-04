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
from metdig.metdig_graphics.lib import utl_plotmap
from metdig.metdig_graphics.lib import utility as utl


def draw_wind_theta_absv(cross_absv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                         h_pos=[0.125, 0.665, 0.25, 0.2]):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 绝对涡度, 沿剖面风'.format(data_name)
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    # init fig ax
    fig, ax = pallete_set.cross_lonpres_pallete(figsize=(16, 9), levels=levels, title=title, forcast_info=forcast_info)

    # plot absv
    _x = cross_absv['lon'].values
    _y = cross_absv['level'].values
    _z = cross_absv.values.squeeze() * 100000
    absv_contour = draw_method.cross_absv_contourf(ax, _x, _y, _z, levels=np.arange(-60, 60, 1))
    # plot colorbar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l + 0.01 + w, b, 0.015, h])
    cb = plt.colorbar(absv_contour, cax=cax, orientation='vertical', extend='max', extendrect=False)
    cb.set_label('Absolute Vorticity (dimensionless)')

    # plot theta
    _x = cross_theta['lon'].values
    _y = cross_theta['level'].values
    _z = cross_theta.values.squeeze()
    theta_contour = ax.contour(_x, _y, _z, levels=np.arange(250, 450, 5), colors='k', linewidths=2)
    theta_contour.clabel(np.arange(250, 450, 5), fontsize=20, colors='k', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    # plot wind
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    ax.barbs(cross_u['lon'][wind_slc_horz].values,
             cross_u['level'][wind_slc_vert].values,
             cross_u.values.squeeze()[wind_slc_vert, wind_slc_horz] * 2.5,
             cross_v.values.squeeze()[wind_slc_vert, wind_slc_horz] * 2.5, color='k')

    # plot terrain
    _x = cross_terrain['lon'].values
    _y = cross_terrain['level'].values
    _z = cross_terrain.values.squeeze()
    draw_method.cross_terrain_contourf(ax, _x, _y, _z, levels=np.arange(0, 500, 1), zorder=100)

    # plot geopotential height at 500 hPa, plot the path of the cross section
    _x = hgt['lon'].values
    _y = hgt['lat'].values
    _z = hgt.values.squeeze()
    draw_method.cross_section_hgt(_x, _y, _z, levels=np.arange(500, 600, 4), cmap='inferno',
                                  st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross,
                                  map_extent=map_extent, h_pos=h_pos)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_相当位温_绝对涡度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)
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


def draw_wind_theta_rh(cross_rh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                       st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                       output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                       h_pos=[0.125, 0.665, 0.25, 0.2]):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 相对湿度, 沿剖面风'.format(data_name)
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    # init fig ax
    fig, ax = pallete_set.cross_lonpres_pallete(figsize=(16, 9), levels=levels, title=title, forcast_info=forcast_info)

    # plot absv
    _x = cross_rh['lon'].values
    _y = cross_rh['level'].values
    _z = cross_rh.values.squeeze()
    rh_contour = draw_method.cross_rh_contourf(ax, _x, _y, _z, levels=np.arange(0, 106, 5), cmap='YlGnBu')
    # plot colorbar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l + 0.01 + w, b, 0.015, h])
    cb = plt.colorbar(rh_contour, cax=cax, orientation='vertical', extend='max', extendrect=False)
    cb.set_label('Relative Humidity')

    # plot theta
    _x = cross_theta['lon'].values
    _y = cross_theta['level'].values
    _z = cross_theta.values.squeeze()
    theta_contour = ax.contour(_x, _y, _z, levels=np.arange(250, 450, 5), colors='k', linewidths=2)
    theta_contour.clabel(np.arange(250, 450, 5), fontsize=20, colors='k', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    # plot wind
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    ax.barbs(cross_u['lon'][wind_slc_horz].values,
             cross_u['level'][wind_slc_vert].values,
             cross_u.values.squeeze()[wind_slc_vert, wind_slc_horz] * 2.5,
             cross_v.values.squeeze()[wind_slc_vert, wind_slc_horz] * 2.5, color='k')

    # plot terrain
    _x = cross_terrain['lon'].values
    _y = cross_terrain['level'].values
    _z = cross_terrain.values.squeeze()
    draw_method.cross_terrain_contourf(ax, _x, _y, _z, levels=np.arange(0, 500, 1), zorder=100)

    # plot geopotential height at 500 hPa, plot the path of the cross section
    _x = hgt['lon'].values
    _y = hgt['lat'].values
    _z = hgt.values.squeeze()
    draw_method.cross_section_hgt(_x, _y, _z, levels=np.arange(500, 600, 4), cmap='inferno',
                                  st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross,
                                  map_extent=map_extent, h_pos=h_pos)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_相当位温_相对湿度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)
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


def draw_wind_theta_spfh(cross_spfh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                         h_pos=[0.125, 0.665, 0.25, 0.2]):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 绝对湿度, 沿剖面风'.format(data_name)
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    # init fig ax
    fig, ax = pallete_set.cross_lonpres_pallete(figsize=(16, 9), levels=levels, title=title, forcast_info=forcast_info)

    # plot absv
    _x = cross_spfh['lon'].values
    _y = cross_spfh['level'].values
    _z = cross_spfh.values.squeeze()
    spfh_contour = ax.contourf(_x, _y, _z, levels=np.arange(0, 20, 2), cmap='YlGnBu')
    # plot colorbar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l + 0.01 + w, b, 0.015, h])
    cb = plt.colorbar(spfh_contour, cax=cax, orientation='vertical', extend='max', extendrect=False)
    cb.set_label('Specific Humidity (g/kg)')

    # plot theta
    _x = cross_theta['lon'].values
    _y = cross_theta['level'].values
    _z = cross_theta.values.squeeze()
    theta_contour = ax.contour(_x, _y, _z, levels=np.arange(250, 450, 5), colors='k', linewidths=2)
    theta_contour.clabel(np.arange(250, 450, 5), fontsize=20, colors='k', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    # plot wind
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    ax.barbs(cross_u['lon'][wind_slc_horz].values,
             cross_u['level'][wind_slc_vert].values,
             cross_u.values.squeeze()[wind_slc_vert, wind_slc_horz] * 2.5,
             cross_v.values.squeeze()[wind_slc_vert, wind_slc_horz] * 2.5, color='k')

    # plot terrain
    _x = cross_terrain['lon'].values
    _y = cross_terrain['level'].values
    _z = cross_terrain.values.squeeze()
    draw_method.cross_terrain_contourf(ax, _x, _y, _z, levels=np.arange(0, 500, 1), zorder=100)

    # plot geopotential height at 500 hPa, plot the path of the cross section
    _x = hgt['lon'].values
    _y = hgt['lat'].values
    _z = hgt.values.squeeze()
    draw_method.cross_section_hgt(_x, _y, _z, levels=np.arange(500, 600, 4), cmap='inferno',
                                  st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross,
                                  map_extent=map_extent, h_pos=h_pos)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_相当位温_绝对湿度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)
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


def draw_wind_tmp_rh(cross_rh, cross_tmp, cross_u, cross_v, cross_u_t, cross_v_n, cross_terrain, hgt,
                     st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                     output_dir=None, is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,
                     h_pos=[0.125, 0.665, 0.25, 0.2]):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]温度, 相对湿度, 水平风场'.format(data_name)
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(init_time, fcst_time, fhour)

    # init fig ax
    fig, ax = pallete_set.cross_lonpres_pallete(figsize=(16, 9), levels=levels, title=title, forcast_info=forcast_info)

    # plot rh
    _x = cross_rh['lon'].values
    _y = cross_rh['level'].values
    _z = cross_rh.values.squeeze()
    rh_contour = draw_method.cross_rh_contourf(ax, _x, _y, _z, levels=np.arange(0, 101, 0.5))
    # plot colorbar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l + 0.01 + w, b, 0.015, h])
    cb = plt.colorbar(rh_contour, cax=cax, ticks=[20, 40, 60, 80, 100], orientation='vertical', extend='max', extendrect=False)
    cb.set_label('Relative Humidity (%)')

    # plot potential temperature using contour, with some custom labeling
    _x = cross_tmp['lon'].values
    _y = cross_tmp['level'].values
    _z = cross_tmp.values.squeeze()
    draw_method.cross_tmp_contour(ax, _x, _y, _z, levels=np.arange(-100, 100, 2))

    # plot wind
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    ax.barbs(cross_u['lon'][wind_slc_horz].values,
             cross_u['level'][wind_slc_vert].values,
             cross_u_t.values.squeeze()[wind_slc_vert, wind_slc_horz] * 2.5,
             cross_v_n.values.squeeze()[wind_slc_vert, wind_slc_horz] * 2.5, color='k')

    # plot terrain
    _x = cross_terrain['lon'].values
    _y = cross_terrain['level'].values
    _z = cross_terrain.values.squeeze()
    draw_method.cross_terrain_contourf(ax, _x, _y, _z, levels=np.arange(0, 500, 1), zorder=100)

    # plot geopotential height at 500 hPa, plot the path of the cross section
    _x = hgt['lon'].values
    _y = hgt['lat'].values
    _z = hgt.values.squeeze()
    draw_method.cross_section_hgt(_x, _y, _z, levels=np.arange(500, 600, 4), cmap='inferno',
                                  st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross,
                                  map_extent=map_extent, h_pos=h_pos)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{2}_温度_相对湿度_水平风场_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)
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


def draw_time_rh_uv_theta(rh, u, v, theta, output_dir=None,
                          is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,):
    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = rh.stda.get_times()
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '相当位温, 相对湿度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}\nwww.nmc.cn'.format(init_time, data_name, points['lon'], points['lat'])

    # init fig ax
    fig, ax = pallete_set.cross_timepres_pallete(figsize=(16, 9), levels=levels, times=times, title=title, forcast_info=forcast_info)

    # plot rh
    _x = times
    _y = rh['level'].values
    _z = rh.values.squeeze()
    rh_contour = ax.contourf(_x, _y, _z, levels=np.arange(0, 100, 5), cmap='YlGnBu', extend='max')
    # plot colorbar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l + 0.01 + w, b, 0.015, h])
    cb = plt.colorbar(rh_contour, cax=cax, ticks=[20, 40, 60, 80, 100], orientation='vertical', extend='max', extendrect=False)
    cb.set_label('相对湿度（%）', size=15)

    # plot wind
    _x = times
    _y = u['level'].values
    _u = u.values.squeeze() * 2.5
    _v = v.values.squeeze() * 2.5
    ax.barbs(_x, _y, _u, _v, color='k')

    # plot tmp
    # '''
    _x = times
    _y = theta['level'].values
    _z = theta.values.squeeze()
    theta_contour = ax.contour(_x, _y, _z, levels=np.arange(250, 450, 5), colors='#F4511E', linewidths=2)
    theta_contour.clabel(theta_contour.levels[1::2], fontsize=15, colors='#F4511E', inline=1,
                         inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{3}_相当位温_相对湿度_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(init_time, fhours[0], fhours[-1], data_name)
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


def draw_time_rh_uv_tmp(rh, u, v, tmp, terrain, output_dir=None,
                        is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False,):
    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = rh.stda.get_times()
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '温度, 相对湿度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}\nwww.nmc.cn'.format(init_time, data_name, points['lon'], points['lat'])

    # init fig ax
    fig, ax = pallete_set.cross_timepres_pallete(figsize=(16, 9), levels=levels, times=times, title=title, forcast_info=forcast_info)

    # plot rh
    _x = times
    _y = rh['level'].values
    _z = rh.values.squeeze()
    rh_contour = draw_method.cross_rh_contourf(ax, _x, _y, _z, levels=np.arange(0, 101, 0.5), cmap='YlGnBu')
    # plot colorbar
    l, b, w, h = ax.get_position().bounds
    cax = plt.axes([l + 0.01 + w, b, 0.015, h])
    cb = plt.colorbar(rh_contour, cax=cax, ticks=[20, 40, 60, 80, 100], orientation='vertical', extend='max', extendrect=False)
    cb.set_label('相对湿度（%）', size=15)

    # plot wind
    _x = times
    _y = u['level'].values
    _u = u.values.squeeze() * 2.5
    _v = v.values.squeeze() * 2.5
    ax.barbs(_x, _y, _u, _v, color='k')

    # plot tmp
    _x = times
    _y = tmp['level'].values
    _z = tmp.values.squeeze()
    tmp_contour = ax.contour(_x, _y, _z, levels=np.arange(-100, 100, 2), colors='#F4511E', linewidths=2)
    tmp_contour.clabel(tmp_contour.levels[1::2], fontsize=15, colors='#F4511E', inline=1,
                       inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    # plot
    _x = times
    _y = terrain['level'].values
    _z = terrain.values.squeeze()
    if _z.max() > 0:
        draw_method.cross_terrain_contourf(ax, _x, _y, _z, levels=np.arange(0, _z.max(), 0.1), zorder=100)

    ret = {
        'png_name': None,
        'output_dir': None,
        'pic_path': None,
        'img_buf': None,
        'fig': None,
        'ax': None,
    }

    # save
    png_name = '{3}_温度_相对湿度_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(init_time, fhours[0], fhours[-1], data_name)    
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
