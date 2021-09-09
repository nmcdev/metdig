import numpy as np
import cartopy.crs as ccrs
import matplotlib.patheffects as path_effects

import metdig.graphics.lib.utl_plotmap as utl_plotmap
import metdig.graphics.lib.utility as  utl
from  metdig.graphics.lib.utility import kwargs_wrapper

@kwargs_wrapper
def add_extrema(ax, stda, transform=ccrs.PlateCarree(), size=20,zorder=12, color='red',va='bottom',ha='right',**kwargs):
    extrema=stda.where(stda==stda.max(),drop=True)
    img = ax.text(extrema.lon,extrema.lat,
                'Max: '+'%.1f' % np.squeeze(extrema.values),
                family='SimHei',size=size, transform=transform,zorder=zorder,color=color,va=va,ha=ha, **kwargs)
    img.set_path_effects([path_effects.Stroke(linewidth=3, foreground='#D9D9D9'),
                        path_effects.Normal()])
    img2 = ax.scatter(extrema.lon,extrema.lat,s=size, color=color, transform=transform,zorder=zorder, **kwargs)
    img2.set_path_effects([path_effects.Stroke(linewidth=3, foreground='#D9D9D9'),
                        path_effects.Normal()])

def city_text(ax, stda, transform=ccrs.PlateCarree(), alpha=1, size=13, **kwargs):
    utl_plotmap.add_city_values_on_map(ax, stda, alpha=alpha, size=size, **kwargs)


def mslp_highlower_center_text(ax, stda, map_extent, transform=ccrs.PlateCarree()):
    x, y = np.meshgrid(stda['lon'].values, stda['lat'].values)
    res = stda['lon'].values[1] - stda['lon'].values[0]
    nwindow = int(9.5 / res)
    mslp_hl = np.ma.masked_invalid(stda.values).squeeze()
    local_min, local_max = utl.extrema(mslp_hl, mode='wrap', window=nwindow)
    # Get location of extrema on grid
    xmin, xmax, ymin, ymax = map_extent
    lons2d, lats2d = x, y
    transformed = transform.transform_points(transform, lons2d, lats2d)
    x = transformed[..., 0]
    y = transformed[..., 1]
    xlows = x[local_min]
    xhighs = x[local_max]
    ylows = y[local_min]
    yhighs = y[local_max]
    lowvals = mslp_hl[local_min]
    highvals = mslp_hl[local_max]
    yoffset = 0.022*(ymax-ymin)
    dmin = yoffset
    # Plot low pressures
    xyplotted = []
    for x, y, p in zip(xlows, ylows, lowvals):
        if x < xmax-yoffset and x > xmin+yoffset and y < ymax-yoffset and y > ymin+yoffset:
            dist = [np.sqrt((x-x0)**2+(y-y0)**2) for x0, y0 in xyplotted]
            if not dist or min(dist) > dmin:  # ,fontweight='bold'
                a = ax.text(x, y, 'L', fontsize=28, zorder=200,
                            ha='center', va='center', color='r', fontweight='normal', transform=transform)
                b = ax.text(x, y-yoffset, repr(int(p)), fontsize=14, zorder=200,
                            ha='center', va='top', color='r', fontweight='normal', transform=transform)
                a.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground='black'),
                                    path_effects.SimpleLineShadow(), path_effects.Normal()])
                b.set_path_effects([path_effects.Stroke(linewidth=1.0, foreground='black'),
                                    path_effects.SimpleLineShadow(), path_effects.Normal()])
                xyplotted.append((x, y))

    # Plot high pressures
    xyplotted = []
    for x, y, p in zip(xhighs, yhighs, highvals):
        if x < xmax-yoffset and x > xmin+yoffset and y < ymax-yoffset and y > ymin+yoffset:
            dist = [np.sqrt((x-x0)**2+(y-y0)**2) for x0, y0 in xyplotted]
            if not dist or min(dist) > dmin:
                a = ax.text(x, y, 'H', fontsize=28, zorder=200,
                            ha='center', va='center', color='b', fontweight='normal', transform=transform)
                b = ax.text(x, y-yoffset, repr(int(p)), fontsize=14, zorder=200,
                            ha='center', va='top', color='b', fontweight='normal', transform=transform)
                a.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground='black'),
                                    path_effects.SimpleLineShadow(), path_effects.Normal()])
                b.set_path_effects([path_effects.Stroke(linewidth=1.0, foreground='black'),
                                    path_effects.SimpleLineShadow(), path_effects.Normal()])
                xyplotted.append((x, y))
