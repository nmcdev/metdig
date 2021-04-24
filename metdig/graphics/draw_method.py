# -*- coding: utf-8 -*-

import numpy as np

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.patheffects as mpatheffects

import metdig.graphics.lib.utility as utl
# from metdig.graphics.lib.utility import plt_kwargs_lcn_set # 弃用

# import metdig.graphics.cmap.ctables as dk_ctables # 弃用
import metdig.graphics.cmap.cm as cm_collected

import metdig.graphics.lib.utl_plotmap as utl_plotmap

def heatwave_contourf(ax, x, y, z, levels=[33,35,37,40,50],transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    cmap,norm = cm_collected.get_cmap('YlOrBr', extend='max', levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)
    img = ax.contourf(x, y, z,levels=levels, cmap=cmap,norm=norm, transform=transform, alpha=alpha, **kwargs)
    return img,levels

def heatwave_scatter(ax,x,y,z,levels=[33,35,37,40],alpha=0.5,transform=ccrs.PlateCarree(),**kwargs):
    cmap, norm = cm_collected.get_cmap('YlOrBr', extend='max', levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)
    img = ax.scatter(x,y,c=z,s=(z-33)*3+3,cmap=cmap,transform=transform, norm=norm,alpha=alpha,**kwargs)
    return img

def uv_barbs(ax, x, y, u, v,color='black',
             transform=ccrs.PlateCarree(), length=6, regrid_shape=20, fill_empty=False, sizes=dict(emptybarb=0.05),
             **kwargs):

    img = ax.barbs(x, y, u, v,color=color,
                   transform=transform, length=length, regrid_shape=regrid_shape, fill_empty=fill_empty, sizes=sizes,
                   **kwargs)
    return img


def hgt_contour(ax, x, y, z, transform=ccrs.PlateCarree(), colors='black', linewidths=2, **kwargs):
    # 颜色表预定义
    levels = np.append(np.append(np.arange(0, 480, 4), np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))), np.arange(604, 2000, 8))
    cmap = None
    norm = None

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)
    return img, levels


def vvel_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    # 颜色表预定义
    levels = [-30, -20, -10, -5, -2.5, -1, -0.5, 0.5, 1, 2.5, 5, 10, 20, 30]
    # cmap, norm, levels = dk_ctables.cm_vertical_velocity_nws()

    cmap, norm = cm_collected.get_cmap('met/vertical_velocity_nws', extend='both', levels=levels)

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img, levels


def theta_pcolormesh(ax, x, y, z, levels=np.arange(300,365,1),transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    # 颜色表预定义
    # cmap = dk_ctables.cm_theta()
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)
    # levels = None
    # norm = None

    cmap,norm = cm_collected.get_cmap('met/theta', extend='both', levels=levels)
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.pcolormesh(x, y, z, cmap=cmap,norm=norm, transform=transform, alpha=alpha, **kwargs)
    return img


def tmp_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    # 颜色表预定义
    # cmap = dk_ctables.cm_temp()
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)
    # levels = None
    # norm = None

    cmap = cm_collected.get_cmap('met/temp')
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img


def prmsl_contourf(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    # 颜色表预定义
    levels = np.arange(960, 1065, 5)
    cmap = cm_collected.get_cmap('guide/cs26')
    # norm = None

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img, levels


def wsp_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    # 颜色表预定义
    levels = [12, 15, 18, 21, 24, 27, 30]
    # colors = ["#FFF59D", "#FFEE58", "#FFCA28", "#FFC107", "#FF9800", "#FB8C00", '#E64A19', '#BF360C']  # RRGGBBAA
    # cmap = ListedColormap(colors, 'wsp')
    # norm = BoundaryNorm(levels, ncolors=cmap.N, clip=False)

    cmap, norm = cm_collected.get_cmap('met/wsp', extend='neither', levels=levels)


    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    if levels:
        z = np.where(z >= levels[0], z, np.nan)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img, levels


def tcwv_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    # 颜色表预定义
    levels = np.concatenate((np.arange(25), np.arange(26, 84, 2)))
    # cmap, norm, levels = dk_ctables.cm_precipitable_water_nws(pos=levels)
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    cmap, norm = cm_collected.get_cmap('met/precipitable_water_nws', extend='both', levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img, levels


def rh_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    # 颜色表预定义
    # cmap, norm, levels = dk_ctables.cm_relative_humidity_nws()
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    levels = [0, 1, 5, 10, 20, 30, 40, 50, 60, 65, 70, 75, 80, 85, 90, 99]
    cmap, norm = cm_collected.get_cmap('met/relative_humidity_nws', extend='max', levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img


def spfh_pcolormesh(ax, x, y, z, levels = np.arange(2,24,0.5),
                     transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    # 颜色表预定义
    # cmap, levels = dk_ctables.cm_specific_humidity_nws(pos=levels)
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)
    # norm = None
    cmap,norm = cm_collected.get_cmap('met/specific_humidity_nws',extend='both',levels=levels)
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm, transform=transform, alpha=alpha, **kwargs)
    return img, levels


def wvfl_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    # 颜色表预定义
    # cmap, norm, levels = dk_ctables.wvfl_ctable()
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)
    levels = np.arange(5,46).tolist()
    cmap, norm = cm_collected.get_cmap('met/wvfl_ctable', extend='max', levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    if levels:
        z = np.where(z >= levels[0], z, np.nan)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img


def pv_contour(ax, x, y, z, transform=ccrs.PlateCarree(), colors='black', linewidths=2, **kwargs):
    # 颜色表预定义
    levels = np.arange(0, 25, 1)
    cmap = None
    norm = None

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.contour(x, y, z, levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    return img, levels


def div_contourf(ax, x, y, z, levels=np.arange(-10, 11, 1),transform=ccrs.PlateCarree(),cmap = cm_collected.get_cmap('PuOr'), alpha=0.5, extend='both', **kwargs):
    # 颜色表预定义
    norm = None

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    return img, levels


def rain_contourf(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.8, extend='max', **kwargs):
    # 颜色表预定义
    levels = [0.1, 4, 13, 25, 60, 120]
    # colors = ["#88F492", "#00A929", "#2AB8FF", "#1202FC", "#FF04F4", "#850C3E"]
    # cmap = None
    # norm = None
    cmap = cm_collected.get_cmap('met/rain')
    colors = cmap.colors

    # 颜色表通用参数替换预定义颜色表
    # cmap, norm, levels, kwargs = plt_kwargs_lcn_set(cmap, norm, levels, **kwargs)

    img = ax.contourf(x, y, z, levels, colors=colors, transform=transform, alpha=alpha, extend=extend, **kwargs)
    return img, levels

#-------------------------
# 后面的均未使用plt_kwargs_lcn_set，后续再考虑优化


def tmx_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), vmin=-45, vmax=45, alpha=0.5, **kwargs):
    # cmap = dk_ctables.cm_temp()
    cmap = cm_collected.get_cmap('met/temp')
    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, alpha=0.5, vmin=-45, vmax=45, **kwargs)

    return img


def tmx_contour(ax, x, y, z, colors=['#FF8F00', '#FF6200', '#FF0000'], levels=[35, 37, 40], linewidths=2, transform=ccrs.PlateCarree(), **kwargs):
    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=2, transform=transform, **kwargs)
    cl = plt.clabel(img, inline=1, fontsize=15, fmt='%i', colors=colors)

    if(cl is not None):
        for t in cl:
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='white'),
                                mpatheffects.Normal()])
    return img


def gust_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), vmin=7.9, vmax=65, alpha=0.5, **kwargs):
    # cmap, levels = dk_ctables.cm_wind_speed_nws()
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    levels = [0, 3.6, 3.6, 10.8, 10.8, 17.2, 17.2, 24.5, 24.5, 32.7, 32.7, 42]
    cmap = cm_collected.get_cmap('met/wind_speed_nws')

    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, **kwargs)
    return img


def dt2m_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=1, vmin=-16, vmax=16, **kwargs):
    # cmap = cm_collected.linearized_ncl_cmap('hotcold_18lev')

    cmap = cm_collected.get_cmap('ncl/hotcold_18lev')
    cmap = cm_collected.linearized_cmap(cmap)

    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, alpha=alpha, vmin=vmin, vmax=vmax, **kwargs)
    return img


def dt2m_contour(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, vmin=-16, vmax=16, **kwargs):
    levels = [-16, -12, -10, -8, -6, 6, 8, 10, 12, 16]
    # cmap = cm_collected.linearized_ncl_cmap('BlRe')

    cmap = cm_collected.get_cmap('ncl/BlRe')
    cmap = cm_collected.linearized_cmap(cmap)

    img = ax.contour(x, y, z, levels=levels, cmap=cmap, transform=transform, alpha=alpha, vmin=vmin, vmax=vmax, **kwargs)

    clev_colors = []
    for iclev in levels:
        per_color = cm_collected.get_part_clev_and_cmap(cmap=cmap, clev_range=[-16, 16], clev_slt=iclev)
        clev_colors.append(np.squeeze(per_color[:]))

    cl = plt.clabel(img, inline=1, fontsize=15, fmt='%i', colors=clev_colors)
    # for t in cl:
    #     t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'), mpatheffects.Normal()])
    return img


def rain_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, valid_time=24, **kwargs):

    if valid_time == 24:
        levels = [0.1, 10, 25, 50, 100, 250, 800]
    elif valid_time == 6:
        levels = [0.1, 4, 13, 25, 60, 120, 800]
    else:
        levels = [0.01, 2, 7, 13, 30, 60, 800]
    cmap, norm = cm_collected.get_cmap('met/rain_nws', extend='neither', levels=levels)

    # cmap, norm, _ = dk_ctables.cm_rain_nws(atime=valid_time)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img

def sleet_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, valid_time=24, **kwargs):

    if valid_time == 24:
        levels = [0.1, 10, 25, 50, 100, 250]
    elif valid_time == 6:
        levels = [0.1, 4, 13, 25, 60, 120]
    else:
        levels = [0.1, 2, 7, 13, 30, 60]
    cmap, norm = cm_collected.get_cmap('met/sleet_nws', extend='max', levels=levels)

    # cmap, norm, _ = dk_ctables.cm_sleet_nws(atime=valid_time)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img


def snow_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, valid_time=24, **kwargs):
    # print(np.nanmin(z),np.nanmax(z))

    if valid_time == 24:
        levels = [0.1, 2.5, 5, 10, 20, 30]
    elif valid_time == 6:
        levels = [0.1, 1, 3, 5, 10, 15]
    else:
        levels = [0.1, 1, 2, 4, 8, 12]
    cmap, norm = cm_collected.get_cmap('met/snow_nws', extend='max', levels=levels)

    # cmap, norm, _ = dk_ctables.cm_snow_nws(atime=valid_time)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img


def qpf_pcolormesh(ax, x, y, z, transform=ccrs.PlateCarree(), alpha=0.5, valid_time=24, **kwargs):
    if valid_time == 24:
        levels = np.concatenate((
            np.array([0, 0.1, 0.5, 1]), np.arange(2.5, 25, 2.5),
            np.arange(25, 50, 5), np.arange(50, 150, 10),
            np.arange(150, 475, 25)))
    elif valid_time == 6:
        levels = np.concatenate(
            (np.array([0, 0.1, 0.5]), np.arange(1, 4, 1),
             np.arange(4, 13, 1.5), np.arange(13, 25, 2),
             np.arange(25, 60, 2.5), np.arange(60, 105, 5)))
    else:
        levels = np.concatenate(
            (np.array([0, 0.01, 0.1]), np.arange(0.5, 2, 0.5),
             np.arange(2, 8, 1), np.arange(8, 20, 2),
             np.arange(20, 55, 2.5), np.arange(55, 100, 5)))
    cmap, norm = cm_collected.get_cmap('met/qpf_nws', extend='max', levels=levels)
    # cmap, norm, _ = dk_ctables.cm_qpf_nws(atime=valid_time)

    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    return img


def cross_rh_contourf(ax, x, y, z, levels=np.arange(0, 101, 0.5), cmap=None, **kwargs):

    if cmap is None:
        startcolor = '#1E90FF'  # 蓝色
        midcolor = '#F1F1F1'  # 白色
        endcolor = '#696969'  # 灰色
        cmap = col.LinearSegmentedColormap.from_list('own2', [startcolor, midcolor, endcolor])

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)

    return img

def cross_mpv_contourf(ax, x, y, z, levels=np.arange(-50, 50, 1), cmap=None, **kwargs):
    if cmap is None:
        cmap = cm_collected.get_cmap('ncl/cmp_flux')

    img = ax.contourf(x, y, z*1e6, levels=levels, cmap=cmap, **kwargs)
    return img

def cross_absv_contourf(ax, x, y, z, levels=np.arange(-60, 60, 1), cmap=None, **kwargs):
    if cmap is None:
        cmap = cm_collected.get_cmap('ncl/hotcold_18lev')

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
    return img


def cross_terrain_contourf(ax, x, y, z, levels=np.arange(0, 500, 1), cmap=None, **kwargs):
    if cmap is None:
        startcolor = '#8B4513'  # 棕色
        endcolor = '#DAC2AD'  # 绿
        cmap = col.LinearSegmentedColormap.from_list('own3', [endcolor, startcolor])

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)

    return img


def cross_tmp_contour(ax, x, y, z, levels=np.arange(-100, 100, 2), colors='#A0522D'):

    tmp_contour = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=1)

    tmp_contour.clabel(levels, fontsize=16, colors=colors, inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    tmp_zero_contour = ax.contour(x, y, z, levels=[0], colors='k', linewidths=3)

    tmp_zero_contour.clabel([0], fontsize=22, colors='k', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)


def cross_section_hgt(ax, x, y, z, levels=np.arange(500, 600, 4), cmap='inferno',
                      st_point=None, ed_point=None, lon_cross=None, lat_cross=None,
                      map_extent=(60, 145, 15, 55), h_pos=[0.125, 0.665, 0.25, 0.2]):
    crs = ccrs.PlateCarree()
    if not h_pos:
        l, b, w, h = ax.get_position().bounds
        h_pos = [l, b + h - 0.22, 0.25, 0.2]
    # ax_inset = fig.add_axes(h_pos, projection=crs)
    ax_inset = plt.axes(h_pos, projection=crs)
    ax_inset.set_extent(map_extent, crs=crs)
    # Add geographic features
    ax_inset.coastlines()
    utl_plotmap.add_china_map_2cartopy_public(ax_inset, name='province', edgecolor='black', lw=0.8, zorder=105)
    # Set the titles and axes labels
    ax_inset.set_title('')

    # plot geopotential height at 500 hPa using xarray's contour wrapper
    # plot the path of the cross section
    ax_inset.contour(x, y, z, levels=levels, cmap='inferno')

    if st_point is not None and ed_point is not None:
        endpoints = crs.transform_points(ccrs.Geodetic(), *np.vstack([st_point, ed_point]).transpose()[::-1])
        ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)

    if lon_cross is None or lat_cross is None:
        if st_point is not None and ed_point is not None:
            ax_inset.plot(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
    else:
        ax_inset.plot(lon_cross, lat_cross, c='k', zorder=2)
