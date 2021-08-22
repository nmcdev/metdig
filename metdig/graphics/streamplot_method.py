import numpy as np

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.patheffects as mpatheffects

import metdig.graphics.lib.utility as utl
import metdig.graphics.lib.utl_plotmap as utl_plotmap
import metdig.graphics.cmap.cm as cm_collected
from  metdig.graphics.lib.utility import kwargs_wrapper

@kwargs_wrapper
def uv_streamplot(ax, ustda, vstda,xdim='lon', ydim='lat', 
             color='gray',density=2,
             transform=ccrs.PlateCarree(), 
             **kwargs):
    # 数据准备
    x = ustda.stda.get_dim_value(xdim)
    y = ustda.stda.get_dim_value(ydim)
    u = ustda.stda.get_value(ydim, xdim)  # 1/s
    v = vstda.stda.get_value(ydim, xdim)  # 1/s
    # 绘制
    if transform is None or (xdim != 'lon' and ydim != 'lat'):
        img = ax.streamplot(x, y, u, v, color=color,density=density, **kwargs)
    else:
        img = ax.streamplot(x, y, u, v, color=color,density=density, transform=transform, **kwargs)
    return img
