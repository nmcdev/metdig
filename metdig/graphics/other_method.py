
import numpy as np

import matplotlib as mpl
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import metdig.graphics.lib.utl_plotmap as utl_plotmap
from  metdig.graphics.lib.utility import kwargs_wrapper

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
    utl_plotmap.add_china_map_2cartopy_public(ax_inset, name='province', edgecolor='black', lw=0.8, zorder=105, crs=ccrs.PlateCarree())
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
    return ax_inset

@kwargs_wrapper
def cross_section_rain(ax, rain, times, title='', title_loc='right', title_fontsize=25, reverse_time=True, xtickfmt='%m月%d日%H时'):
    
    l, b, w, h = ax.get_position().bounds
    ax_inset = plt.axes([l, b - h*0.7 - 0.15, w, h * 0.7])

    if not title:
        title = f"过去{rain.attrs['valid_time']}小时降水"
    ax_inset.set_title(title, loc=title_loc, fontsize=title_fontsize)

    xstklbls = mpl.dates.DateFormatter(xtickfmt)
    ax_inset.xaxis.set_major_formatter(xstklbls)
    for label in ax_inset.get_xticklabels():
        label.set_rotation(30)
        label.set_fontsize(15)
        label.set_horizontalalignment('right')
    #要放到以上get_xtcklabels之后，否则get_xticklabels会失效，原因未明
    utl_plotmap.time_ticks_formatter(ax_inset, times)

    for label in ax_inset.get_yticklabels():
        label.set_fontsize(15)

    ax_inset.set_ylabel(f"降水量/mm", fontsize=15)
    ax_inset.set_xlim(times[0], times[len(times) - 1])

    rain = rain.where(rain >= 0 , 0)  # 无效值赋值成0
    ax_inset.set_ylim(ymin=0, ymax=rain.values.max()*1.1)

    # ax_inset绘制x轴为时间的柱状图
    ax_inset.bar(rain.stda.fcst_time, rain.values.squeeze(), width=0.1, color='b', align='center')

    if(reverse_time):
        # 反转x轴
        ax_inset.invert_xaxis()

    return ax_inset
