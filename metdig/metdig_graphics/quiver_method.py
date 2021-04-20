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
from  metdig.metdig_graphics.lib.utility import kwargs_wrapper

@kwargs_wrapper
def uv_quiver(ax, ustda, vstda,xdim='lon', ydim='lat', 
             color='black',scale=1000,
             transform=ccrs.PlateCarree(), regrid_shape=30, 
             **kwargs):
    # 数据准备
    x = ustda.stda.get_dim_value(xdim)
    y = ustda.stda.get_dim_value(ydim)
    u = ustda.stda.get_2d_value(ydim, xdim)  # 1/s
    v = vstda.stda.get_2d_value(ydim, xdim)  # 1/s
    # 绘制
    if regrid_shape is None or transform is None or (xdim != 'lon' and ydim != 'lat'):
        img = ax.quiver(x, y, u, v, color=color, scale=scale,  **kwargs)
    else:
        img = ax.quiver(x, y, u, v, color=color, transform=transform, scale=scale,  regrid_shape=regrid_shape,  **kwargs)
