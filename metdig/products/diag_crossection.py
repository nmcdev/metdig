# -*- coding: utf-8 -*-

import datetime
import numpy as np
import pandas as pd

import matplotlib.lines as lines

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.quiver_method import *
from metdig.graphics.other_method import *
from metdig.graphics.draw_compose import *

def draw_wind_theta_wvfldiv(cross_wvfldiv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                         h_pos=None,
                         wvfldiv_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{0:}]相当位温, 沿剖面水平风和水汽通量散度'.format(data_name,cross_wvfldiv.attrs['var_cn_name'])
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_沿剖面水平风和水汽通量散度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['wvfldiv'] = wvfldiv_contourf(obj.ax, cross_wvfldiv,xdim='index',ydim='level',regrid_shape=None,transform=None, colorbar_kwargs={'pos':'right'},extend='min',
        kwargs=wvfldiv_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index',kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100, kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()


def draw_wind_theta_wvfl(cross_wvfl, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                         h_pos=None,
                         wvfl_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{0:}]相当位温, 沿剖面水平风和水汽通量'.format(data_name,cross_wvfl.attrs['var_cn_name'])
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_沿剖面水平风和水汽通量_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['wvfl'] = contourf_2d(obj.ax, cross_wvfl,xdim='index',ydim='level',regrid_shape=None,transform=None, 
        levels=np.arange(5,46,5),cmap='met/wvfl_ctable',colorbar_kwargs={'pos':'right'},extend='max',
        kwargs=wvfl_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index',kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100, kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_wind_theta_wsp(cross_wsp, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                         h_pos=None,
                         wsp_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{0:}]相当位温, 沿剖面水平风和风速'.format(data_name,cross_wsp.attrs['var_cn_name'])
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_沿剖面水平风和风速_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['wsp'] = contourf_2d(obj.ax, cross_wsp,xdim='index',ydim='level',regrid_shape=None,transform=None, 
        levels=np.arange(12,52,3),cmap='ncl/MPL_YlOrbr',colorbar_kwargs={'pos':'right'},extend='max',
        kwargs=wsp_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index',kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100, kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_wind_theta_fg( cross_u, cross_v, cross_theta, cross_fg, cross_terrain, hgt,
                         st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                         h_pos=None,
                         fg_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]相当位温, 锋生函数, 沿剖面水平风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_锋生函数_沿剖面水平风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['fg'] = cross_fg_contourf(obj.ax, cross_fg, xdim='index',kwargs=fg_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index',kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_wind_theta_w( cross_u, cross_v, cross_theta, cross_w, cross_terrain, hgt,
                         st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                         h_pos=None,
                         w_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]相当位温, 垂直运动速度, 沿剖面水平风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_垂直运动速度_沿剖面水平风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['w'] = cross_w_contourf(obj.ax, cross_w, xdim='index',kwargs=w_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index',kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_wind_theta_div(cross_div, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                       st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                       h_pos=None,
                       div_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                       **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]相当位温, 水平散度, 沿剖面水平风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_水平散度_沿剖面水平风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['div'] = div_contourf(obj.ax, cross_div, xdim='index', ydim='level',levels=np.arange(-10, 10,1),extend='both',
                                  cmap='ncl/BlueWhiteOrangeRed',transform=None,colorbar_kwargs=dict(pos='right',orientation='vertical'),kwargs=div_contourf_kwargs,
                                  )
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index', kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_time_wind_qcld_qsn_tmp(qcld, qsn, tmp, u, v, terrain, mean_area=None,
                                 qcld_contour_kwargs={},qice_contour_kwargs={}, tmp_contourf_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                                 **pallete_kwargs):

    init_time = pd.to_datetime(qcld['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = qcld['dtime'].values
    times = pallete_kwargs.pop('times', qcld.stda.fcst_time)
    data_name = str(qcld['member'].values[0]).upper()
    levels = qcld['level'].values

    title = '云水比, 雪水比, 温度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_云水比_雪水比_水平风_温度_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['qcld'] = qcld_contourf(obj.ax, qcld, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right top'}, transform=None, kwargs=qcld_contour_kwargs)
    obj.img['qsn'] = qsn_contourf(obj.ax, qsn, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right bottom'}, transform=None, kwargs=qice_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level',kwargs=tmp_contourf_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    red_line = lines.Line2D([], [], color='#0A1F5D', label='temperature')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, brown_line], loc='upper left', title=None, framealpha=1)
    leg.set_zorder(100)
    obj.save()
    return obj.get_mpl()

def draw_time_wind_qcld_qice_tmp(qcld, qice, tmp, u, v, terrain, mean_area=None,
                                 qcld_contour_kwargs={},qice_contour_kwargs={}, tmp_contourf_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                                 **pallete_kwargs):

    init_time = pd.to_datetime(qcld['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = qcld['dtime'].values
    times = pallete_kwargs.pop('times', qcld.stda.fcst_time)
    data_name = str(qcld['member'].values[0]).upper()
    levels = qcld['level'].values

    title = '云水比, 冰水比, 温度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_云水比_冰水比_水平风_温度_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['qcld'] = qcld_contourf(obj.ax, qcld, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right top'}, transform=None, kwargs=qcld_contour_kwargs)
    obj.img['qice'] = qice_contourf(obj.ax, qice, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right bottom'}, transform=None, kwargs=qice_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level',kwargs=tmp_contourf_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    red_line = lines.Line2D([], [], color='#0A1F5D', label='temperature')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, brown_line], loc='upper left', title=None, framealpha=1)
    leg.set_zorder(100)
    obj.save()
    return obj.get_mpl()


def draw_wind_w_tmpadv_tmp(cross_tmpadv, cross_tmp, cross_t, cross_w, cross_terrain, hgt,
                           st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                           h_pos=None,
                           tmpadv_contourf_kwargs={}, tmp_contour_kwargs={}, wind_quiver_kwargs={},terrain_contourf_kwargs={},
                           **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_tmpadv['level'].values
    index = cross_tmpadv['index'].values
    lon_cross = cross_tmpadv['lon_cross'].values
    lat_cross = cross_tmpadv['lat_cross'].values

    title = '[{}]温度, 温度平流, 沿剖垂直环流'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_温度_温度平流_沿剖垂直环流_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_t = cross_t.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_w = cross_w.isel(lon=wind_slc_horz, level=wind_slc_vert)
    ratio = np.nanmax(np.abs(cross_t.values))/np.nanmax(np.abs(cross_w.values))
    cross_w = cross_w*ratio

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['tmpadv'] = tmpadv_contourf(obj.ax, cross_tmpadv, xdim='index', ydim='level', transform=None, colorbar_kwargs={'pos': 'right'}, kwargs=tmpadv_contourf_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, cross_tmp, xdim='index', kwargs=tmp_contour_kwargs)
    obj.img['w'] = uv_quiver(obj.ax, cross_t, cross_w, xdim='index', ydim='level', color='k', scale=800, transform=None, regrid_shape=None, kwargs=wind_quiver_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()


def draw_wind_tmpadv_tmp(cross_tmpadv, cross_tmp, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                         h_pos=None,
                         tmpadv_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]温度, 温度平流, 沿剖面水平风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_温度_温度平流_沿剖面水平风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['tmpadv'] = tmpadv_contourf(obj.ax, cross_tmpadv, xdim='index', ydim='level', transform=None, colorbar_kwargs={'pos': 'right'}, kwargs=tmpadv_contourf_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, cross_tmp,xdim='index', kwargs=tmp_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()


def draw_wind_vortadv_tmp(cross_vortadv, cross_tmp, cross_u, cross_v, cross_terrain, hgt,
                          st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                          h_pos=None,
                          vortadv_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                          **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]温度, 垂直涡度平流, 沿剖面水平风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_温度_垂直涡度平流_沿剖面水平风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['vortadv'] = vortadv_contourf(obj.ax, cross_vortadv, xdim='index', ydim='level', transform=None,if_mask=False, colorbar_kwargs={'pos': 'right'}, kwargs=vortadv_contourf_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, cross_tmp, xdim='index', kwargs=tmp_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_wind_thetaes_mpvg(cross_mpvg, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                        st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                        h_pos=None,
                        mpv_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]饱和相当位温, 准地转湿位涡, 沿剖面准地转风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_饱和相当位温_准地转湿位涡_沿剖面准地转风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['mpvg'] = cross_mpv_contourf(obj.ax, cross_mpvg, xdim='index',levels=np.arange(-20, 21, 1),kwargs=mpv_contourf_kwargs)
    obj.img['thetaes'] = cross_theta_contour(obj.ax, cross_theta, xdim='index',kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_wind_theta_mpv(cross_mpv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                        st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                        h_pos=None,
                        mpv_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                        **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]相当位温, 湿位涡, 沿剖面水平风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_湿位涡_沿剖面水平风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['mpv'] = cross_mpv_contourf(obj.ax, cross_mpv, xdim='index', kwargs=mpv_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index', kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()


def draw_wind_theta_absv(cross_absv, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                         h_pos=None,
                         absv_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{0:}]相当位温, {1:}, 沿剖面水平风'.format(data_name,cross_absv.attrs['var_cn_name'])
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_{3:}_沿剖面水平风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name,cross_absv.attrs['var_cn_name'])

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['absv'] = cross_absv_contourf(obj.ax, cross_absv, xdim='index',kwargs=absv_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index',kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100, kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()


def draw_wind_theta_rh(cross_rh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                       st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                       h_pos=None,
                       rh_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                       **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]相当位温, 相对湿度, 沿剖面水平风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_相对湿度_沿剖面水平风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['rh'] = cross_rh_contourf(obj.ax, cross_rh, xdim='index', levels=np.arange(0, 106, 5), kwargs=rh_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index', kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_wind_w_theta_spfh(cross_spfh, cross_theta, cross_t, cross_w, cross_terrain, hgt,
                         st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                         h_pos=None,
                         spfh_contourf_kwargs={}, theta_contour_kwargs={}, wind_quiver_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_spfh['level'].values
    index = cross_spfh['index'].values
    lon_cross = cross_spfh['lon_cross'].values
    lat_cross = cross_spfh['lat_cross'].values

    title = '[{}]相当位温, 绝对湿度, 沿剖面垂直环流'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_绝对湿度_沿剖面垂直环流_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_t = cross_t.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_w = cross_w.isel(lon=wind_slc_horz, level=wind_slc_vert)
    ratio = np.nanmax(np.abs(cross_t.values))/np.nanmax(np.abs(cross_w.values))
    cross_w = cross_w*ratio

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['spfh'] = cross_spfh_contourf(obj.ax, cross_spfh, xdim='index', levels=np.arange(0, 20, 2), cmap='YlGnBu', kwargs=spfh_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index', kwargs=theta_contour_kwargs)
    # barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['w'] = uv_quiver(obj.ax, cross_t, cross_w, xdim='index', ydim='level', color='k', scale=800, transform=None, regrid_shape=None, kwargs=wind_quiver_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_wind_theta_spfh(cross_spfh, cross_theta, cross_u, cross_v, cross_terrain, hgt,
                         st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                         h_pos=None,
                         spfh_contourf_kwargs={}, theta_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                         **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]相当位温, 绝对湿度, 沿剖面水平风'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_绝对湿度_沿剖面水平风_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['spfh'] = cross_spfh_contourf(obj.ax, cross_spfh, xdim='index',levels=np.arange(0, 20, 2), cmap='YlGnBu', kwargs=spfh_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index',kwargs=theta_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()


def draw_wind_tmp_rh_vvel(cross_rh, cross_tmp, cross_u, cross_v, cross_vvel, cross_terrain, hgt,
                     st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                     h_pos=None,
                     rh_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},vvel_contour_kwargs={},terrain_contourf_kwargs={},
                     **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]温度 相对湿度 沿剖面水平风 气压垂直运动速度'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_温度_相对湿度_沿剖面水平风_气压垂直运动速度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)

    obj.img['rh'] = cross_rh_contourf(obj.ax, cross_rh, levels=np.arange(0, 101, 0.5), xdim='index', kwargs=rh_contourf_kwargs)
    obj.img['vvel'] = cross_vvel_contour(obj.ax, cross_vvel, zorder=1,xdim='index', kwargs=vvel_contour_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, cross_tmp, xdim='index', kwargs=tmp_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7,zorder=2, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()


def draw_wind_w_theta_spfh_vvel(cross_spfh, cross_theta, cross_t, cross_w, cross_vvel, cross_terrain, hgt,
                           st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                           h_pos=None,
                           spfh_contour_kwargs={}, theta_contourf_kwargs={}, wind_quiver_kwargs={}, vvel_contour_kwargs={}, terrain_contourf_kwargs={},
                           **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_spfh['level'].values
    index = cross_spfh['index'].values
    lon_cross = cross_spfh['lon_cross'].values
    lat_cross = cross_spfh['lat_cross'].values

    title = '[{}]相当位温, 绝对湿度, 沿剖面垂直环流，气压垂直运动速度'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_相当位温_绝对湿度_沿剖面垂直环流_气压垂直运动速度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_t = cross_t.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_w = cross_w.isel(lon=wind_slc_horz, level=wind_slc_vert)
    ratio = np.nanmax(np.abs(cross_t.values))/np.nanmax(np.abs(cross_w.values))
    cross_w = cross_w*ratio

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)

    obj.img['spfh'] = cross_spfh_contour(obj.ax, cross_spfh, xdim='index', kwargs=spfh_contour_kwargs)
    obj.img['theta'] = cross_theta_contourf(obj.ax, cross_theta, xdim='index', kwargs=theta_contourf_kwargs)
    obj.img['w'] = uv_quiver(obj.ax, cross_t, cross_w, xdim='index', ydim='level', color='k', scale=800, transform=None, regrid_shape=None, kwargs=wind_quiver_kwargs)
    obj.img['vvel'] = cross_vvel_contour(obj.ax, cross_vvel, xdim='index', cmap='black',linewidths=2,levels=np.arange(-10,10,0.5), kwargs=vvel_contour_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()




def draw_time_rh_uv_theta(rh, u, v, theta, terrain,rh_contourf_kwargs={}, uv_barbs_kwargs={}, theta_contour_kwargs={},terrain_contourf_kwargs={}, **pallete_kwargs):
    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = pallete_kwargs.pop('times', rh.stda.fcst_time)
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '相当位温, 相对湿度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}'.format(
        init_time, data_name, points['lon'], points['lat'])
    png_name = '{3}_相当位温_相对湿度_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['rh'] = cross_rh_contourf(obj.ax, rh, xdim='fcst_time', ydim='level', levels=np.arange(0, 100.5, 5), extend='max', kwargs=rh_contourf_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, theta, xdim='fcst_time', ydim='level', levels=np.arange(250, 450, 5), colors='#A0522D', kwargs=theta_contour_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_time_div_vort_spfh_uv(div, vort, spfh, u, v, terrain,
                               spfh_contourf_kwargs={}, uv_barbs_kwargs={}, div_contour_kwargs={}, vort_contourf_kwargs={},
                               **pallete_kwargs):

    init_time = pd.to_datetime(spfh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = spfh['dtime'].values
    times = pallete_kwargs.pop('times', spfh.stda.fcst_time)
    points = {'lon': spfh['lon'].values, 'lat': spfh['lat'].values}
    data_name = str(spfh['member'].values[0]).upper()
    levels = spfh['level'].values

    title = '散度, 垂直涡度, 比湿, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}'.format(
        init_time, data_name, points['lon'], points['lat'])
    png_name = '{3}_散度_垂直涡度_比湿_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['spfh'] = cross_spfh_contourf(obj.ax, spfh, xdim='fcst_time', ydim='level', extend='max', kwargs=spfh_contourf_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['div'] = div_contour(obj.ax, div, xdim='fcst_time', ydim='level', colors='red', transform=None, kwargs=div_contour_kwargs)
    obj.img['vort'] = vort_contour(obj.ax, vort, xdim='fcst_time', ydim='level', colors='black', transform=None, kwargs=div_contour_kwargs)
    cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=100)
    red_line = lines.Line2D([], [], color='red', label='horizontal divergence')
    black_line = lines.Line2D([], [], color='black', label='vertical vorticity')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, black_line, brown_line], loc='upper left', title=None, framealpha=1)
    leg.set_zorder(100)
    obj.save()
    return obj.get_mpl()


def draw_time_wind_tmpadv_tmp(tmpadv, tmp, u, v, terrain, mean_area=None,
                              tmpadv_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},
                              **pallete_kwargs):

    init_time = pd.to_datetime(tmpadv['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = tmpadv['dtime'].values
    times = pallete_kwargs.pop('times', tmpadv.stda.fcst_time)
    data_name = str(tmpadv['member'].values[0]).upper()
    levels = tmpadv['level'].values

    title = '温度, 温度平流, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_温度_温度平流_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['tmpadv'] = tmpadv_contourf(obj.ax, tmpadv, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right'}, transform=None, kwargs=tmpadv_contourf_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level', kwargs=tmp_contour_kwargs)
    cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=100)
    red_line = lines.Line2D([], [], color='black', label='temperature')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, brown_line], loc='upper left', title=None, framealpha=1)
    leg.set_zorder(100)
    obj.save()
    return obj.get_mpl()


def draw_time_wind_vortadv_tmp(vortadv, tmp, u, v, terrain, mean_area=None,
                               vortadv_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},
                               **pallete_kwargs):

    init_time = pd.to_datetime(vortadv['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = vortadv['dtime'].values
    times = pallete_kwargs.pop('times', vortadv.stda.fcst_time)
    # points = {'lon': vortadv['lon'].values, 'lat': vortadv['lat'].values}
    data_name = str(vortadv['member'].values[0]).upper()
    levels = vortadv['level'].values

    title = '温度, 垂直涡度平流, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_温度_垂直涡度平流_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['vortadv'] = vortadv_contourf(obj.ax, vortadv, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right'}, transform=None, if_mask=False,kwargs=vortadv_contourf_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level', kwargs=tmp_contour_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=100)
    red_line = lines.Line2D([], [], color='red', label='temperature')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, brown_line], loc='upper left', title=None, framealpha=1)
    leg.set_zorder(100)
    obj.save()
    return obj.get_mpl()

def draw_time_wind_theta_mpv(theta, mpv, u, v, terrain, mean_area=None,
                             theta_contour_kwargs={}, mpv_contour_kwargs={}, uv_barbs_kwargs={},
                             **pallete_kwargs):

    init_time = pd.to_datetime(theta['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = theta['dtime'].values
    times = pallete_kwargs.pop('times', theta.stda.fcst_time)
    # points = {'lon': theta['lon'].values, 'lat': theta['lat'].values}
    data_name = str(theta['member'].values[0]).upper()
    levels = theta['level'].values

    title = '相当位温, 湿位涡, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_相当位温_湿位涡_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['mpv'] = mpv_contourf(obj.ax, mpv, xdim='fcst_time', ydim='level', colorbar_kwargs={'pos': 'right'}, transform=None,kwargs=mpv_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, theta, xdim='fcst_time', ydim='level', kwargs=theta_contour_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=100)
    obj.save()
    return obj.get_mpl()


def draw_time_wind_thetaes_mpvg(thetaes, mpvg, u, v, terrain, mean_area=None,
                             theta_contour_kwargs={}, mpv_contour_kwargs={}, uv_barbs_kwargs={},
                             **pallete_kwargs):

    init_time = pd.to_datetime(thetaes['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = thetaes['dtime'].values
    times = pallete_kwargs.pop('times', thetaes.stda.fcst_time)
    # points = {'lon': thetaes['lon'].values, 'lat': thetaes['lat'].values}
    data_name = str(thetaes['member'].values[0]).upper()
    levels = thetaes['level'].values

    title = '饱和相当位温, 准地转湿位涡, 准地转风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n平均区域:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_饱和相当位温_准地转湿位涡_准地转风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['mpvg'] = mpv_contourf(obj.ax, mpvg, xdim='fcst_time', ydim='level', levels=np.arange(-20, 21, 1), colorbar_kwargs={'pos': 'right'}, transform=None, kwargs=mpv_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['thetaes'] = cross_theta_contour(obj.ax, thetaes, xdim='fcst_time', ydim='level', kwargs=theta_contour_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=100)
    obj.save()
    return obj.get_mpl()


def draw_time_div_vort_rh_uv(div, vort, rh, u, v, terrain,
                             rh_contourf_kwargs={}, uv_barbs_kwargs={}, div_contour_kwargs={}, vort_contour_kwargs={},terrain_contourf_kwargs={},
                             **pallete_kwargs):

    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = pallete_kwargs.pop('times', rh.stda.fcst_time)
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '散度, 垂直涡度, 相对湿度, 水平风'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}, {3}'.format(
        init_time, data_name, points['lon'], points['lat'])
    png_name = '{3}_散度_垂直涡度_相对湿度_水平风_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times=times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['rh'] = cross_rh_contourf(obj.ax, rh, xdim='fcst_time', ydim='level', levels=np.arange(0, 100, 5), extend='max', kwargs=rh_contourf_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['div'] = div_contour(obj.ax, div, xdim='fcst_time', ydim='level', colors='red', transform=None, kwargs=div_contour_kwargs)
    obj.img['vort'] = vort_contour(obj.ax, vort, xdim='fcst_time', ydim='level', colors='black', transform=None, kwargs=vort_contour_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    red_line = lines.Line2D([], [], color='red', label='horizontal divergence')
    black_line = lines.Line2D([], [], color='black', label='vertical verticity')
    brown_line = lines.Line2D([], [], color='brown', label='terrain')
    leg = obj.ax.legend(handles=[red_line, black_line, brown_line], loc='upper left', title=None, framealpha=1)
    leg.set_zorder(100)
    obj.save()
    return obj.get_mpl()


def draw_time_rh_uv_tmp_vvel(rh, u, v, tmp, vvel, terrain,  rh_contourf_kwargs={}, uv_barbs_kwargs={}, tmp_contour_kwargs={}, vvel_contour_kwargs={},
            terrain_contourf_kwargs={}, **pallete_kwargs):
    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = pallete_kwargs.pop('times', rh.stda.fcst_time)
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '温度 相对湿度 水平风 气压垂直速度'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_温度_相对湿度_水平风_气压垂直速度_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['rh'] = cross_rh_contourf(obj.ax, rh, xdim='fcst_time', ydim='level', levels=np.arange(0, 101, 0.5), extend='max', kwargs=rh_contourf_kwargs)
    obj.img['vvel'] = cross_vvel_contour(obj.ax, vvel, xdim='fcst_time', ydim='level',linewidths=2,kwargs=vvel_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level',  kwargs=tmp_contour_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=20,kwargs=terrain_contourf_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_time_rh_uv_tmp_vvel_rain(rh, u, v, tmp, vvel, rain, terrain,  rh_contourf_kwargs={}, uv_barbs_kwargs={}, tmp_contour_kwargs={}, vvel_contour_kwargs={},
            terrain_contourf_kwargs={}, rain_kwargs={},
            **pallete_kwargs):
    init_time = pd.to_datetime(rh['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhours = rh['dtime'].values
    times = pallete_kwargs.pop('times', rh.stda.fcst_time)
    points = {'lon': rh['lon'].values, 'lat': rh['lat'].values}
    data_name = str(rh['member'].values[0]).upper()
    levels = rh['level'].values

    title = '温度 相对湿度 水平风 气压垂直速度'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]模式时间剖面\n预报点:{2}'.format(
        init_time, data_name, '('+','.join([str(u.lon.min().values), str(u.lon.max().values), str(u.lat.min().values), str(u.lat.max().values)])+')')
    png_name = '{3}_温度_相对湿度_水平风_气压垂直速度_时间剖面产品_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_预报时效_{1:03d}_至_{2:03d}.png'.format(
        init_time, fhours[0], fhours[-1], data_name)

    obj = cross_timepres_compose(levels, times, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['rh'] = cross_rh_contourf(obj.ax, rh, xdim='fcst_time', ydim='level', levels=np.arange(0, 101, 0.5), extend='max', kwargs=rh_contourf_kwargs)
    obj.img['vvel'] = cross_vvel_contour(obj.ax, vvel, xdim='fcst_time', ydim='level',linewidths=2,kwargs=vvel_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, u, v, xdim='fcst_time', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, tmp, xdim='fcst_time', ydim='level',  kwargs=tmp_contour_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, terrain, xdim='fcst_time', ydim='level', levels=np.arange(0, 500, 1), zorder=20,kwargs=terrain_contourf_kwargs)
    obj.img['rain'] = cross_section_rain(obj.ax, rain, times, kwargs=rain_kwargs)
    obj.save()
    return obj.get_mpl()