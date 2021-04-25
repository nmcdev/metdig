
import numpy as np

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import metdig.graphics.lib.utl_plotmap as utl_plotmap

def cross_section_hgt(ax, hgt, levels=np.arange(500, 600, 4), cmap='inferno',
                      st_point=None, ed_point=None, lon_cross=None, lat_cross=None,
                      map_extent=(60, 145, 15, 55), h_pos=[0.125, 0.665, 0.25, 0.2]):
    x, y, z = hgt['lon'].values, hgt['lat'].values, hgt.values.squeeze()
    crs = ccrs.PlateCarree()
    if not h_pos:
        l, b, w, h = ax.get_position().bounds
        h_pos = [l, b + h - 0.22, 0.25, 0.2]
    # ax_inset = fig.add_axes(h_pos, projection=crs)
    ax_inset = plt.axes(h_pos, projection=crs)
    ax_inset.set_extent(map_extent, crs=crs)
    # Add geographic features
    ax_inset.coastlines()
    utl_plotmap.add_china_map_2cartopy_public(ax_inset, name='province', edgecolor='black', lw=0.8, zorder=105)
    # Set the titles and axes labels
    ax_inset.set_title('')

    # plot geopotential height at 500 hPa using xarray's contour wrapper
    # plot the path of the cross section
    ax_inset.contour(x, y, z, levels=levels, cmap='inferno')

    if st_point is not None and ed_point is not None:
        endpoints = crs.transform_points(ccrs.Geodetic(), *np.vstack([st_point, ed_point]).transpose()[::-1])
        ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)

    if lon_cross is None or lat_cross is None:
        if st_point is not None and ed_point is not None:
            ax_inset.plot(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
    else:
        ax_inset.plot(lon_cross, lat_cross, c='k', zorder=2)