# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.lines as lines

from metdig.graphics.lib import utility as utl

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.quiver_method import *
from metdig.graphics.other_method import *
from metdig.graphics.draw_compose import *

def draw_wind_theta_fg( cross_u, cross_v, cross_theta, cross_fg, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         h_pos=[0.125, 0.665, 0.25, 0.2],
                         fg_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 锋生函数, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_锋生函数_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_fg_contourf(obj.ax, cross_fg, kwargs=fg_contourf_kwargs)
    cross_theta_contour(obj.ax, cross_theta, kwargs=theta_contour_kwargs)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()

def draw_wind_theta_w( cross_u, cross_v, cross_theta, cross_w, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         h_pos=[0.125, 0.665, 0.25, 0.2],
                         w_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 垂直运动速度, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_垂直运动速度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_w_contourf(obj.ax, cross_w, kwargs=w_contourf_kwargs)
    cross_theta_contour(obj.ax, cross_theta, kwargs=theta_contour_kwargs)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()

def draw_wind_theta_div(cross_div, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                       st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                       h_pos=[0.125, 0.665, 0.25, 0.2],
                       div_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                       **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 水平散度, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_水平散度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    div_contourf(obj.ax, cross_div, ydim='level',levels=np.arange(-10, 10,1),extend='both',
                 cmap='RdBu',transform=None,colorbar_kwargs=dict(pos='right',orientation='vertical'),kwargs=div_contourf_kwargs,
                )
    cross_theta_contour(obj.ax, cross_theta, kwargs=theta_contour_kwargs)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()

def draw_time_wind_qcld_qsn_tmp(qcld, qsn, tmp, u, v, terrain, mean_area=None,
                                 qcld_contour_kwargs={},qice_contour_kwargs={}, tmp_contourf_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                                 **pallete_kwargs):

    init_time = pd.to_datetime(qcld['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = qcld['dtime'].values
    times = qcld.stda.fcst_time
    data_name = str(qcld['member'].values[0]).upper()
    levels = qcld['level'].values

    title = '云水比, 雪水比, 温度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_云水比_雪水比_水平风_温度_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    cenlon = u.lon.mean()
    cenlat = u.lat.mean()
    u = u.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    v = v.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    qcld = qcld.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    qsn = qsn.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    tmp = tmp.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    terrain = terrain.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    qcld_contourf(obj.ax, qcld, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right top'}, transform=None, kwargs=qcld_contour_kwargs)
    qsn_contourf(obj.ax, qsn, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right bottom'}, transform=None, kwargs=qice_contour_kwargs)
    barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level',kwargs=tmp_contourf_kwargs)
    if terrain.max() > 0:
        cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, terrain.max(), 0.1), zorder=100,kwargs=terrain_contourf_kwargs)
    red_line = lines.Line2D([], [], color='#0A1F5D', label='temperature')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, brown_line], loc=3, title=None, framealpha=1)
    leg.set_zorder(100)
    return obj.save()

def draw_time_wind_qcld_qice_tmp(qcld, qice, tmp, u, v, terrain, mean_area=None,
                                 qcld_contour_kwargs={},qice_contour_kwargs={}, tmp_contourf_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                                 **pallete_kwargs):

    init_time = pd.to_datetime(qcld['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = qcld['dtime'].values
    times = qcld.stda.fcst_time
    data_name = str(qcld['member'].values[0]).upper()
    levels = qcld['level'].values

    title = '云水比, 冰水比, 温度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_云水比_冰水比_水平风_温度_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    cenlon = u.lon.mean()
    cenlat = u.lat.mean()
    u = u.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    v = v.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    qcld = qcld.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    qice = qice.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    tmp = tmp.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    terrain = terrain.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    qcld_contourf(obj.ax, qcld, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right top'}, transform=None, kwargs=qcld_contour_kwargs)
    qice_contourf(obj.ax, qice, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right bottom'}, transform=None, kwargs=qice_contour_kwargs)
    barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level',kwargs=tmp_contourf_kwargs)
    if terrain.max() > 0:
        cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, terrain.max(), 0.1), zorder=100,kwargs=terrain_contourf_kwargs)
    red_line = lines.Line2D([], [], color='#0A1F5D', label='temperature')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, brown_line], loc=3, title=None, framealpha=1)
    leg.set_zorder(100)
    return obj.save()


def draw_wind_w_tmpadv_tmp(cross_tmpadv, cross_tmp, cross_t, cross_w, cross_terrain, hgt,
                           st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                           h_pos=[0.125, 0.665, 0.25, 0.2],
                           tmpadv_contourf_kwargs={}, tmp_contour_kwargs={}, wind_quiver_kwargs={},terrain_contourf_kwargs={},
                           **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_tmpadv['level'].values

    title = '[{}]温度, 温度平流, 沿剖垂直环流'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_温度_温度平流_沿剖垂直环流_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(3, 100, 3)
    cross_t = cross_t.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_w = cross_w.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    tmpadv_contourf(obj.ax, cross_tmpadv, xdim='lon', ydim='level', transform=None, colorbar_kwargs={'pos': 'right'}, kwargs=tmpadv_contourf_kwargs)
    cross_tmp_contour(obj.ax, cross_tmp, kwargs=tmp_contour_kwargs)
    uv_quiver(obj.ax, cross_t, cross_w, xdim='lon', ydim='level', color='k', scale=800, transform=None, regrid_shape=None, kwargs=wind_quiver_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_wind_tmpadv_tmp(cross_tmpadv, cross_tmp, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         h_pos=[0.125, 0.665, 0.25, 0.2],
                         tmpadv_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]温度, 温度平流, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_温度_温度平流_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    tmpadv_contourf(obj.ax, cross_tmpadv, xdim='lon', ydim='level', transform=None, colorbar_kwargs={'pos': 'right'}, kwargs=tmpadv_contourf_kwargs)
    cross_tmp_contour(obj.ax, cross_tmp, kwargs=tmp_contour_kwargs)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_wind_vortadv_tmp(cross_vortadv, cross_tmp, cross_u, cross_v, cross_terrain, hgt,
                          st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                          h_pos=[0.125, 0.665, 0.25, 0.2],
                          vortadv_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                          **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]温度, 垂直涡度平流, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_温度_垂直涡度平流_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    vortadv_contourf(obj.ax, cross_vortadv, xdim='lon', ydim='level', transform=None,if_mask=False,
                     colorbar_kwargs={'pos': 'right'}, kwargs=vortadv_contourf_kwargs)
    cross_tmp_contour(obj.ax, cross_tmp, kwargs=tmp_contour_kwargs)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()

def draw_wind_thetaes_mpvg(cross_mpvg, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                        st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                        h_pos=[0.125, 0.665, 0.25, 0.2],
                        mpv_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 湿位涡, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_湿位涡_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_mpv_contourf(obj.ax, cross_mpvg, levels=np.arange(-20, 21, 1),kwargs=mpv_contourf_kwargs)
    cross_theta_contour(obj.ax, cross_theta, kwargs=theta_contour_kwargs)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()

def draw_wind_theta_mpv(cross_mpv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                        st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                        h_pos=[0.125, 0.665, 0.25, 0.2],
                        mpv_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 湿位涡, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_湿位涡_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_mpv_contourf(obj.ax, cross_mpv, kwargs=mpv_contourf_kwargs)
    cross_theta_contour(obj.ax, cross_theta, kwargs=theta_contour_kwargs)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_wind_theta_absv(cross_absv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         h_pos=[0.125, 0.665, 0.25, 0.2],
                         absv_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 绝对涡度, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_绝对涡度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_absv_contourf(obj.ax, cross_absv, kwargs=absv_contourf_kwargs)
    cross_theta_contour(obj.ax, cross_theta, kwargs=theta_contour_kwargs)
    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100, kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_wind_theta_rh(cross_rh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                       st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                       h_pos=[0.125, 0.665, 0.25, 0.2],
                       rh_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                       **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 相对湿度, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_相对湿度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_rh_contourf(obj.ax, cross_rh, levels=np.arange(0, 106, 5), kwargs=rh_contourf_kwargs)
    cross_theta_contour(obj.ax, cross_theta, kwargs=theta_contour_kwargs)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()

def draw_wind_w_theta_spfh(cross_spfh, cross_theta, cross_t, cross_w, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         h_pos=[0.125, 0.665, 0.25, 0.2],
                         spfh_contourf_kwargs={}, theta_contour_kwargs={}, wind_quiver_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_spfh['level'].values

    title = '[{}]相当位温, 绝对湿度, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_绝对湿度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(3, 100, 3)
    cross_t = cross_t.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_w = cross_w.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_spfh_contourf(obj.ax, cross_spfh, levels=np.arange(0, 20, 2), cmap='YlGnBu', kwargs=spfh_contourf_kwargs)
    cross_theta_contour(obj.ax, cross_theta, kwargs=theta_contour_kwargs)
    # barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    uv_quiver(obj.ax, cross_t, cross_w, xdim='lon', ydim='level', color='k', scale=800, transform=None, regrid_shape=None, kwargs=wind_quiver_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()

def draw_wind_theta_spfh(cross_spfh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                         h_pos=[0.125, 0.665, 0.25, 0.2],
                         spfh_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]相当位温, 绝对湿度, 沿剖面风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_绝对湿度_沿剖面风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_spfh_contourf(obj.ax, cross_spfh, levels=np.arange(0, 20, 2), cmap='YlGnBu', kwargs=spfh_contourf_kwargs)
    cross_theta_contour(obj.ax, cross_theta, kwargs=theta_contour_kwargs)
    barbs_2d(obj.ax, cross_u, cross_v, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_wind_tmp_rh(cross_rh, cross_tmp, cross_u, cross_v, cross_u_t, cross_v_n, cross_terrain, hgt,
                     st_point=None, ed_point=None, lon_cross=None, lat_cross=None, map_extent=(50, 150, 0, 65),
                     h_pos=[0.125, 0.665, 0.25, 0.2],
                     rh_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                     **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values

    title = '[{}]温度, 相对湿度, 水平风场'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_温度_相对湿度_水平风场_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    cross_u_t = cross_u_t.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v_n = cross_v_n.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_rh_contourf(obj.ax, cross_rh, levels=np.arange(0, 101, 0.5), kwargs=rh_contourf_kwargs)
    cross_tmp_contour(obj.ax, cross_tmp, kwargs=tmp_contour_kwargs)
    barbs_2d(obj.ax, cross_u_t, cross_v_n, xdim='lon', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_terrain_contourf(obj.ax, cross_terrain, levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    return obj.save()


def draw_time_rh_uv_theta(rh, u, v, theta, terrain,rh_contourf_kwargs={}, uv_barbs_kwargs={}, theta_contour_kwargs={},terrain_contourf_kwargs={}, **pallete_kwargs):
    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = rh.stda.fcst_time
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '相当位温, 相对湿度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}'.format(
        init_time, data_name, points['lon'], points['lat'])
    png_name = '{3}_相当位温_相对湿度_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_rh_contourf(obj.ax, rh, xdim='fcst_time', ydim='level', levels=np.arange(0, 100.5, 5), extend='max', kwargs=rh_contourf_kwargs)
    barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_theta_contour(obj.ax, theta, xdim='fcst_time', ydim='level', levels=np.arange(250, 450, 5), colors='#A0522D', kwargs=theta_contour_kwargs)
    if terrain.max() > 0:
        cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, terrain.max(), 0.1), zorder=100,kwargs=terrain_contourf_kwargs)
    return obj.save()


def draw_time_div_vort_spfh_uv(div, vort, spfh, u, v, terrain,
                               spfh_contourf_kwargs={}, uv_barbs_kwargs={}, div_contour_kwargs={}, vort_contourf_kwargs={},
                               **pallete_kwargs):

    init_time = pd.to_datetime(spfh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = spfh['dtime'].values
    times = spfh.stda.fcst_time
    points = {'lon': spfh['lon'].values, 'lat': spfh['lat'].values}
    data_name = str(spfh['member'].values[0]).upper()
    levels = spfh['level'].values

    title = '散度, 垂直涡度, 比湿, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}'.format(
        init_time, data_name, points['lon'], points['lat'])
    png_name = '{3}_散度_垂直涡度_比湿_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_spfh_contourf(obj.ax, spfh, xdim='fcst_time', ydim='level', extend='max', kwargs=spfh_contourf_kwargs)
    barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    div_contour(obj.ax, div, xdim='fcst_time', ydim='level', colors='red', transform=None, kwargs=div_contour_kwargs)
    vort_contour(obj.ax, vort, xdim='fcst_time', ydim='level', colors='black', transform=None, kwargs=div_contour_kwargs)
    if terrain.max() > 0:
        cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, terrain.max(), 0.1), zorder=100)
    red_line = lines.Line2D([], [], color='red', label='horizontal divergence')
    black_line = lines.Line2D([], [], color='black', label='vertical vorticity')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, black_line, brown_line], loc=3, title=None, framealpha=1)
    leg.set_zorder(100)
    return obj.save()


def draw_time_wind_tmpadv_tmp(tmpadv, tmp, u, v, terrain, mean_area=None,
                              tmpadv_contourf_kwargs={'levels': np.arange(-15, 15, 1)}, tmp_contour_kwargs={}, uv_barbs_kwargs={},
                              **pallete_kwargs):

    init_time = pd.to_datetime(tmpadv['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = tmpadv['dtime'].values
    times = tmpadv.stda.fcst_time
    data_name = str(tmpadv['member'].values[0]).upper()
    levels = tmpadv['level'].values

    title = '温度, 温度平流, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_温度_温度平流_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    cenlon = u.lon.mean()
    cenlat = u.lat.mean()
    u = u.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    v = v.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    tmpadv = tmpadv.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    tmp = tmp.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    terrain = terrain.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    tmpadv_contourf(obj.ax, tmpadv, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right'}, transform=None, kwargs=tmpadv_contourf_kwargs)
    barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level', kwargs=tmp_contour_kwargs)
    if terrain.max() > 0:
        cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, terrain.max(), 0.1), zorder=100)
    red_line = lines.Line2D([], [], color='red', label='temperature')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, brown_line], loc=3, title=None, framealpha=1)
    leg.set_zorder(100)
    return obj.save()


def draw_time_wind_vortadv_tmp(vortadv, tmp, u, v, terrain, mean_area=None,
                               vortadv_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},
                               **pallete_kwargs):

    init_time = pd.to_datetime(vortadv['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = vortadv['dtime'].values
    times = vortadv.stda.fcst_time
    # points = {'lon': vortadv['lon'].values, 'lat': vortadv['lat'].values}
    data_name = str(vortadv['member'].values[0]).upper()
    levels = vortadv['level'].values

    title = '温度, 垂直涡度平流, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_温度_垂直涡度平流_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    cenlon = u.lon.mean()
    cenlat = u.lat.mean()
    u = u.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    v = v.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    vortadv = vortadv.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    tmp = tmp.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    terrain = terrain.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    vortadv_contourf(obj.ax, vortadv, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right'}, transform=None, if_mask=False,kwargs=vortadv_contourf_kwargs)
    barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level', kwargs=tmp_contour_kwargs)
    if terrain.max() > 0:
        cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, terrain.max(), 0.1), zorder=100)
    red_line = lines.Line2D([], [], color='red', label='temperature')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, brown_line], loc=3, title=None, framealpha=1)
    leg.set_zorder(100)
    return obj.save()


def draw_time_div_vort_rh_uv(div, vort, rh, u, v, terrain,
                             rh_contourf_kwargs={}, uv_barbs_kwargs={}, div_contour_kwargs={}, vort_contourf_kwargs={},
                             **pallete_kwargs):

    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = rh.stda.fcst_time
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '散度, 垂直涡度, 相对湿度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}'.format(
        init_time, data_name, points['lon'], points['lat'])
    png_name = '{3}_散度_垂直涡度_相对湿度_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_rh_contourf(obj.ax, rh, xdim='fcst_time', ydim='level', levels=np.arange(0, 100, 5), extend='max', kwargs=rh_contourf_kwargs)
    barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    div_contour(obj.ax, div, xdim='fcst_time', ydim='level', colors='red', transform=None, kwargs=div_contour_kwargs)
    vort_contour(obj.ax, vort, xdim='fcst_time', ydim='level', colors='black', transform=None, kwargs=div_contour_kwargs)
    if terrain.max() > 0:
        cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, terrain.max(), 0.1), zorder=100)
    red_line = lines.Line2D([], [], color='red', label='horizontal divergence')
    black_line = lines.Line2D([], [], color='black', label='vertical verticity')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, black_line, brown_line], loc=3, title=None, framealpha=1)
    leg.set_zorder(100)
    return obj.save()


def draw_time_rh_uv_tmp(rh, u, v, tmp, terrain,  rh_contourf_kwargs={}, uv_barbs_kwargs={}, tmp_contour_kwargs={}, **pallete_kwargs):
    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = rh.stda.fcst_time
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '温度, 相对湿度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_温度_相对湿度_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    cenlon = u.lon.mean()
    cenlat = u.lat.mean()
    u = u.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    v = v.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    rh = rh.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    tmp = tmp.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})
    terrain = terrain.mean(dim=('lon', 'lat')).expand_dims({'lon': [cenlon], 'lat': [cenlat]})

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    cross_rh_contourf(obj.ax, rh, xdim='fcst_time', ydim='level', levels=np.arange(0, 101, 0.5), extend='max', kwargs=rh_contourf_kwargs)
    barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level', kwargs=tmp_contour_kwargs)
    if terrain.max() > 0:
        cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, terrain.max(), 0.1), zorder=100)
    return obj.save()
