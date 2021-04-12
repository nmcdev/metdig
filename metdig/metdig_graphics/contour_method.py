import numpy as np

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.patheffects as mpatheffects

import metdig.metdig_graphics.lib.utility as utl
import metdig.metdig_graphics.cmap.cm as cm_collected

from metdig.metdig_utl import numpy_units_convert


def contour_2d(ax, stda, xdim='lon', ydim='lat', draw_units='',
               add_clabel=True, cb_fontsize=20, cb_fmt='%.0f', cb_colors='black',
               levels=None, colors='black', transform=ccrs.PlateCarree(), linewidths=2, **kwargs):
    """[graphics层绘制contour平面图通用方法]

    Args:
        ax ([type]): [description]
        stda ([type]): [stda标准格式]
        xdim (str, optional): [绘图时x维度名称，从以下stda维度名称中选择一个填写: member, level, time dtime, lat, lon]. Defaults to 'lon'.
        ydim (str, optional): [绘图时y维度名称，从以下stda维度名称中选择一个填写: member, level, time dtime, lat, lon]. Defaults to 'lat'.
        draw_units (str, optional): [绘图时单位，如果不传则不进行单位转换，默认用stda中的单位]. Defaults to ''.
        add_clabel (bool, optional): [是否调用plt.clabel]. Defaults to True.
        cb_fontsize (int, optional): [clabel字体大小]. Defaults to None.
        cb_fmt (str, optional): [clabel字体格式]. Defaults to None.
        cb_colors (str, optional): [clabel字体颜色]. Defaults to None.
        levels (list, optional): [description]. Defaults to None.
        colors (str, optional): [description]. Defaults to 'black'.
        transform ([type], optional): [description]. Defaults to ccrs.PlateCarree().
        linewidths (int, optional): [description]. Defaults to 2.
    """
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], draw_units)

    img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)

    if add_clabel:
        plt.clabel(img, inline=1, fontsize=cb_fontsize, fmt=cb_fmt, colors=cb_colors)


############################################################################################################################
# 以下为特殊方法，无法使用上述通用方法时在后面增加单独的方法
############################################################################################################################


def hgt_contour(ax, stda, add_clabel=True, transform=ccrs.PlateCarree(), linewidths=2, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'dagpm')

    levels = np.append(np.append(np.arange(0, 480, 4), np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))), np.arange(604, 2000, 8))
    colors = 'black'

    img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        plt.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors='black')


def pv_contour(ax, stda, add_clabel=True, transform=ccrs.PlateCarree(), linewidths=2, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], '1e-6*K*m**2/(s*kg)')

    levels = np.arange(0, 25, 1)
    colors = 'black'

    img = ax.contour(x, y, z, levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        plt.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors='black')


def prmsl_contour(ax, stda, add_clabel=True, transform=ccrs.PlateCarree(), linewidths=1, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'hPa')

    levels = np.arange(900, 1100, 2.5)
    colors = 'black'

    img = ax.contour(x, y, z, levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        plt.clabel(img, inline=1, fontsize=15, fmt='%.0f', colors='black')


def tmx_contour(
        ax, stda, add_clabel=True, levels=[35, 37, 40],
        colors=['#FF8F00', '#FF6200', '#FF0000'],
        transform=ccrs.PlateCarree(),
        linewidths=2, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'degC')

    img = ax.contour(x, y, z, levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        cl = plt.clabel(img, inline=1, fontsize=15, fmt='%i', colors=colors)
        if cl is not None:
            for t in cl:
                t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='white'), mpatheffects.Normal()])


def dt2m_contour(ax, stda, add_clabel=True, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'degC')

    levels = [-16, -12, -10, -8, -6, 6, 8, 10, 12, 16]
    cmap = cm_collected.get_cmap('ncl/BlRe')
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


def cross_theta_contour(ax, stda, xy=('lon', 'level'), add_clabel=True, linewidths=2, **kwargs):
    x, y, z = stda[xy[0]].values, stda[xy[1]].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'kelvin')

    levels = np.arange(250, 450, 5)

    img = ax.contour(x, y, z, levels=levels, colors='black', linewidths=linewidths)
    if add_clabel:
        plt.clabel(img, levels, fontsize=20, colors='k', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)


def cross_tmp_contour(ax, stda, xy=('lon', 'level'), add_clabel=True):
    x, y, z = stda[xy[0]].values, stda[xy[1]].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'degC')

    levels = np.arange(-100, 100, 2)

    img = ax.contour(x, y, z, levels=levels, colors='#A0522D', linewidths=1)
    if add_clabel:
        plt.clabel(img, levels, fontsize=16, colors='#A0522D', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    img = ax.contour(x, y, z, levels=[0], colors='k', linewidths=3)
    if add_clabel:
        plt.clabel(img, [0], fontsize=22, colors='k', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
