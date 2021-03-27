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


def div_contourf(ax, stda, add_colorbar=True, levels=np.arange(-10, -1), cmap='Blues_r', extend='both', transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], '1e-5/s')

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='Divergence 10' + '$^{-5}$s$^{-1}$')


def prmsl_contourf(ax, stda, add_colorbar=True, levels=np.arange(960, 1065, 5), cmap='guide/cs26', extend='neither', transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'hPa')

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='Mean sea level pressure (hPa)', extend='max')


def rain_contourf(ax, stda, add_colorbar=True, levels=[0.1, 4, 13, 25, 60, 120], cmap='met/rain', extend='max', transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'mm')

    cmap = cm_collected.get_cmap(cmap)
    colors = cmap.colors

    img = ax.contourf(x, y, z, levels, colors=colors, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='{}h precipitation (mm)'.format(stda.attrs['valid_time']), extend='max')
