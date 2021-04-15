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
    x = ustda['lon'].values
    y = ustda['lat'].values
    u = ustda.values.squeeze()
    v = vstda.values.squeeze()
    # 绘制
    img = ax.quiver(x, y, u, v, color=color, transform=transform,scale=scale,  regrid_shape=regrid_shape,  **kwargs)
