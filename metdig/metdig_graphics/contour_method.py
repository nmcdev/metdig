import numpy as np

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.patheffects as mpatheffects

import metdig.metdig_graphics.lib.utility as utl
import metdig.metdig_graphics.lib.utl_plotmap as utl_plotmap
import metdig.metdig_graphics.cmap.cm as cm_collected

from metdig.metdig_utl import numpy_units_convert


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
        plt.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors='black')


def tmx_contour(ax, stda, add_clabel=True, levels=[35, 37, 40], colors=['#FF8F00', '#FF6200', '#FF0000'], transform=ccrs.PlateCarree(), linewidths=2, **kwargs):
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
