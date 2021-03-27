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


def uv_barbs(ax, uvstda, color='black', transform=ccrs.PlateCarree(), length=6, regrid_shape=20, fill_empty=False, sizes=dict(emptybarb=0.05), **kwargs):
    # 数据准备
    ustda = uvstda[0]
    vstda = uvstda[1]
    x = ustda['lon'].values
    y = ustda['lat'].values
    u = ustda.values.squeeze() * 2.5
    v = vstda.values.squeeze() * 2.5
    u, u_units = numpy_units_convert(u, ustda.attrs['var_units'], 'm/s')  # 转换成绘图所需单位
    v, v_units = numpy_units_convert(v, vstda.attrs['var_units'], 'm/s')  # 转换成绘图所需单位

    # 绘制
    img = ax.barbs(x, y, u, v, color=color, transform=transform, length=length, regrid_shape=regrid_shape, fill_empty=fill_empty, sizes=sizes, **kwargs)
    return img, None, u_units
