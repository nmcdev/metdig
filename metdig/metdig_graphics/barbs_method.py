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


def barbs_2d(ax, ustda, vstda, xdim='lon', ydim='lat', draw_units='',
          transform=ccrs.PlateCarree(), regrid_shape=20,
          color='black', length=6, fill_empty=False, sizes=dict(emptybarb=0.05),
          **kwargs):
    """[graphics层绘制bars平面图通用方法]

    Args:
        ax ([type]): [description]
        ustda ([type]): [u矢量 stda标准格式]
        vstda ([type]): [v矢量 stda标准格式]
        xdim (str, optional): [绘图时x维度名称，从以下stda维度名称中选择一个填写: member, level, time dtime, lat, lon]. Defaults to 'lon'.
        ydim (str, optional): [绘图时y维度名称，从以下stda维度名称中选择一个填写: member, level, time dtime, lat, lon]. Defaults to 'lat'.
        draw_units (str, optional): [绘图时单位]. Defaults to ''.
        transform ([type], optional): [description]. Defaults to ccrs.PlateCarree().
        regrid_shape (int, optional): [description]. Defaults to 20.
        color (str, optional): [description]. Defaults to 'black'.
        length (int, optional): [description]. Defaults to 6.
        fill_empty (bool, optional): [description]. Defaults to False.
        sizes ([type], optional): [description]. Defaults to dict(emptybarb=0.05).
    """    
    x = ustda[xdim].values
    y = ustda[ydim].values
    u = ustda.squeeze().transpose(ydim, xdim).values * 2.5
    v = vstda.squeeze().transpose(ydim, xdim).values * 2.5
    u, u_units = numpy_units_convert(u, ustda.attrs['var_units'], draw_units)  # 转换成绘图所需单位
    v, v_units = numpy_units_convert(v, vstda.attrs['var_units'], draw_units)  # 转换成绘图所需单位
    
    if regrid_shape is None or transform is None:
        # matplotlib 
        img = ax.barbs(x, y, u, v, color=color, length=length,  fill_empty=fill_empty, sizes=sizes, **kwargs)
    else:
        # cartopy 含transform，regrid_shape的两个参数
        img = ax.barbs(x, y, u, v, transform=transform, regrid_shape=regrid_shape,
                   color=color, length=length,  fill_empty=fill_empty, sizes=sizes, **kwargs)

############################################################################################################################
#####以下为特殊方法，无法使用上述通用方法时在后面增加单独的方法
############################################################################################################################

def uv_barbs(ax, ustda, vstda, color='black', transform=ccrs.PlateCarree(),
             length=6, regrid_shape=20, fill_empty=False, sizes=dict(emptybarb=0.05),
             **kwargs):
    # 数据准备
    x = ustda['lon'].values
    y = ustda['lat'].values
    u = ustda.values.squeeze() * 2.5
    v = vstda.values.squeeze() * 2.5
    u, u_units = numpy_units_convert(u, ustda.attrs['var_units'], 'm/s')  # 转换成绘图所需单位
    v, v_units = numpy_units_convert(v, vstda.attrs['var_units'], 'm/s')  # 转换成绘图所需单位

    # 绘制
    img = ax.barbs(x, y, u, v, color=color, transform=transform, length=length,
                   regrid_shape=regrid_shape, fill_empty=fill_empty, sizes=sizes, **kwargs)
