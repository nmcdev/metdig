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
def barbs_2d(ax, ustda, vstda, xdim='lon', ydim='lat',
             transform=ccrs.PlateCarree(), regrid_shape=20,
             color='black', length=6, fill_empty=False, sizes=dict(emptybarb=0.05),barb_increments={'half': 2, 'full': 4, 'flag': 20},
             **kwargs):
    """[graphics层绘制bars平面图通用方法]

    Args:
        ax ([type]): [description]
        ustda ([type]): [u矢量 stda标准格式]
        vstda ([type]): [v矢量 stda标准格式]
        xdim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lon'.
        ydim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lat'.
        transform ([type], optional): [stda的投影类型，仅在xdim='lon' ydim='lat'时候生效]. Defaults to ccrs.PlateCarree().
        regrid_shape (int, optional): [cartopy下独有的参数，仅在ax的transform存在的情况下生效]. Defaults to 20.
        color (str, optional): [description]. Defaults to 'black'.
        length (int, optional): [description]. Defaults to 6.
        fill_empty (bool, optional): [description]. Defaults to False.
        sizes ([type], optional): [description]. Defaults to dict(emptybarb=0.05).

    Returns:
        [type]: [绘图对象]
    """    
    x = ustda.stda.get_dim_value(xdim)
    y = ustda.stda.get_dim_value(ydim)
    u = ustda.stda.get_value(ydim, xdim) * 2.5
    v = vstda.stda.get_value(ydim, xdim) * 2.5

    if regrid_shape is None or transform is None or (xdim != 'lon' or ydim != 'lat'):
        # matplotlib
        img = ax.barbs(x, y, u, v, color=color, length=length,  fill_empty=fill_empty, sizes=sizes, barb_increments=barb_increments,**kwargs)
    else:
        # cartopy 含transform，regrid_shape的两个参数
        img = ax.barbs(x, y, u, v, transform=transform, regrid_shape=regrid_shape,barb_increments=barb_increments,
                       color=color, length=length,  fill_empty=fill_empty, sizes=sizes, **kwargs)
    
    return img

############################################################################################################################
# 以下为特殊方法，无法使用上述通用方法时在后面增加单独的方法
############################################################################################################################

@kwargs_wrapper
def uv_barbs(ax, ustda, vstda, color='black', transform=ccrs.PlateCarree(),
             length=6, regrid_shape=20, fill_empty=False, sizes=dict(emptybarb=0.05),
             **kwargs):
    # 数据准备
    x = ustda['lon'].values
    y = ustda['lat'].values
    u = ustda.values.squeeze() * 2.5
    v = vstda.values.squeeze() * 2.5

    # 绘制
    img = ax.barbs(x, y, u, v, color=color, transform=transform, length=length,
                   regrid_shape=regrid_shape, fill_empty=fill_empty, sizes=sizes, **kwargs)
    return img