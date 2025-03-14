import numpy as np
import xarray as xr

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.patheffects as mpatheffects
import matplotlib.lines as lines

import metdig.graphics.lib.utility as utl
import metdig.graphics.cmap.cm as cm_collected
from metdig.graphics.lib.utility import kwargs_wrapper


@kwargs_wrapper
def contour_2d(ax, stda, xdim='lon', ydim='lat',
               add_clabel=True, cb_fontsize=20, cb_fmt='%.0f', cb_colors='black', cb_level=None,
               levels=None, colors='black',
               transform=ccrs.PlateCarree(), linewidths=2,
               **kwargs):
    """[graphics层绘制contour平面图通用方法]

    Args:
        ax ([type]): [description]
        stda ([type]): [stda标准格式]
        xdim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lon'.
        ydim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lat'.
        add_clabel (bool, optional): [是否调用ax.clabel]. Defaults to True.
        cb_fontsize (int, optional): [clabel字体大小]. Defaults to None.
        cb_fmt (str, optional): [clabel字体格式]. Defaults to None.
        cb_colors (str, optional): [clabel字体颜色]. Defaults to None.
        cb_level (str, optional): [clabel标出的等值线数值，None表示所有等值线全标]. Defaults to None.
        levels (list, optional): [description]. Defaults to None.
        colors (str, optional): [description]. Defaults to 'black'.
        transform ([type], optional): [stda的投影类型，仅在xdim='lon' ydim='lat'时候生效]. Defaults to ccrs.PlateCarree().
        linewidths (int, optional): [description]. Defaults to 2.

    Returns:
        [type]: [绘图对象]
    """
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)

    if (transform is None) or (xdim != 'lon' and ydim != 'lat'):
        img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, **kwargs)
    else:
        img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)

    if add_clabel:
        cb_level = levels if cb_level is None else cb_level
        if cb_level is None:
            ax.clabel(img, inline=1, fontsize=cb_fontsize, fmt=cb_fmt, colors=cb_colors)
        else:
            ax.clabel(img, cb_level, inline=1, fontsize=cb_fontsize, fmt=cb_fmt, colors=cb_colors)
    
    return img


############################################################################################################################
# 以下为特殊方法，无法使用上述通用方法时在后面增加单独的方法
############################################################################################################################
@kwargs_wrapper
def spfh_contour(ax, stda,  xdim='lon', ydim='lat',
                add_clabel=True,
                levels= np.arange(8,20, 4),
                colors='yellow',
                transform=ccrs.PlateCarree(), linewidths=0.8,
                **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # dagpm

    img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        ax.clabel(img, inline=1, fontsize=13, fmt='%.0f', colors=colors)
    return img

@kwargs_wrapper
def ulj_contour(ax, stda,  xdim='lon', ydim='lat',
                add_clabel=True,
                levels= np.arange(35,85, 10),
                colors='yellow',
                transform=ccrs.PlateCarree(), linewidths=0.8,
                **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # dagpm

    img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        ax.clabel(img, inline=1, fontsize=13, fmt='%.0f', colors=colors)
    return img


@kwargs_wrapper
def rain_contour(ax, stda,  xdim='lon', ydim='lat',
                add_clabel=False,
                levels=[1,10,25,50,100,250],
                cmap='met/rain',
                transform=ccrs.PlateCarree(), linewidths=0.7,
                **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # dagpm
    cmap, norm = cm_collected.get_cmap(cmap, extend='max', levels=levels,isLinear=True)

    img = ax.contour(x, y, z, levels=levels, transform=transform, norm=norm, cmap=cmap, linewidths=linewidths, **kwargs)
    if add_clabel:
        ax.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors='black')
    return img

@kwargs_wrapper
def hgt_spaghetti_contour(ax, stda,  xdim='lon', ydim='lat',
        add_clabel=True,
        levels=[508,548,588],
        colors=['#F8A1A4','#6BD089','#60C5F1'],
        transform=ccrs.PlateCarree(), linewidths=2,
        **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    m = stda.stda.get_dim_value('member')
    
    img=[]
    for im in m:
        z=stda.sel(member=im).stda.get_value(ydim, xdim)
        img.append(ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs))
    
    #控制预报
    z=stda.isel(member=0).stda.get_value(ydim, xdim)
    img.append(ax.contour(x, y, z, levels=levels, transform=transform, colors='black', linewidths=linewidths,linestyles='dashed',label='控制预报', **kwargs))

    #集合平均
    z=stda.mean('member').stda.get_value(ydim, xdim)
    img.append(ax.contour(x, y, z, levels=levels, transform=transform, colors='black', linewidths=linewidths,label='集合平均', **kwargs))
    if add_clabel:
        ax.clabel(img[-1], inline=1, fontsize=20, fmt='%.0f', colors='black')

    return img

@kwargs_wrapper
def hgt_contour(ax, stda,  xdim='lon', ydim='lat',
                add_clabel=True,
                levels=np.append(np.append(np.arange(0, 480, 4), np.append(np.arange(480, 580, 4), np.arange(580, 604, 4))), np.arange(604, 2000, 8)),
                colors='black',
                transform=ccrs.PlateCarree(), linewidths=1.7,
                **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # dagpm

    img = ax.contour(x, y, z, levels=levels, transform=transform, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        ax.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors='black')
    return img

@kwargs_wrapper
def vort_contour(ax, stda, xdim='lon', ydim='lat',
               add_clabel=True,
               levels=np.arange(2, 18, 2), colors='black',
               transform=ccrs.PlateCarree(), linewidths=1, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)   # 1/s
    z = z * 1e5  # 1e-5/s

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        ax.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors=colors)
    return img

@kwargs_wrapper
def div_contour(ax, stda, xdim='lon', ydim='lat',
               add_clabel=True,
               levels=np.append(np.arange(-10, -4),np.arange(5,11)), colors='black',
               transform=ccrs.PlateCarree(), linewidths=1, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)   # 1/s
    z = z * 1e5  # 1e-5/s

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        ax.clabel(img, inline=1, fontsize=20, fmt='%.0f', colors=colors)
    return img

@kwargs_wrapper
def cape_contour(ax, stda, xdim='lon', ydim='lat',
               add_clabel=True,cb_fontsize=20,
               levels=np.arange(1000, 4100, 500), colors='red',
               transform=ccrs.PlateCarree(), linewidths=1,clabel_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        ax.clabel(img, inline=1, fontsize=cb_fontsize, fmt='%.0f', colors=colors)
    return img



@kwargs_wrapper
def pv_contour(ax, stda, xdim='lon', ydim='lat',
               add_clabel=True,cb_fontsize=20,
               levels=np.arange(3, 25, 2), colors='black',
               transform=ccrs.PlateCarree(), linewidths=1,clabel_kwargs={}, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)
    z = z * 1e6  # 1e-6*K*m**2/(s*kg)

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        ax.clabel(img, inline=1, fontsize=cb_fontsize, fmt='%.0f', colors=colors)
    return img


@kwargs_wrapper
def prmsl_contour(ax, stda, xdim='lon', ydim='lat',
                  add_clabel=True,
                  levels=np.arange(900, 1100, 2.5), colors='black',
                  transform=ccrs.PlateCarree(), linewidths=1, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # 'hPa'

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        ax.clabel(img, inline=1, fontsize=15, fmt='%.0f', colors=colors)
    return img


@kwargs_wrapper
def tmp_contour(ax, stda,  xdim='lon', ydim='lat',
                add_clabel=True,
                levels=[35, 37, 40], colors=['#FF8F00', '#FF6200', '#FF0000'],
                transform=ccrs.PlateCarree(), linewidths=2, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # degC

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, transform=transform, **kwargs)
    if add_clabel:
        cl = ax.clabel(img, inline=1, fontsize=15, fmt='%i', colors=colors)
        if cl is not None:
            for t in cl:
                t.set_path_effects([mpatheffects.Stroke(linewidth=2, foreground='white'), mpatheffects.Normal()])
    return img


@kwargs_wrapper
def dt2m_contour(ax, stda, xdim='lon', ydim='lat',
                 add_clabel=True,
                 levels=[-16, -12, -10, -8, -6, 6, 8, 10, 12, 16], cmap='ncl/BlRe',
                 transform=ccrs.PlateCarree(), alpha=0.5, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)  # degC

    cmap = cm_collected.get_cmap(cmap)
    cmap = cm_collected.linearized_cmap(cmap)

    img = ax.contour(x, y, z, levels=levels, cmap=cmap, transform=transform, alpha=alpha, vmin=-16, vmax=16, **kwargs)

    if add_clabel:
        clev_colors = []
        for iclev in levels:
            per_color = cm_collected.get_part_clev_and_cmap(cmap=cmap, clev_range=[-16, 16], clev_slt=iclev)
            clev_colors.append(np.squeeze(per_color[:]))
        cl = ax.clabel(img, inline=1, fontsize=15, fmt='%i', colors=clev_colors)
        if cl is not None:
            for t in cl:
                t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'), mpatheffects.Normal()])
    return img


@kwargs_wrapper
def cross_theta_contour(ax, stda, xdim='lon', ydim='level',
                        add_clabel=True, 
                        levels=np.arange(200, 450, 4), colors='black',
                        linewidths=2, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # kelvin

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        ax.clabel(img, fontsize=17, colors=colors, inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
    return img

@kwargs_wrapper
def cross_fg_contour(ax, stda, xdim='lon', ydim='level',
                        add_clabel=True, 
                        levels=np.arange(1,100,1), colors='blue',
                        linewidths=2, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)
    z = z * 1e9

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        ax.clabel(img, fontsize=17, colors=colors, inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
    return img

@kwargs_wrapper
def cross_wsp_contour(ax, stda, xdim='lon', ydim='level',
                        add_clabel=True, 
                        levels=np.arange(0,100,2), colors='blue',
                        linewidths=2, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # kelvin

    img = ax.contour(x, y, z, levels=levels, colors=colors, linewidths=linewidths, **kwargs)
    if add_clabel:
        ax.clabel(img, fontsize=17, colors=colors, inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
    return img

@kwargs_wrapper
def cross_tmp_contour(ax, stda, xdim='lon', ydim='level', 
                      add_clabel=True, 
                      levels=np.arange(-100, 100, 2), colors='#0A1F5D', linewidths=1, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # degC

    # 颜色统一
    single_color = '#0A1F5D'
    if isinstance(colors, str):
        single_color = colors

    img = ax.contour(x, y, z, levels=levels, colors=colors,linewidths=linewidths, **kwargs)
    if add_clabel:
        ax.clabel(img, fontsize=17, colors=single_color, inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
    
    if z.min() < 0 and z.max() > 0:
        img = ax.contour(x, y, z, levels=[0], colors=single_color, linewidths=linewidths+2)
        if add_clabel:
            ax.clabel(img, [0], fontsize=22, colors=single_color, inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
    return img


@kwargs_wrapper
def cross_spfh_contour(ax, stda, xdim='lon', ydim='level',
                        add_clabel=True, cmap='ncl/WhiteBlue',
                        levels=np.arange(0, 20, 2), 
                        linewidths=2, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) 
    
    cmap, norm = cm_collected.get_cmap(cmap, levels=np.arange(0, 20, 2), isLinear=True)

    img = ax.contour(x, y, z, levels=levels, cmap=cmap, norm=norm, linewidths=linewidths, **kwargs)
    if add_clabel:
        ax.clabel(img, levels, fontsize=17, colors='black', inline=1, inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)
    return img

@kwargs_wrapper
def cross_vvel_contour(ax, stda, xdim='lon', ydim='level', 
                      add_clabel=True, cmap='ncl/MPL_YlGn_r',
                      levels=np.arange(-3,0,0.2).tolist(), linewidths=1, **kwargs):
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim) # degC
    cmap, norm = cm_collected.get_cmap(cmap, extend='min', levels=levels,isLinear=True)

    # 上升运动为虚线，下沉运动为实线
    # 上升运动为负值，下沉运动为正值
    # dashed虚线，solid实线
    if max(levels) <= 0.001:
        linestyles = 'dashed' # 全为虚线
    elif min(levels) >= 0.001:
        linestyles = 'solid' # 全为实线
    else:
        linestyles = []
        for level in levels:
            if level <= 0.001: # 有正有负，0归类到虚线
                linestyles.append('dashed')
            else:
                linestyles.append('solid')

    img = ax.contour(x, y, z, levels=levels, cmap=cmap,linewidths=linewidths,linestyles=linestyles, **kwargs)

    if add_clabel:
        ax.clabel(img, fontsize=10, inline=1, inline_spacing=8, fmt='%.1f', rightside_up=True, use_clabeltext=True)
    return img
