# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from metdig.metdig_graphics.lib import utility as utl

from metdig.metdig_graphics.barbs_method import *
from metdig.metdig_graphics.contour_method import *
from metdig.metdig_graphics.contourf_method import *
from metdig.metdig_graphics.pcolormesh_method import *
from metdig.metdig_graphics.other_method import *
from metdig.metdig_graphics.draw_compose import *


def draw_wind_theta_mpv(cross_mpv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                        st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                        h_pos=[0.125, 0.665, 0.25, 0.2], **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 湿位涡, 沿剖面风'.format(data_name)
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_相当位温_湿位涡_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, **products_kwargs)
    cross_mpv_contourf(obj.ax, cross_mpv)
    cross_theta_contour(obj.ax, cross_theta)
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    barbs_2d(obj.ax,
          cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert),
          cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert),
          xdim='lon', ydim='level', color='k', transform=None, regrid_shape=None)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_wind_theta_absv(cross_absv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         h_pos=[0.125, 0.665, 0.25, 0.2], **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 绝对涡度, 沿剖面风'.format(data_name)
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_相当位温_绝对涡度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, **products_kwargs)
    cross_absv_contourf(obj.ax, cross_absv)
    cross_theta_contour(obj.ax, cross_theta)
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    barbs_2d(obj.ax,
          cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert),
          cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert),
          xdim='lon', ydim='level', color='k', transform=None, regrid_shape=None)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_wind_theta_rh(cross_rh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                       st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                       h_pos=[0.125, 0.665, 0.25, 0.2], **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 相对湿度, 沿剖面风'.format(data_name)
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_相当位温_相对湿度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, **products_kwargs)
    cross_rh_contourf(obj.ax, cross_rh, levels=np.arange(0, 106, 5), cmap='YlGnBu')
    cross_theta_contour(obj.ax, cross_theta)
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    barbs_2d(obj.ax,
          cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert),
          cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert),
          xdim='lon', ydim='level', color='k', transform=None, regrid_shape=None)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_wind_theta_spfh(cross_spfh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         h_pos=[0.125, 0.665, 0.25, 0.2], **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 绝对湿度, 沿剖面风'.format(data_name)
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)

    png_name = '{2}_相当位温_绝对湿度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, **products_kwargs)
    cross_spfh_contourf(obj.ax, cross_spfh, levels=np.arange(0, 20, 2), cmap='YlGnBu')
    cross_theta_contour(obj.ax, cross_theta)
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    barbs_2d(obj.ax,
          cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert),
          cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert),
          xdim='lon', ydim='level', color='k', transform=None, regrid_shape=None)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_wind_tmp_rh(cross_rh, cross_tmp, cross_u, cross_v, cross_u_t, cross_v_n, cross_terrain, hgt,
                     st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                     h_pos=[0.125, 0.665, 0.25, 0.2], **products_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]温度, 相对湿度, 水平风场'.format(data_name)
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
        init_time, fcst_time, fhour)
    png_name = '{2}_温度_相对湿度_水平风场_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, **products_kwargs)
    cross_rh_contourf(obj.ax, cross_rh, levels=np.arange(0, 101, 0.5))
    cross_tmp_contour(obj.ax, cross_tmp)
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    barbs_2d(obj.ax,
          cross_u_t.isel(lon=wind_slc_horz, level=wind_slc_vert),
          cross_v_n.isel(lon=wind_slc_horz, level=wind_slc_vert),
          xdim='lon', ydim='level', color='k', transform=None, regrid_shape=None)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_time_rh_uv_theta(rh, u, v, theta, **products_kwargs):
    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = rh.stda.fcst_time
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '相当位温, 相对湿度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}\nwww.nmc.cn'.format(
        init_time, data_name, points['lon'], points['lat'])
    png_name = '{3}_相当位温_相对湿度_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, **products_kwargs)
    img = obj.ax.contourf(times, rh['level'].values, rh.values.squeeze(), levels=np.arange(0, 100, 5), cmap='YlGnBu', extend='max')
    utl.add_colorbar(obj.ax, img, ticks=[20, 40, 60, 80, 100], label='Relative Humidity',  orientation='vertical', extend='max', pos='right')
    obj.ax.barbs(times, u['level'].values, u.values.squeeze() * 2.5, v.values.squeeze() * 2.5, color='k')
    img = obj.ax.contour(times, theta['level'].values, theta.values.squeeze(), levels=np.arange(250, 450, 5), colors='#F4511E', linewidths=2)
    plt.clabel(img, img.levels[1::2], fontsize=15, colors='#F4511E', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
    return obj.save()


def draw_time_rh_uv_tmp(rh, u, v, tmp, terrain,  **products_kwargs):
    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = rh.stda.fcst_time
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '温度, 相对湿度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}\nwww.nmc.cn'.format(
        init_time, data_name, points['lon'], points['lat'])
    png_name = '{3}_温度_相对湿度_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, **products_kwargs)
    img = obj.ax.contourf(times, rh['level'].values, rh.values.squeeze(), levels=np.arange(0, 101, 0.5), cmap='YlGnBu')
    utl.add_colorbar(obj.ax, img, ticks=[20, 40, 60, 80, 100], label='Relative Humidity',  orientation='vertical', extend='max', pos='right')
    obj.ax.barbs(times, u['level'].values, u.values.squeeze() * 2.5, v.values.squeeze() * 2.5, color='k')
    img = obj.ax.contour(times, tmp['level'].values, tmp.values.squeeze(), levels=np.arange(-100, 100, 2), colors='#F4511E', linewidths=2)
    plt.clabel(img, img.levels[1::2], fontsize=15, colors='#F4511E', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
    _x, _y, _z = times, terrain['level'].values, terrain.values.squeeze()
    if _z.max() > 0:
        cmap = col.LinearSegmentedColormap.from_list('own3', ['#8B4513', '#DAC2AD'])
        obj.ax.contourf(_x, _y, _z, levels=np.arange(0, _z.max(), 0.1), cmap=cmap,  zorder=100)
    return obj.save()
