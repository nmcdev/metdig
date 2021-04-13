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


def contourf_2d(ax, stda, xdim='lon', ydim='lat',
                add_colorbar=True, cb_pos='bottom', cb_ticks=None, cb_label=None,
                levels=None, cmap='jet', extend='both',
                transform=ccrs.PlateCarree(), alpha=0.8,
                **kwargs):
    """[graphics层绘制contourf平面图通用方法]

    Args:
        ax ([type]): [description]
        stda ([type]): [stda标准格式]
        xdim (str, optional): [绘图时x维度名称，从以下stda维度名称中选择一个填写: member, level, time dtime, lat, lon]. Defaults to 'lon'.
        ydim (str, optional): [绘图时y维度名称，从以下stda维度名称中选择一个填写: member, level, time dtime, lat, lon]. Defaults to 'lat'.
        add_colorbar (bool, optional): [是否绘制colorbar]. Defaults to True.
        cb_pos (str, optional): [colorbar的位置]. Defaults to 'bottom'.
        cb_ticks ([type], optional): [colorbar的刻度]. Defaults to None.
        cb_label ([type], optional): [colorbar的label，如果不传则自动进行var_cn_name和var_units拼接]. Defaults to None.
        levels ([list], optional): [description]. Defaults to None.
        cmap (str, optional): [description]. Defaults to 'jet'.
        extend (str, optional): [description]. Defaults to 'both'.
        transform ([type], optional): [description]. Defaults to ccrs.PlateCarree().
        alpha (float, optional): [description]. Defaults to 0.8.
    """
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values

    cmap, norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels)

    if transform is None:
        img = ax.contourf(x, y, z, levels, cmap=cmap, norm=norm, alpha=alpha, extend=extend, **kwargs)
    else:
        img = ax.contourf(x, y, z, levels, cmap=cmap, norm=norm, transform=transform, alpha=alpha, extend=extend, **kwargs)

    if add_colorbar:
        cb_units = stda.attrs['var_units']
        cb_name = stda.attrs['var_cn_name']
        cb_label = '{}({})'.format(cb_name, cb_units) if not cb_label else cb_label
        utl.add_colorbar(ax, img, ticks=cb_ticks, pos=cb_pos, extend=extend, label=cb_label)

############################################################################################################################
# 以下为特殊方法，无法使用上述通用方法时在后面增加单独的方法
############################################################################################################################


def div_contourf(ax, stda, xdim='lon', ydim='lat',
                 add_colorbar=True,
                 levels=np.arange(-10, -1), cmap='Blues_r', extend='both',
                 transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values  # 1/s
    z = z * 1e5  # 1e-5/s

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='Divergence 10' + '$^{-5}$s$^{-1}$')


def prmsl_contourf(ax, stda, xdim='lon', ydim='lat',
                   add_colorbar=True,
                   levels=np.arange(960, 1065, 5), cmap='guide/cs26', extend='neither',
                   transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values  # hPa

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='Mean sea level pressure (hPa)', extend='max')


def rain_contourf(ax, stda, xdim='lon', ydim='lat',
                  add_colorbar=True,
                  levels=[0.1, 4, 13, 25, 60, 120], cmap='met/rain', extend='max',
                  transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values  # mm

    cmap = cm_collected.get_cmap(cmap)
    colors = cmap.colors

    img = ax.contourf(x, y, z, levels, colors=colors, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='{}h precipitation (mm)'.format(stda.attrs['valid_time']), extend='max')


def cross_absv_contourf(ax, stda, xdim='lon', ydim='level',
                        add_colorbar=True,
                        levels=np.arange(-60, 60, 1), cmap='ncl/hotcold_18lev',
                        **kwargs):
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values  # 1/s
    z = z * 1e5  # 1e-5/s

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Absolute Vorticity (dimensionless)',  orientation='vertical', extend='max', pos='right')


def cross_rh_contourf(ax, stda, xdim='lon', ydim='level',
                      add_colorbar=True,
                      levels=np.arange(0, 101, 0.5), cmap=None,
                      **kwargs):
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values  # percent

    if cmap is None:
        startcolor = '#1E90FF'  # 蓝色
        midcolor = '#F1F1F1'  # 白色
        endcolor = '#696969'  # 灰色
        cmap = col.LinearSegmentedColormap.from_list('own2', [startcolor, midcolor, endcolor])

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=[20, 40, 60, 80, 100], label='Relative Humidity',  orientation='vertical', extend='max', pos='right')


def cross_spfh_contourf(ax, stda, xdim='lon', ydim='level',
                        add_colorbar=True,
                        levels=np.arange(0, 20, 2), cmap='YlGnBu',
                        **kwargs):
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values  # g/kg

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Specific Humidity (g/kg)',  orientation='vertical', extend='max', pos='right')


def cross_mpv_contourf(ax, stda, xdim='lon', ydim='level',
                       add_colorbar=True,
                       levels=np.arange(-50, 50, 1), cmap='ncl/cmp_flux',
                       **kwargs):
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values  # 1e-6*K*m**2/(s*kg)
    z = z * 1e6  # 1e-6*K*m**2/(s*kg)

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Moisture Potential Vorticity (10$^{-6}$ K*m**2/(s*kg))',
                         label_size=15, orientation='vertical', extend='max', pos='right')


def cross_terrain_contourf(ax, stda, xdim='lon', ydim='level',
                           levels=np.arange(0, 500, 1), cmap=None,
                           **kwargs):
    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.squeeze().transpose(ydim, xdim).values

    if cmap is None:
        startcolor = '#8B4513'  # 棕色
        endcolor = '#DAC2AD'  # 绿
        cmap = col.LinearSegmentedColormap.from_list('own3', [endcolor, startcolor])

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
