# -*- coding: utf-8 -*-
'''
@author:谭正华
'''

import os
import datetime
import numpy as np
import pandas as pd

from metdig.graphics.barbs_method import *
from metdig.graphics.contour_method import *
from metdig.graphics.contourf_method import *
from metdig.graphics.pcolormesh_method import *
from metdig.graphics.text_method import *
from metdig.graphics.draw_compose import *
from metdig.graphics.quiver_method import *
from metdig.graphics.other_method import *

import meteva.base as meb
import metdig.graphics.lib.utl_plotmap as utl_plotmap

def draw_prmsl_dprmsl24(prmsl, dprmsl24, map_extent=(60, 145, 15, 55),
                      dprmsl24_contourf_kwargs={}, prmsl_contour_kwargs={},
                      **pallete_kwargs):
    init_time = pd.to_datetime(prmsl.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(prmsl['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(prmsl['member'].values[0])
    forcast_info = prmsl.stda.description()
    title = '[{}] 海平面气压（黑线），24小时变压（填色）'.format(data_name.upper())
    png_name = '{2}_海平面气压_24小时变压_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.jpg'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['dprmsl24'] = contourf_2d(obj.ax, dprmsl24, levels=np.arange(-26,26,2), cb_ticks =np.arange(-26,26,2), cmap='PiYG', extend='neither', kwargs=dprmsl24_contourf_kwargs)
    obj.img['prmsl'] = prmsl_contour(obj.ax, prmsl, levels=np.arange(900,1040,2.5), kwargs=prmsl_contour_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_hgt_ana_fcst_bias(hgt_a, hgt_f, hgt_b, map_extent=(60, 145, 15, 55),
                      hgt_a_contour_kwargs={}, hgt_f_contour_kwargs={}, hgt_b_contourf_kwargs={},
                      **pallete_kwargs):
    init_time = pd.to_datetime(hgt_a.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt_a['dtime'].values[0])
    fhour0 = int(hgt_f['dtime'].values[0])

    data_name = str(hgt_a['member'].values[0])
    forcast_info = hgt_a.stda.description()
    title = '[{}] {}hPa 位势高度场 当前时次分析场（实线），{}小时前预报（虚线）、预报偏差（填色）'.format(data_name.upper(),hgt_a['level'].values[0],fhour0)
    png_name = '{2}_位势高度场_预报检验_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.jpg'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['hgt_b'] = contourf_2d(obj.ax, hgt_b, cmap='PiYG',levels=np.arange(-4,4.5,0.5), cb_ticks=np.arange(-4,4.5,0.5), extend='neither',kwags=hgt_b_contourf_kwargs)
    obj.img['hgt_a'] = contour_2d(obj.ax, hgt_a, levels=np.arange(0,1000,2),linewidths=1,cb_fontsize=15,kwargs=hgt_a_contour_kwargs)
    obj.img['hgt_f'] = contour_2d(obj.ax, hgt_f, levels=np.arange(0,1000,2),linewidths=1,linestyles='dotted',colors='red',cb_colors='red',cb_fontsize=15,linewidthsfloat=0.8,kwargs=hgt_f_contour_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_wsp_ana_fcst_bias(u_a, v_a, u_f, v_f, wsp_a, wsp_f, wsp_b, map_extent=(60, 145, 15, 55),
                      uv_a_brabs_kwargs={}, uv_f_brabs_kwargs={},
                      wsp_a_contour_kwargs={}, wsp_f_contour_kwargs={}, 
                      wsp_b_contourf_kwargs={}, **pallete_kwargs):
    init_time = pd.to_datetime(u_a.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u_a['dtime'].values[0])
    fhour0 = int(u_f['dtime'].values[0])

    data_name = str(u_a['member'].values[0])
    forcast_info = u_a.stda.description()
    title = '[{}] {}hPa 风场 当前时次分析场（黑色），{}小时前预报（红色）、风速预报偏差（填色）'.format(data_name.upper(),u_a['level'].values[0],fhour0)
    png_name = '{2}_风场_预报检验_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.jpg'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['wsp_b'] = wsp_contourf(obj.ax, wsp_b, cmap='PiYG',levels=np.arange(-4,4.5,0.5), 
                                       colorbar_kwargs={'label':'{}小时风速预报偏差(m/s)'.format(fhour0)}, kwargs=wsp_b_contourf_kwargs)
    obj.img['wsp_a'] = contour_2d(obj.ax, wsp_a, colors='black',cb_colors='black',levels=[12],linewidths=1,cb_fontsize=15, kwargs=wsp_a_contour_kwargs)
    obj.img['wsp_f'] = contour_2d(obj.ax, wsp_f, colors='red',cb_colors='red',levels=[12],linewidths=1,cb_fontsize=15, kwargs=wsp_f_contour_kwargs)
    obj.img['uv_a'] = uv_barbs(obj.ax, u_a, v_a, color='black', kwargs=uv_a_brabs_kwargs)
    obj.img['uv_f'] = uv_barbs(obj.ax, u_f, v_f, color='red', kwargs=uv_f_brabs_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_prmsl_ana_fcst_bias(prmsl_a, prmsl_f, prmsl_b, map_extent=(60, 145, 15, 55),
                      prmsl_a_contour_kwargs={}, prmsl_f_contour_kwargs={}, prmsl_b_contourf_kwargs={},
                      **pallete_kwargs):
    init_time = pd.to_datetime(prmsl_a.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(prmsl_a['dtime'].values[0])
    fhour0 = int(prmsl_f['dtime'].values[0])

    data_name = str(prmsl_a['member'].values[0])
    forcast_info = prmsl_a.stda.description()
    title = '[{}] 海平面气压场 当前时次分析场（实线），{}小时前预报（虚线）、预报偏差（填色）'.format(data_name.upper(),fhour0)
    png_name = '{2}_海平面气压场_预报检验_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.jpg'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['prmsl_b'] = prmsl_contourf(obj.ax, prmsl_b, cmap='PiYG',levels=np.arange(-4,4.5,0.5), 
                                      colorbar_kwargs={'label':'{}小时预报偏差(hPa)'.format(fhour0)},kwags=prmsl_b_contourf_kwargs)
    obj.img['prmsl_a'] = prmsl_contour(obj.ax, prmsl_a, levels=np.arange(600,1800,2.5),kwargs=prmsl_a_contour_kwargs)
    obj.img['prmsl_f'] = prmsl_contour(obj.ax, prmsl_f, levels=np.arange(600,1800,2.5),linestyles='dotted',colors='red',linewidthsfloat=0.8,kwargs=prmsl_f_contour_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_hgt_ivt(hgt, ivtu, ivtv, ivt, map_extent=(60, 145, 15, 55),
                     ivt_pcolormesh_kwargs={}, ivtuv_quiver_kwargs={}, hgt_contour_kwargs={},
                     **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(hgt['member'].values[0])
    title = '[{}] {}hPa 位势高度, {}hPa 水汽通量'.format(data_name.upper(), hgt['level'].values[0], ivt['level'].values[0])

    forcast_info = hgt.stda.description()
    png_name = '{2}_位势高度场_风场_水汽通量_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['ivt'] = wvfl_pcolormesh(obj.ax, ivt, kwargs=ivt_pcolormesh_kwargs)
    obj.img['ivtuv'] = uv_quiver(obj.ax, ivtu, ivtv, kwargs=ivtuv_quiver_kwargs)
    obj.img['hgt'] = hgt_contour(obj.ax, hgt, kwargs=hgt_contour_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_wvfldiv_tcwv(wvfldiv, tcwv, map_extent=(60, 145, 15, 55),
                     tcwv_pcolormesh_kwargs={}, wvfldiv_contour_kwargs={},
                     **pallete_kwargs):
    init_time = pd.to_datetime(wvfldiv.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(wvfldiv['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(wvfldiv['member'].values[0])
    title = '[{}] {}hPa 水汽通量散度（等值线）,  整层可降水量（填色）'.format(data_name.upper(), wvfldiv['level'].values[0])

    forcast_info = wvfldiv.stda.description()
    png_name = '{2}_水汽通量散度_整层可降水量_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['tcwv'] = tcwv_pcolormesh(obj.ax, tcwv, levels=np.arange(30,80,5), kwargs=tcwv_pcolormesh_kwargs)
    obj.img['wvfldiv'] = contour_2d(obj.ax, wvfldiv, levels=np.arange(-100,0,3), colors='blue', linewidths=1.7, kwargs=wvfldiv_contour_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_div_tcwv(div, tcwv, map_extent=(60, 145, 15, 55),
                     tcwv_pcolormesh_kwargs={}, div_contour_kwargs={},
                     **pallete_kwargs):
    init_time = pd.to_datetime(div.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(div['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    data_name = str(div['member'].values[0])
    title = '[{}] {}hPa 散度（等值线）,  整层可降水量（填色）'.format(data_name.upper(), div['level'].values[0])

    forcast_info = div.stda.description()
    png_name = '{2}_散度_整层可降水量_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['tcwv'] = tcwv_pcolormesh(obj.ax, tcwv, levels=np.arange(30,80,5), kwargs=tcwv_pcolormesh_kwargs)
    obj.img['div'] = contour_2d(obj.ax, div*1e5, levels=np.arange(-100,0,3), colors='blue', linewidths=1.7, cb_colors='black',kwargs=div_contour_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_wsp_uv_div(wsp, u, v, div, map_extent=(60, 145, 15, 55),
                    div_contourf_kwargs={}, uv_barbs_kwargs={}, wsp_contour_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(wsp.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(wsp['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(wsp['member'].values[0])

    title = '[{}] {}hPa风,水平散度'.format(data_name.upper(),u['level'].values[0])

    forcast_info = wsp.stda.description()
    png_name = '{2}_风场_水平散度_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['div'] = div_contourf(obj.ax, div, levels=np.arange(-10, 10, 1), cmap='guide/cs1', extend='both', kwargs=div_contourf_kwargs)
    obj.img['uv'] = uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    obj.img['wsp'] = contour_2d(obj.ax, wsp, levels=np.arange(12,40,2), linewidths=1.7, kwargs=wsp_contour_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_uv_fg_thta(u, v, fg, thta, map_extent=(60, 145, 15, 55),
                    thta_contour_kwargs={}, uv_barbs_kwargs={}, fg_pcolormesh_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(u.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(u['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(u['member'].values[0])

    title = '[{}] {}hPa 锋生函数, 风场，假相当位温'.format(data_name.upper(), u['level'].values[0], u['level'].values[0])
    
    forcast_info = u.stda.description()
    png_name = '{2}_锋生函数_风场_假相当位温_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())
    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['fg'] = fg_pcolormesh(obj.ax, fg, kwargs=fg_pcolormesh_kwargs)
    obj.img['uv'] = uv_barbs(obj.ax, u, v, kwargs=uv_barbs_kwargs)
    obj.img['thta'] = contour_2d(obj.ax, thta, levels=range(0,1000,4), colors='black', kwargs=thta_contour_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_K_idx(T850, K_idx, map_extent=(60, 145, 15, 55), K_pcolormesh_kwargs={}, **pallete_kwargs):
    init_time = pd.to_datetime(T850.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(T850['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(T850['member'].values[0])

    title = '[{}] K指数'.format(data_name.upper())
    forcast_info = T850.stda.description()
    png_name = '{2}_K指数_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['k_idx'] = K_idx_pcolormesh(obj.ax, K_idx, kwargs=K_pcolormesh_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_cape(cape, map_extent=(60, 145, 15, 55), cape_pcolormesh_kwargs={}, **pallete_kwargs):
    init_time = pd.to_datetime(cape.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(cape['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(cape['member'].values[0])

    title = '[{}] 对流有效位能'.format(data_name.upper())
    forcast_info = cape.stda.description()
    png_name = '{2}_对流有效位能_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['cape'] = cape_pcolormesh(obj.ax, cape, levels=np.arange(100, 1500, 100), cmap='guide/cs2', kwargs=cape_pcolormesh_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_cross_theta_fg_mpv(cross_theta, cross_fg, cross_mpv, cross_terrain, hgt,
                      st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                      h_pos=None,
                      mpv_contourf_kwargs={}, fg_contourf_kwargs={}, theta_contour_kwargs={}, terrain_contourf_kwargs={},
                      **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_fg['level'].values
    index = cross_fg['index'].values
    lon_cross = cross_fg['lon_cross'].values
    lat_cross = cross_fg['lat_cross'].values

    title = '[{}]锋生函数(蓝线), 相当位温(红线)，湿位涡(填色)'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_锋生函数_相当位温_湿位涡_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['fg'] = cross_fg_contour(obj.ax, cross_fg, xdim='index', kwargs=fg_contourf_kwargs)
    obj.img['mpv'] = cross_mpv_contourf(obj.ax, cross_mpv, xdim='index', levels=np.arange(-3,3,0.2), cmap='guide/cs4', kwargs=mpv_contourf_kwargs)
    obj.img['theta'] = cross_theta_contour(obj.ax, cross_theta, xdim='index', levels=np.arange(1,1000,4), colors='red', kwargs=theta_contour_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index',levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_cross_div_uv_wsp(cross_div, cross_wsp, cross_u, cross_v, cross_terrain, prmsl,
                    st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                    h_pos=None,
                    div_contourf_kwargs={}, wsp_contour_kwargs={}, uv_barbs_kwargs={},terrain_contourf_kwargs={},
                    **pallete_kwargs):
    init_time = pd.to_datetime(prmsl.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(prmsl['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(prmsl['member'].values[0]).upper()
    levels = cross_u['level'].values
    index = cross_u['index'].values
    lon_cross = cross_u['lon_cross'].values
    lat_cross = cross_u['lat_cross'].values

    title = '[{}]水平散度（填色），水平风，风速（蓝线）'.format(data_name)
    forcast_info = prmsl.stda.description()
    png_name = '{2}_水平散度_水平风_风速_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_u = cross_u.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_v = cross_v.isel(lon=wind_slc_horz, level=wind_slc_vert)

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['cross_div'] = cross_div_contourf(obj.ax, cross_div, xdim='index', kwargs=div_contourf_kwargs)
    obj.img['cross_wsp'] = cross_wsp_contour(obj.ax, cross_wsp, xdim='index', kwargs=wsp_contour_kwargs)
    obj.img['uv'] = barbs_2d(obj.ax, cross_u, cross_v, xdim='index', ydim='level', color='k', length=7, transform=None, regrid_shape=None, kwargs=uv_barbs_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['prmsl'] = cross_section_prmsl(obj.ax, prmsl, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_cross_wind_w_tmp_vvel_tmpadv(cross_tmpadv, cross_tmp, cross_t, cross_w, cross_vvel, cross_terrain, hgt,
                           st_point=None, ed_point=None, map_extent=(50, 150, 0, 65),
                           h_pos=None,
                           tmpadv_contourf_kwargs={}, tmp_contour_kwargs={}, vvel_contour_kwargs={}, wind_quiver_kwargs={}, terrain_contourf_kwargs={},
                           **pallete_kwargs):
    init_time = pd.to_datetime(hgt.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)
    data_name = str(hgt['member'].values[0]).upper()
    levels = cross_tmpadv['level'].values
    index = cross_tmpadv['index'].values
    lon_cross = cross_tmpadv['lon_cross'].values
    lat_cross = cross_tmpadv['lat_cross'].values

    title = '[{}]温度（红线，℃）, 垂直速度（蓝线，Pa/s），温度平流（填色）, 沿剖垂直环流'.format(data_name)
    forcast_info = hgt.stda.description()
    png_name = '{2}_温度_垂直速度_温度平流_沿剖垂直环流_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, len(index), len(index) // 40)
    cross_t = cross_t.isel(lon=wind_slc_horz, level=wind_slc_vert)
    cross_w = cross_w.isel(lon=wind_slc_horz, level=wind_slc_vert)
    ratio = np.nanmax(np.abs(cross_t.values))/np.nanmax(np.abs(cross_w.values))
    cross_w = cross_w*ratio

    obj = cross_lonpres_compose(levels, index=index, lon_cross=lon_cross, lat_cross=lat_cross, st_point=st_point, ed_point=ed_point, title=title, description=forcast_info, png_name=png_name, kwargs=pallete_kwargs)
    obj.img['tmpadv'] = tmpadv_contourf(obj.ax, cross_tmpadv, xdim='index', ydim='level', levels=np.arange(-5, 5, 0.5), transform=None, colorbar_kwargs={'pos': 'right'}, kwargs=tmpadv_contourf_kwargs)
    obj.img['tmp'] = cross_tmp_contour(obj.ax, cross_tmp, xdim='index', colors='red', kwargs=tmp_contour_kwargs)
    obj.img['vvel'] = cross_vvel_contour(obj.ax, cross_vvel, xdim='index', cmap='blue',levels=np.arange(-10,0,0.2).tolist(),kwargs=vvel_contour_kwargs)
    obj.img['w'] = uv_quiver(obj.ax, cross_t, cross_w, xdim='index', ydim='level', color='k', scale=800, transform=None, regrid_shape=None, kwargs=wind_quiver_kwargs)
    obj.img['terrain'] = cross_terrain_contourf(obj.ax, cross_terrain, xdim='index', levels=np.arange(0, 500, 1), zorder=100,kwargs=terrain_contourf_kwargs)
    obj.img['hgt'] = cross_section_hgt(obj.ax, hgt, st_point=st_point, ed_point=ed_point, lon_cross=lon_cross, lat_cross=lat_cross, map_extent=map_extent, h_pos=h_pos)
    obj.save()
    return obj.get_mpl()

def draw_hgt_fcst_change(hgt_f, hgt_fp, hgt_chg, map_extent=(60, 145, 15, 55),
                      hgt_f_contour_kwargs={}, hgt_fp_contour_kwargs={}, hgt_chg_contourf_kwargs={},
                      **pallete_kwargs):
    init_time = pd.to_datetime(hgt_f.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(hgt_f['dtime'].values[0])

    data_name = str(hgt_f['member'].values[0])
    forcast_info = hgt_f.stda.description()
    title = '[{}] {}hPa 位势高度场 当前时次预报（实线），24小时前预报（虚线），预报调整（填色）'.format(data_name.upper(),hgt_f['level'].values[0])
    png_name = '{2}_位势高度场_24小时预报调整_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.jpg'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['hgt_chg'] = contourf_2d(obj.ax, hgt_chg, cmap='PiYG',levels=np.arange(-4,4,1), cb_ticks=np.arange(-4,4,1), cb_label='24小时预报调整(dagpm)', extend='neither',kwags=hgt_chg_contourf_kwargs)
    obj.img['hgt_f'] = contour_2d(obj.ax, hgt_f, levels=np.arange(400,600,4),linewidths=1,cb_fontsize=15,kwargs=hgt_f_contour_kwargs)
    obj.img['hgt_fp'] = contour_2d(obj.ax, hgt_fp, levels=np.arange(400,600,4),linewidths=1,linestyles='dotted',colors='red',cb_colors='red',cb_fontsize=15,linewidthsfloat=0.8,kwargs=hgt_fp_contour_kwargs)
    obj.save()
    return obj.get_mpl()

def draw_wind_fcst_change(wsp_f, wsp_fp, wsp_chg, u_f, v_f, u_fp, v_fp, map_extent=(60, 145, 15, 55),
                      wsp_f_contour_kwargs={}, wsp_fp_contour_kwargs={}, wsp_chg_contourf_kwargs={}, uv_f_barbs_kwargs={}, uv_fp_barbs_kwargs={},
                      **pallete_kwargs):
    init_time = pd.to_datetime(wsp_f.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(wsp_f['dtime'].values[0])

    data_name = str(wsp_f['member'].values[0])
    forcast_info = wsp_f.stda.description()
    fhour0=int(wsp_fp['dtime'].values[0])
    title = '[{}] {}hPa 当前时次预报及低空急流（黑色），{}小时前低空急流（蓝色）、经向风速预报调整'.format(data_name.upper(),wsp_fp['level'].values[0],fhour0)
    png_name = '{2}_风场_预报调整_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.jpg'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['wsp_chg'] = wsp_contourf(obj.ax, wsp_chg, cmap='PiYG',levels=np.arange(-20,20,2), colorbar_kwargs={'label':'{}小时经向风速预报调整(m/s)'.format(fhour0)}, kwags=wsp_chg_contourf_kwargs)
    obj.img['wsp_f'] = contour_2d(obj.ax, wsp_f, colors='black',cb_colors='black',levels=[12],linewidths=1,cb_fontsize=15,kwargs=wsp_f_contour_kwargs)
    obj.img['wsp_fp'] = contour_2d(obj.ax, wsp_fp, colors='blue',cb_colors='blue',levels=[12],linewidths=1,cb_fontsize=15,kwargs=wsp_fp_contour_kwargs)
    obj.img['uv_f'] = uv_barbs(obj.ax, u_f, v_f, color='black',kwargs=uv_f_barbs_kwargs)
    # obj.img['uv_fp'] = uv_barbs(obj.ax, u_fp, v_fp, color='red',kwargs=uv_fp_barbs_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_prmsl_fcst_change(prmsl_f, prmsl_fp, prmsl_chg, map_extent=(60, 145, 15, 55),
                      prmsl_f_contour_kwargs={}, prmsl_fp_contour_kwargs={}, prmsl_chg_contourf_kwargs={},
                      **pallete_kwargs):
    init_time = pd.to_datetime(prmsl_f.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(prmsl_f['dtime'].values[0])

    data_name = str(prmsl_f['member'].values[0])
    forcast_info = prmsl_f.stda.description()
    title = '[{}] 海平面气压场 当前时次预报（实线），24小时前预报（虚线），预报调整（填色）'.format(data_name.upper())
    png_name = '{2}_海平面气压场_24小时预报调整_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.jpg'.format(init_time, fhour, data_name.upper())

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)
    obj.img['prmsl_chg'] = contourf_2d(obj.ax, prmsl_chg, cmap='PiYG',levels=np.arange(-10,10,1), cb_ticks=np.arange(-10,10,1), cb_label='24小时预报调整(hPa)', extend='neither',kwags=prmsl_chg_contourf_kwargs)
    obj.img['prmsl_f'] = prmsl_contour(obj.ax, prmsl_f, levels=np.arange(800,1080,2.5),kwargs=prmsl_f_contour_kwargs)
    obj.img['prmsl_fp'] = prmsl_contour(obj.ax, prmsl_fp, levels=np.arange(800,1080,2.5),linestyles='dotted',colors='red',linewidthsfloat=0.8,kwargs=prmsl_fp_contour_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_obs_wind_div_td(u10m, v10m, div, td, map_extent=(60, 145, 15, 55),
                         div_contourf_kwargs={}, td_contour_kwargs={}, uv_barbs_kwargs={},
                         **pallete_kwargs):
    obs_time = pd.to_datetime(td.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()

    forcast_info = td.stda.description()
    title = '10米风场+散度（填色）、2米露点（等值线）'
    png_name = '10米风场_散度_2米露点_观测时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时.jpg'.format(obs_time)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, add_city=False,background_zoom_level=7,kwargs=pallete_kwargs)
    obj.img['div'] = div_contourf(obj.ax, div, levels=np.arange(-200,220,20), cmap='PiYG', extend='both', kwargs=div_contourf_kwargs)
    obj.img['td'] = contour_2d(obj.ax, td, levels=np.arange(-100,100,1),kwargs=td_contour_kwargs)
    obj.img['uv10m'] = barbs_2d(obj.ax, u10m.dropna(), v10m.dropna(), length=5.5, lw=0.5, sizes=dict(emptybarb=0.0), regrid_shape=None, color='black',kwargs=uv_barbs_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_obs_wind_div_tmp(u10m, v10m, div, tmp, map_extent=(60, 145, 15, 55),
                         div_contourf_kwargs={}, tmp_contour_kwargs={}, uv_barbs_kwargs={},
                         **pallete_kwargs):
    obs_time = pd.to_datetime(tmp.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()

    forcast_info = tmp.stda.description()
    title = '10米风场+散度（填色）、温度（等值线）'
    png_name = '10米风场_散度_温度_观测时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时.jpg'.format(obs_time)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, add_city=False,background_zoom_level=7,kwargs=pallete_kwargs)
    obj.img['div'] = div_contourf(obj.ax, div, levels=np.arange(-200,220,20), cmap='PiYG', extend='both', kwargs=div_contourf_kwargs)
    obj.img['tmp'] = contour_2d(obj.ax, tmp, levels=np.arange(-100,100,2),kwargs=tmp_contour_kwargs)
    obj.img['uv10m'] = barbs_2d(obj.ax, u10m.dropna(), v10m.dropna(), length=5.5, lw=0.5, sizes=dict(emptybarb=0.0), regrid_shape=None, color='black',kwargs=uv_barbs_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_obs_wind_wsp_div_dtmp(u10m, v10m, wsp, div, dtmp, map_extent=(60, 145, 15, 55),
                               div_contourf_kwargs={}, dtmp_contour_kwargs={}, wsp_contour_kwargs={}, uv_barbs_kwargs={},
                               **pallete_kwargs):
    obs_time = pd.to_datetime(div.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()

    forcast_info = div.stda.description()
    title = '10米风场、风速（蓝线）+散度（填色），2米气温的1小时变温（等值线）'
    png_name = '10米风场、风速_散度_2米气温的1小时变温_观测时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时.jpg'.format(obs_time)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, add_city=False,background_zoom_level=7,kwargs=pallete_kwargs)
    obj.img['div'] = div_contourf(obj.ax, div, levels=np.arange(-200,220,20), cmap='PiYG', extend='both', kwargs=div_contourf_kwargs)
    obj.img['dtmp'] = contour_2d(obj.ax, dtmp, levels=np.arange(-100,-2,0.5),kwargs=dtmp_contour_kwargs)
    obj.img['wsp'] = contour_2d(obj.ax, wsp, colors='blue',cb_colors='blue',levels=np.arange(12,100,1),linewidths=1,cb_fontsize=15, kwargs=wsp_contour_kwargs)
    obj.img['uv10m'] = barbs_2d(obj.ax, u10m.dropna(), v10m.dropna(), length=5.5, lw=0.5, sizes=dict(emptybarb=0.0), regrid_shape=None, color='black',kwargs=uv_barbs_kwargs)
    obj.save()
    return obj.get_mpl()


def draw_obs_rain24(rain, map_extent=(60, 145, 15, 55),add_extrema=True,clip_area=None,
                  rain_contourf_kwargs={},
                  rain_contour_kwargs={},
                  extrema_text_kwargs={},
                  **pallete_kwargs):
    init_time = pd.to_datetime(rain.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(rain['dtime'].values[0])
    fcst_time = init_time + datetime.timedelta(hours=fhour)

    valid_time = rain.attrs['valid_time']
    data_name = str(rain['member'].values[0])
    var_cn_name = rain.attrs['var_cn_name']
    title = '[{}] {}小时降水'.format(data_name.upper(), valid_time)

    forcast_info = rain.stda.description()
    png_name = '{2}_降水_{3}_预报_起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时预报时效_{1:}小时.png'.format(init_time, fhour, data_name.upper(), var_cn_name)

    obj = horizontal_compose(title=title, description=forcast_info, png_name=png_name, map_extent=map_extent, kwargs=pallete_kwargs)

    img_qpf=contourf_2d(obj.ax, rain, levels=[1,10,25,50,100,250], linewidths=1, extend='max', cb_fontsize=10, map='met/rain')
    obj.img['rain_contourf'] = img_qpf

    if (clip_area != None):
        utl_plotmap.shp2clip_by_region_name(img_qpf, obj.ax, clip_area)

    if(add_extrema):
        extrma_text=add_extrema_on_ax(obj.ax,rain,kwargs=extrema_text_kwargs)
        
    obj.save()
    return obj.get_mpl()