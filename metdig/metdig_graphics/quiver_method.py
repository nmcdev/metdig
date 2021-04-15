import numpy as np

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.patheffects as mpatheffects

import metdig.metdig_graphics.lib.utility as utl
import metdig.metdig_graphics.lib.utl_plotmap as utl_plotmap
import metdig.metdig_graphics.cmap.cm as cm_collected

from metdig.metdig_utl import numpy_units_convert

def uv_quiver(ax, uvstda,color='black',scale=2500,
             transform=ccrs.PlateCarree(), regrid_shape=30, 
             **kwargs):
    ustda = uvstda[0]
    vstda = uvstda[1]
    x = ustda['lon'].values
    y = ustda['lat'].values
    u = ustda.values.squeeze() * 2.5
    v = vstda.values.squeeze() * 2.5
    u, u_units = numpy_units_convert(u, ustda.attrs['var_units'], 'm/s')  # 转换成绘图所需单位
    v, v_units = numpy_units_convert(v, vstda.attrs['var_units'], 'm/s')  # 转换成绘图所需单位

    # 绘制
    img = ax.quiver(x, y, u, v, color=color, transform=transform,scale=scale,  regrid_shape=regrid_shape,  **kwargs)
