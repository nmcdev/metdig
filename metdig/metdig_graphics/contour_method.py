import numpy as np
import xarray as xr

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.patheffects as mpatheffects

import metdig.metdig_graphics.lib.utility as utl
import metdig.metdig_graphics.cmap.cm as cm_collected
from metdig.metdig_graphics.lib.utility import kwargs_wrapper


@kwargs_wrapper
def contour_2d(ax, stda, xdim='lon', ydim='lat',
               add_clabel=True, cb_fontsize=20, cb_fmt='%.0f', cb_colors='black', cb_level=None,
               levels=None, colors='black',
               transform=ccrs.PlateCarree(), linewidths=2,
               **kwargs):
    """[graphics层绘制contour平面图通用方法]

    Args:
        ax ([type]): [description]
        stda ([type]): [u矢量 stda标准格式]
        xdim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lon'.
        ydim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lat'.
        add_clabel (bool, optional): [是否调用plt.clabel]. Defaults to True.
        cb_fontsize (int, optional): [clabel字体大小]. Defaults to None.
        cb_fmt (str, optional): [clabel字体格式]. Defaults to None.
        cb_colors (str, optional): [clabel字体颜色]. Defaults to None.
        cb_level (str, optional): [clabel标出的等值线数值，None表示所有等值线全标]. Defaults to None.
        levels (list, optional): [description]. Defaults to None.
        colors (str, optional): [description]. Defaults to 'black'.
        transform ([type], optional): [stda的投影类型，仅在xdim='lon' ydim='lat'时候生效]. Defaults to ccrs.PlateCarree().
        linewidths (int, optional): [description]. Defaults to 2.
    """
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_2d_value(ydim, xdim)

    if transform is None or (xdim != 'lon' and ydim != 'lat'):
        img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, **kwargs)
    else:
        img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)

    if add_clabel:
        cb_level = levels if cb_level is None else cb_level
        if cb_level is None:
            plt.clabel(img, inline=1, fontsize=cb_fontsize, fmt=cb_fmt, colors=cb_colors)
        else:
            plt.clabel(img, cb_level, inline=1, fontsize=cb_fontsize, fmt=cb_fmt, colors=cb_colors)


############################################################################################################################
# 以下为特殊方法，无法使用上述通用方法时在后面增加单独的方法
############################################################################################################################


@kwargs_wrapper
def hgt_contour(ax, stda,  xdim='lon', ydim='lat',
                add_clabel=True,
                levels=np.append(np.append(np.arange(0, 480, 4), np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))), np.arange(604, 2000, 8)),
                colors='black',
                transform=ccrs.PlateCarree(), linewidths=2,
                **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_2d_value(ydim, xdim) # dagpm

    img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        plt.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors='black')


@kwargs_wrapper
def pv_contour(ax, stda, xdim='lon', ydim='lat',
               add_clabel=True,
               levels=np.arange(0, 25, 1), colors='black',
               transform=ccrs.PlateCarree(), linewidths=2, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_2d_value(ydim, xdim) # K*m**2/(s*kg)
    z = z * 1e6  # 1e-6*K*m**2/(s*kg)

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        plt.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors='black')


@kwargs_wrapper
def prmsl_contour(ax, stda, xdim='lon', ydim='lat',
                  add_clabel=True,
                  levels=np.arange(900, 1100, 2.5), colors='black',
                  transform=ccrs.PlateCarree(), linewidths=1, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_2d_value(ydim, xdim) # 'hPa'

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        plt.clabel(img, inline=1, fontsize=15, fmt='%.0f', colors=colors)


@kwargs_wrapper
def tmx_contour(ax, stda,  xdim='lon', ydim='lat',
                add_clabel=True,
                levels=[35, 37, 40], colors=['#FF8F00', '#FF6200', '#FF0000'],
                transform=ccrs.PlateCarree(), linewidths=2, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_2d_value(ydim, xdim) # degC

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        cl = plt.clabel(img, inline=1, fontsize=15, fmt='%i', colors=colors)
        if cl is not None:
            for t in cl:
                t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='white'), mpatheffects.Normal()])


@kwargs_wrapper
def dt2m_contour(ax, stda, xdim='lon', ydim='lat',
                 add_clabel=True,
                 levels=[-16, -12, -10, -8, -6, 6, 8, 10, 12, 16], cmap='ncl/BlRe',
                 transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_2d_value(ydim, xdim)  # degC

    cmap = cm_collected.get_cmap(cmap)
    cmap = cm_collected.linearized_cmap(cmap)

    img = ax.contour(x, y, z, levels=levels, cmap=cmap, transform=transform, alpha=alpha, vmin=-16, vmax=16, **kwargs)

    if add_clabel:
        clev_colors = []
        for iclev in levels:
            per_color = cm_collected.get_part_clev_and_cmap(cmap=cmap, clev_range=[-16, 16], clev_slt=iclev)
            clev_colors.append(np.squeeze(per_color[:]))
        cl = plt.clabel(img, inline=1, fontsize=15, fmt='%i', colors=clev_colors)
        if cl is not None:
            for t in cl:
                t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'), mpatheffects.Normal()])


@kwargs_wrapper
def cross_theta_contour(ax, stda, xdim='lon', ydim='level',
                        add_clabel=True, 
                        levels=np.arange(250, 450, 5), colors='black',
                        linewidths=2, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_2d_value(ydim, xdim) # kelvin

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        plt.clabel(img, fontsize=17, colors=colors, inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)


@kwargs_wrapper
def cross_tmp_contour(ax, stda, xdim='lon', ydim='level', 
                      add_clabel=True, 
                      levels=np.arange(-100, 100, 2), colors='#A0522D', **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_2d_value(ydim, xdim) # degC

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=1, **kwargs)
    if add_clabel:
        plt.clabel(img, fontsize=17, colors=colors, inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    if z.min() < 0 and z.max() > 0:
        img = ax.contour(x, y, z, levels=[0], colors='k', linewidths=3)
        if add_clabel:
            plt.clabel(img, [0], fontsize=22, colors='k', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
