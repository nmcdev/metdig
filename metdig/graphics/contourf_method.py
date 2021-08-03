import numpy as np
import xarray as xr

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.patheffects as mpatheffects

import metdig.graphics.lib.utility as utl
import metdig.graphics.cmap.cm as cm_collected
from  metdig.graphics.lib.utility import kwargs_wrapper

@kwargs_wrapper
def contourf_2d(ax, stda, xdim='lon', ydim='lat',
                add_colorbar=True, cb_pos='bottom', cb_ticks=None, cb_label=None,
                levels=None, cmap='jet', extend='both', isLinear=False,
                transform=ccrs.PlateCarree(), alpha=0.8, 
                colorbar_kwargs={}, **kwargs):
    """[graphics层绘制contourf平面图通用方法]

    Args:
        ax ([type]): [description]
        stda ([type]): [u矢量 stda标准格式]
        xdim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lon'.
        ydim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lat'.
        add_colorbar (bool, optional): [是否绘制colorbar]. Defaults to True.
        cb_pos (str, optional): [colorbar的位置]. Defaults to 'bottom'.
        cb_ticks ([type], optional): [colorbar的刻度]. Defaults to None.
        cb_label ([type], optional): [colorbar的label，如果不传则自动进行var_cn_name和var_units拼接]. Defaults to None.
        levels ([list], optional): [description]. Defaults to None.
        cmap (str, optional): [description]. Defaults to 'jet'.
        extend (str, optional): [description]. Defaults to 'both'.
        isLinear ([bool], optional): [是否对colors线性化]. Defaults to False.
        transform ([type], optional): [stda的投影类型，仅在xdim='lon' ydim='lat'时候生效]. Defaults to ccrs.PlateCarree().
        alpha (float, optional): [description]. Defaults to 0.8.

    Returns:
        [type]: [绘图对象]
    """
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)

    cmap, norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels, isLinear=isLinear)

    if transform is None or (xdim != 'lon' and ydim != 'lat'):
        img = ax.contourf(x, y, z, levels, cmap=cmap, norm=norm, alpha=alpha, extend=extend, **kwargs)
    else:
        img = ax.contourf(x, y, z, levels, cmap=cmap, norm=norm, transform=transform, alpha=alpha, extend=extend, **kwargs)

    if add_colorbar:
        cb_label = '{}({})'.format(stda.attrs['var_cn_name'], stda.attrs['var_units']) if not cb_label else cb_label
        utl.add_colorbar(ax, img, ticks=cb_ticks, pos=cb_pos, extend=extend, label=cb_label, **colorbar_kwargs)
    
    return img

############################################################################################################################
# 以下为特殊方法，无法使用上述通用方法时在后面增加单独的方法
############################################################################################################################

@kwargs_wrapper
def cref_contourf(ax, stda, xdim='lon', ydim='lat',
                  add_colorbar=True,
                  levels=[10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70], 
                  transform=ccrs.PlateCarree(), alpha=1,colorbar_kwargs={},
                  **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm
    z[z<15]=np.nan
    colors = ['#01A0F6', '#00ECEC', '#00D800', '#019000', '#FFFF00', '#E7C000', '#FF9000', '#FF0000', '#D60000', '#D60000', '#FF00F0', '#9600B4', '#AD90F0']
    cmap, norm = cm_collected.get_cmap(colors, extend='max', levels=levels)

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='(dbz)', extend='max', **colorbar_kwargs)

@kwargs_wrapper
def heatwave_contourf(ax, stda, xdim='lon', ydim='lat', 
                      add_colorbar=True,
                      levels=[33,35,37,40,50], cmap='YlOrBr', extend='max', 
                      transform=ccrs.PlateCarree(), alpha=0.5, colorbar_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) 

    cmap,norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    img = ax.contourf(x, y, z,levels=levels, cmap=cmap, norm=norm, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='Temperature ($^\circ$C)', extendrect=False, **colorbar_kwargs)
    return img

@kwargs_wrapper
def qcld_contourf(ax, stda,  xdim='lon', ydim='lat',
                    add_colorbar=True, 
                    levels=np.arange(0.05,0.51,0.05), cmap='Greens', extend='max',
                    transform=ccrs.PlateCarree(), alpha=0.7, colorbar_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # g/kg
    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, alpha=alpha, transform=transform, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='QCLD (g kg$^{-1}$)',**colorbar_kwargs)
    return img

@kwargs_wrapper
def qsn_contourf(ax, stda,  xdim='lon', ydim='lat',
                    add_colorbar=True, 
                    levels=np.arange(0.05,0.51,0.05), cmap='Blues', extend='max',
                    transform=ccrs.PlateCarree(), alpha=0.7, colorbar_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # g/kg
    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, alpha=alpha, transform=transform, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='QSNOW (g kg$^{-1}$)',**colorbar_kwargs)
    return img


@kwargs_wrapper
def qice_contourf(ax, stda,  xdim='lon', ydim='lat',
                    add_colorbar=True, 
                    levels=np.arange(0.05,0.51,0.05), cmap='Blues', extend='max',
                    transform=ccrs.PlateCarree(), alpha=0.7, colorbar_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # g/kg
    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, alpha=alpha, transform=transform, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='QICE (g kg$^{-1}$)',**colorbar_kwargs)
    return img


@kwargs_wrapper
def tcwv_contourf(ax, stda, xdim='lon', ydim='lat',
    add_colorbar=True,
    levels = np.concatenate((np.arange(25), np.arange(26, 84, 2))),cmap='met/precipitable_water_nws', extend='max',
    transform=ccrs.PlateCarree(), alpha=0.8, colorbar_kwargs={}, **kwargs):

    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.stda.get_value(ydim, xdim)  # mm

    cmap = cm_collected.get_cmap(cmap)
    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='total column water(mm)', extend='max',**colorbar_kwargs)
    return img

@kwargs_wrapper
def ulj_contourf(ax, stda, xdim='lon', ydim='lat',
    add_colorbar=True,
    levels = np.arange(40,120,10),cmap=['#99E3FB', '#47B6FB','#0F77F7','#AC97F5','#A267F4','#9126F5','#E118F3'], extend='max',
    transform=ccrs.PlateCarree(), alpha=0.8, colorbar_kwargs={}, **kwargs):

    x = stda[xdim].values
    y = stda[ydim].values
    z = stda.stda.get_value(ydim, xdim)  # m/s

    cmap = cm_collected.get_cmap(cmap)
    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label=str(stda.level.values[0])+'hPa wind speed (m/s)', extend='max',**colorbar_kwargs)
    return img
    
@kwargs_wrapper
def tmpadv_contourf(ax, stda,  xdim='lon', ydim='lat',
                    add_colorbar=True, 
                    levels=np.arange(-10, 10.1, 1), cmap='ncl/BlueWhiteOrangeRed', extend='both',
                    transform=ccrs.PlateCarree(), alpha=0.8, colorbar_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # 1/s
    z = z * 1e4  # 1e-4/s
    z[np.abs(z)<1]=np.nan
    cmap = cm_collected.get_cmap(cmap,levels)

    img = ax.contourf(x, y, z, levels, cmap=cmap, alpha=alpha, transform=transform, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='temperature advection (10' + '$^{-4}$K*s$^{-1}$)',**colorbar_kwargs)
    return img


@kwargs_wrapper
def vortadv_contourf(ax, stda,  xdim='lon', ydim='lat',
                    add_colorbar=True, 
                    levels=np.arange(-10, 10.1, 0.5), cmap='ncl/BlueRed', extend='both',if_mask=True,
                    transform=ccrs.PlateCarree(), alpha=0.8, colorbar_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # 1/s
    z = z * 1e8  # 1e-8/s
    if if_mask:
        z[np.abs(z)<1]=np.nan
    cmap = cm_collected.get_cmap(cmap)
    img = ax.contourf(x, y, z, levels, cmap=cmap, alpha=alpha, transform=transform, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='vorticity advection (10' + '$^{-8}$s$^{-1}$)',extend=extend,**colorbar_kwargs)
    return img

@kwargs_wrapper
def vort_contourf(ax, stda,  xdim='lon', ydim='lat',
                    add_colorbar=True, 
                    levels=np.arange(2, 18, 2), cmap='Wistia', extend='max',
                    transform=ccrs.PlateCarree(), alpha=0.8, colorbar_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # 1/s
    z = z * 1e5  # 1e-5/s
    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label=str(stda.level.values[0])+'hPa vorticity (10' + '$^{-5}$s$^{-1}$)',**colorbar_kwargs)
    return img

@kwargs_wrapper
def div_contourf(ax, stda, xdim='lon', ydim='lat',
                 add_colorbar=True,
                 levels=np.arange(-10, -1), cmap='Blues_r', extend='min',
                 transform=ccrs.PlateCarree(), alpha=0.8,colorbar_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # 1/s
    z = z * 1e5  # 1e-5/s

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='divergence 10' + '$^{-5}$s$^{-1}$',extend=extend,**colorbar_kwargs)
    return img


@kwargs_wrapper
def prmsl_contourf(ax, stda, xdim='lon', ydim='lat',
                   add_colorbar=True,
                   levels=np.arange(960, 1065, 5), cmap='guide/cs26', extend='neither',
                   transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # hPa

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='mean sea level pressure (hPa)', extend='max')
    return img

@kwargs_wrapper
def pres_contourf(ax, stda, xdim='lon', ydim='lat',
                   add_colorbar=True,
                   levels=None, cmap='guide/cs26', extend='both',
                   transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # hPa

    if(levels==None):
        levels=np.arange(int(np.nanmin(z)),int(np.nanmax(z)),2.5)
        ticks=np.arange(int(np.nanmin(z)),int(np.nanmax(z)),int(int(int(np.nanmax(z))-int(np.nanmin(z)))/10)).tolist()
    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels, cmap=cmap, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=ticks, label='surface pressure (hPa)', extend=extend)
    return img

@kwargs_wrapper
def qpf_contourf(ax, stda,  xdim='lon', ydim='lat', valid_time=24,
                   add_colorbar=True,
                   transform=ccrs.PlateCarree(), alpha=1,levels=None,
                   **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm

    if levels is None:
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
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    z = np.where(z < 0.1, np.nan, z)
    img = ax.contourf(x, y, z, levels=levels, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='{}h precipitation (mm)'.format(valid_time), extend='max')

@kwargs_wrapper
def rain_contourf(ax, stda, xdim='lon', ydim='lat',
                  add_colorbar=True,
                  levels=[0.1, 4, 13, 25, 60, 120], cmap='met/rain', extend='max',
                  transform=ccrs.PlateCarree(), alpha=0.8, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm

    cmap = cm_collected.get_cmap(cmap)
    colors = cmap.colors

    img = ax.contourf(x, y, z, levels, colors=colors, transform=transform, alpha=alpha, extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='{}h precipitation (mm)'.format(stda.attrs['valid_time']), extend='max')
    return img


@kwargs_wrapper
def cross_absv_contourf(ax, stda, xdim='lon', ydim='level',
                        add_colorbar=True,
                        levels=np.arange(-36, 36+1, 4), cmap='ncl/BlueWhiteOrangeRed',
                        **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # 1/s
    z = z * 1e5  # 1e-5/s

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, extend='both',**kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Absolute Vorticity (dimensionless)',  orientation='vertical', extend='both', pos='right')
    return img


@kwargs_wrapper
def cross_rh_contourf(ax, stda, xdim='lon', ydim='level',
                      add_colorbar=True,
                      levels=np.arange(0, 101, 0.5), cmap=None,extend='max',
                      **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # percent

    if cmap is None:
        cmap = col.LinearSegmentedColormap.from_list('own2', ['#1E90FF','#94D8F6','#F1F1F1','#BFBFBF','#696969'])
    else:
        cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, extend=extend,**kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=[20, 40, 60, 80, 100], label='Relative Humidity',  orientation='vertical', extend=extend, pos='right')
    return img

@kwargs_wrapper
def cross_w_contourf(ax, stda, xdim='lon', ydim='level',
                        add_colorbar=True,
                        levels=np.arange(-0.5,0.51,0.05).tolist(), cmap='RdYlGn_r',
                        **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # m/s
    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap,extend='both', **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Vertical velocity (m/s)',  orientation='vertical', extend='both', pos='right')
    return img

@kwargs_wrapper
def cross_spfh_contourf(ax, stda, xdim='lon', ydim='level',
                        add_colorbar=True,
                        levels=np.arange(0, 20, 1), cmap='ncl/MPL_Greens',extend='max',
                        **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # g/kg

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap,extend=extend, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Specific Humidity (g/kg)',  orientation='vertical', extend=extend, pos='right')
    return img


@kwargs_wrapper
def cross_mpv_contourf(ax, stda, xdim='lon', ydim='level',
                       add_colorbar=True,
                       levels=np.arange(-10, 10, 1), cmap='ncl/cmp_flux',
                       **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # K*m**2/(s*kg)
    z = z * 1e6  # 1e-6*K*m**2/(s*kg)

    cmap = cm_collected.get_cmap(cmap)

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Moisture Potential Vorticity (10$^{-6}$ K*m**2/(s*kg))',
                         label_size=15, orientation='vertical', extend='max', pos='right')
    return img


@kwargs_wrapper
def cross_terrain_contourf(ax, stda, xdim='lon', ydim='level',
                           levels=np.arange(0, 500, 1), cmap=None,
                           **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)

    if cmap is None:
        startcolor = '#8B4513'  # 棕色
        endcolor = '#DAC2AD'  # 绿
        cmap = col.LinearSegmentedColormap.from_list('own3', [endcolor, startcolor])

    img = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
    return img
