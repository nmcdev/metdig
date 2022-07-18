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
def pcolormesh_2d(ax, stda, xdim='lon', ydim='lat',
                  add_colorbar=True, cb_pos='bottom', cb_ticks=None, cb_label=None,
                  levels=None, cmap='jet', extend='both',isLinear=False,
                  transform=ccrs.PlateCarree(), alpha=0.5,
                  colorbar_kwargs={}, **kwargs):
    """[graphics层绘制pcolormesh平面图通用方法]

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
        alpha (float, optional): [description]. Defaults to 0.5.

    Returns:
        [type]: [绘图对象]
    """
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)

    cmap, norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels,isLinear=isLinear)

    if transform is None or (xdim != 'lon' and ydim != 'lat'):
        img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, alpha=alpha, **kwargs)
    else:
        img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)

    if add_colorbar:
        try:
            cb_label = '{}({})'.format(stda.attrs['var_cn_name'], stda.attrs['var_units']) if not cb_label else cb_label
        except:
            print('输入变量请添加"var_cn_name"属性和"var_units"属性')
        utl.add_colorbar(ax, img, ticks=cb_ticks, pos=cb_pos, extend=extend, label=cb_label, kwargs=colorbar_kwargs)
    
    return img


############################################################################################################################
# 以下为特殊方法，无法使用上述通用方法时在后面增加单独的方法
############################################################################################################################
@kwargs_wrapper
def ulj_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                   add_colorbar=True, levels = np.arange(40,120,10),cmap=['#99E3FB', '#47B6FB','#0F77F7','#AC97F5','#A267F4','#9126F5','#E118F3'],
                   transform=ccrs.PlateCarree(), alpha=0.5, colorbar_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # m/s

    cmap, norm = cm_collected.get_cmap(name=cmap, extend='neither', levels=levels)
    if list(levels):
        z = np.where(z >= levels[0], z, np.nan)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Wind Speed (m/s)', extend='max',kwargs=colorbar_kwargs)
    return img

@kwargs_wrapper
def vvel_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                    add_colorbar=True,
                    levels=[-30, -20, -10, -5, -2.5, -1, -0.5, 0.5, 1, 2.5, 5, 10, 20, 30], cmap='met/vertical_velocity_nws',
                    transform=ccrs.PlateCarree(), alpha=0.7,colorbar_kwargs={}, 
                    **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # Pa/s
    z = z * 10  # 0.1*Pa/s
    z[np.abs(z)<0.5]=np.nan
    cmap, norm = cm_collected.get_cmap(cmap, extend='both', levels=levels)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, ticks=levels, label='Vertical Velocity (0.1*Pa/s)', extend='max',kwargs=colorbar_kwargs)
    return img

@kwargs_wrapper
def cape_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                     add_colorbar=True,
                     levels=np.arange(600, 4100, 200), cmap='ncl/MPL_YlOrRd',
                     transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={}, 
                     **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # K

    if levels is not None:
        z = np.where(z >= levels[0], z, np.nan)

    cmap, norm = cm_collected.get_cmap(cmap, extend='max', levels=levels)

    img = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='CAPE (J/kg)', extend='max',kwargs=colorbar_kwargs)
    return img

@kwargs_wrapper
def theta_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                     add_colorbar=True,
                     levels=np.arange(300, 365, 1), cmap='met/theta',
                     transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={}, 
                     **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # K

    cmap, norm = cm_collected.get_cmap(cmap, extend='both', levels=levels)

    img = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Theta-E (K)',kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def tmp_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                   add_colorbar=True,
                   cmap='met/temp',
                   transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={}, 
                   **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # degC

    cmap = cm_collected.get_cmap(cmap)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Temperature (°C)',kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def wsp_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                   add_colorbar=True,
                   levels=[12, 15, 18, 21, 24, 27, 30], cmap='met/wsp',
                   transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={},
                   **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # m/s

    cmap, norm = cm_collected.get_cmap(cmap, extend='max', levels=levels)
    if levels is not None:
        z = np.where(z >= levels[0], z, np.nan)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Wind Speed (m/s)', extend='max',kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def tcwv_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                    add_colorbar=True,
                    levels=np.concatenate((np.arange(25), np.arange(26, 84, 2))), cmap='met/precipitable_water_nws',
                    transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={},extend='max',
                    **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm

    cmap, norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='total column water(mm)', extend=extend,kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def rh_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                  add_colorbar=True,
                  levels=[0, 1, 5, 10, 20, 30, 40, 50, 60, 65, 70, 75, 80, 85, 90, 99], cmap='met/relative_humidity_nws',extend='max',
                  transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={},
                  **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # percent

    cmap, norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels)
    # cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='(%)', extend=extend,kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def spfh_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                    add_colorbar=True,
                    levels=np.arange(2, 24, 0.5), cmap='met/specific_humidity_nws',
                    transform=ccrs.PlateCarree(), alpha=0.8,colorbar_kwargs={},
                    **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # g/kg

    cmap, norm = cm_collected.get_cmap(cmap, extend='both', levels=levels)

    img = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Specific Humidity (g/kg)',kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def fg_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                  add_colorbar=True,
                  levels = np.arange(-4, 4.5,0.5).tolist(), cmap='ncl/hotcolr_19lev',
                  transform=ccrs.PlateCarree(), alpha=0.8,colorbar_kwargs={},
                  **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # kelvin/m/s
    z = z * 1e9  
    z[np.abs(z)<0.5]=np.nan
    cmap, norm = cm_collected.get_cmap(cmap, extend='both', levels=levels)

    img = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm, transform=transform, alpha=alpha,**kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Front Genesis Function (1${0^{-8}}$K*s${^{-1}}$ m${^{-1}}$)', extend='both',kwargs=colorbar_kwargs)
    return img
            

@kwargs_wrapper
def wvfl_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                    add_colorbar=True,
                    levels=np.arange(5, 46).tolist(), cmap='met/wvfl_ctable',
                    transform=ccrs.PlateCarree(), alpha=0.8,colorbar_kwargs={},
                    **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # g/(cm*hPa*s)

    cmap, norm = cm_collected.get_cmap(cmap, extend='max', levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    if levels:
        z = np.where(z >= levels[0], z, np.nan)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='Water Vapor Flux g/(cm*hPa*s)', extend='max',kwargs=colorbar_kwargs)
    return img

@kwargs_wrapper
def wvfldiv_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                    add_colorbar=True,
                    levels=np.arange(-10, 0, 0.5).tolist(), extend='min',cmap='Greens_r',
                    transform=ccrs.PlateCarree(), alpha=0.8,colorbar_kwargs={},
                    **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)*100000  # 10**4 g/(m**2*Pa*s)

    cmap, norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels)
    cmap.set_under(color=[0, 0, 0, 0], alpha=0.0)

    if levels:
        z = np.where(z >= levels[0], z, np.nan)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='水汽通量散度 10$^{-5}$ g/(m**2*Pa*s)', extend=extend,kwargs=colorbar_kwargs)
    return img

@kwargs_wrapper
def tmp_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                   add_colorbar=True,
                   cmap='met/temp',levels = np.arange(-45, 46,1),extend='both',
                   transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={},
                   **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # degC

    cmap, norm = cm_collected.get_cmap(cmap, extend='both', levels=levels)

    img = ax.pcolormesh(x, y, z, cmap=cmap,norm=norm, transform=transform, alpha=alpha,  **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='°C', extend='both',kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def gust_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                    add_colorbar=True,
                    cmap='met/wind_speed_nws',
                    levels =[1.6,3.4,5.5,8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7, 37, 41.5, 46.2, 51.0, 56.1, 61.3],
                    transform=ccrs.PlateCarree(), alpha=1,colorbar_kwargs={},level_drop=7.9,
                    **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # m/s
    
    cmap,norm = cm_collected.get_cmap(cmap,extend='max', levels=levels)

    z = np.where(z < level_drop, np.nan, z)

    img = ax.pcolormesh(x, y, z, cmap=cmap,norm=norm, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        ticks = levels
        utl.add_colorbar(ax, img, ticks=ticks, label='风速 (m/s)', extend='max',kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def dt2m_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                    add_colorbar=True, levels=np.arange(-16,17,1),
                    cmap='ncl/hotcold_18lev',
                    transform=ccrs.PlateCarree(), alpha=1,colorbar_kwargs={},
                    **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # degC
    z[np.abs(z)<4]=np.nan
    cmap,norm = cm_collected.get_cmap(cmap, extend='neither', levels=levels,isLinear=True)
    # cmap = cm_collected.linearized_cmap(cmap)

    img = ax.pcolormesh(x, y, z, cmap=cmap, transform=transform, alpha=alpha, norm=norm, **kwargs)
    if add_colorbar:
        ticks = [-16, -12, -10, -8, -6, -4, 0, 4, 6, 8, 10, 12, 16]
        utl.add_colorbar(ax, img, ticks=ticks, label='°C', extend='both',kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def qpf_pcolormesh(ax, stda,  xdim='lon', ydim='lat', valid_time=24,
                   add_colorbar=True,
                   transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={},
                   **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm

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
    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='{}h precipitation (mm)'.format(valid_time), extend='max',kwargs=colorbar_kwargs)
    return img


@kwargs_wrapper
def rain_snow_sleet_pcolormesh(ax, rain_snow_sleet_stdas,  xdim='lon', ydim='lat', valid_time=24,
                               add_colorbar=True,
                               transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={},
                               **kwargs):
    # 雨
    stda = rain_snow_sleet_stdas[0]
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm

    if valid_time == 24:
        levels = [0.1, 10, 25, 50, 100, 250]
    elif valid_time == 6:
        levels = [0.1, 4, 13, 25, 60, 120]
    else:
        levels = [0.01, 2, 7, 13, 30, 60]
    cmap, norm = cm_collected.get_cmap('met/rain_nws', extend='max', levels=levels)

    imgrain = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        l, b, w, h = ax.get_position().bounds
        utl.add_colorbar(ax, imgrain, label='雨 (mm)', rect=[l + w * 0.7, b - 0.04, w * 0.30, .02], extend='max',kwargs=colorbar_kwargs)

    # 雪
    stda = rain_snow_sleet_stdas[1]
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm

    if valid_time == 24:
        levels = [0.1, 2.5, 5, 10, 20, 30]
    elif valid_time == 6:
        levels = [0.1, 1, 3, 5, 10, 15]
    else:
        levels = [0.1, 1, 2, 4, 8, 12]
    cmap, norm = cm_collected.get_cmap('met/snow_nws', extend='neither', levels=levels)

    imgsnow = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        l, b, w, h = ax.get_position().bounds
        utl.add_colorbar(ax, imgsnow, label='雪 (mm)', rect=[l + w * 0.33, b - 0.04, w * 0.30, .02], extend='max',kwargs=colorbar_kwargs)

    # 雨夹雪
    stda = rain_snow_sleet_stdas[2]
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm

    if valid_time == 24:
        levels = [0.1, 10, 25, 50, 100, 250]
    elif valid_time == 6:
        levels = [0.1, 4, 13, 25, 60, 120]
    else:
        levels = [0.1, 2, 7, 13, 30, 60]
    cmap, norm = cm_collected.get_cmap('met/sleet_nws', extend='neither', levels=levels)

    imgsleet = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, imgsleet, label='雨夹雪 (mm)', rect=[l, b - 0.04, w * 0.30, .02], extend='max',kwargs=colorbar_kwargs)
    return imgrain, imgsnow, imgsleet


@kwargs_wrapper
def ir_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                  add_colorbar=True,
                  levels=np.arange(160, 301), cmap='met/wv_enhancement',
                  transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={},
                  **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm

    cmap, norm = cm_collected.get_cmap(cmap, extend='max', levels=levels, isLinear=True)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='(K)', extend='max', kwargs=colorbar_kwargs)
    return img
        
@kwargs_wrapper
def cref_pcolormesh(ax, stda, xdim='lon', ydim='lat',
                  add_colorbar=True,
                  levels=[10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70], 
                  transform=ccrs.PlateCarree(), alpha=0.5,colorbar_kwargs={},
                  **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # mm
    z[z<15]=np.nan
    colors = ['#01A0F6', '#00ECEC', '#00D800', '#019000', '#FFFF00', '#E7C000', '#FF9000', '#FF0000', '#D60000', '#D60000', '#FF00F0', '#9600B4', '#AD90F0']
    cmap, norm = cm_collected.get_cmap(colors, extend='max', levels=levels)

    img = ax.pcolormesh(x, y, z, norm=norm, cmap=cmap, transform=transform, alpha=alpha, **kwargs)
    if add_colorbar:
        utl.add_colorbar(ax, img, label='(dbz)',extend='max', kwargs=colorbar_kwargs)
    return img