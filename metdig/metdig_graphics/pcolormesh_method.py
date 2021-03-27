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


def vvel_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], '0.1*Pa/s')

    levels = [-30, -20, -10, -5, -2.5, -1, -0.5, 0.5, 1, 2.5, 5, 10, 20, 30]
    cmap, norm = cm_collected.get_cmap('met/vertical_velocity_nws', extend='both', levels=levels)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='Vertical Velocity (0.1*Pa/s)', extend='max')


def theta_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'K')

    levels = np.arange(300, 365, 1)
    cmap, norm = cm_collected.get_cmap('met/theta', extend='both', levels=levels)

    img = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Theta-E (K)')


def tmp_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'degC')

    cmap = cm_collected.get_cmap('met/temp')
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Temperature (°C)')


def wsp_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'm/s')

    levels = [12, 15, 18, 21, 24, 27, 30]
    cmap, norm = cm_collected.get_cmap('met/wsp', extend='neither', levels=levels)
    if levels:
        z = np.where(z >= levels[0], z, np.nan)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Wind Speed (m/s)', extend='max')


def tcwv_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'mm')

    levels = np.concatenate((np.arange(25), np.arange(26, 84, 2)))
    cmap, norm = cm_collected.get_cmap('met/precipitable_water_nws', extend='both', levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='(mm)', extend='max')


def rh_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'percent')

    levels = [0, 1, 5, 10, 20, 30, 40, 50, 60, 65, 70, 75, 80, 85, 90, 99]
    cmap, norm = cm_collected.get_cmap('met/relative_humidity_nws', extend='max', levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='(%)', extend='max')


def spfh_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'g/kg')

    levels = np.arange(2, 24, 0.5)
    cmap, norm = cm_collected.get_cmap('met/specific_humidity_nws', extend='both', levels=levels)

    img = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Specific Humidity (g/kg)')


def wvfl_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'g/(cm*hPa*s)')

    levels = np.arange(5, 46).tolist()
    cmap, norm = cm_collected.get_cmap('met/wvfl_ctable', extend='max', levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    if levels:
        z = np.where(z >= levels[0], z, np.nan)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Water Vapor Flux g/(cm*hPa*s)', extend='max')


def tmx_pcolormesh(ax, stda, add_colorbar=True, add_city=False, transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'degC')

    cmap = cm_collected.get_cmap('met/temp')

    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, alpha=alpha, vmin=-45, vmax=45, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='°C', extend='both')

    if add_city:
        utl_plotmap.add_city_values_on_map(ax, stda)


def gust_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=1, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'm/s')

    # levels = [0, 3.6, 3.6, 10.8, 10.8, 17.2, 17.2, 24.5, 24.5, 32.7, 32.7, 42] # 未用到？
    cmap = cm_collected.get_cmap('met/wind_speed_nws')

    z = np.where(z < 7.9, np.nan, z)

    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        ticks = [8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7, 37, 41.5, 46.2, 51.0, 56.1, 61.3]
        utl.add_colorbar(ax, img, ticks=ticks, label='风速 (m/s)', extend='max')


def dt2m_pcolormesh(ax, stda, add_colorbar=True, transform=ccrs.PlateCarree(), alpha=1, **kwargs):
    x, y, z = stda['lon'].values, stda['lat'].values, stda.values.squeeze()
    z, z_units = numpy_units_convert(z, stda.attrs['var_units'], 'degC')

    cmap = cm_collected.get_cmap('ncl/hotcold_18lev')
    cmap = cm_collected.linearized_cmap(cmap)

    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, alpha=alpha, vmin=-16, vmax=16, **kwargs)
    if add_colorbar:
        ticks = [-16, -12, -10, -8, -6, -4, 0, 4, 6, 8, 10, 12, 16]
        utl.add_colorbar(ax, img, ticks=ticks, label='°C', extend='both')