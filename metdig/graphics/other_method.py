
import numpy as np

import matplotlib as mpl
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import metdig.graphics.lib.utl_plotmap as utl_plotmap
from  metdig.graphics.lib.utility import kwargs_wrapper


def cross_section_hgt(ax, hgt, levels=np.arange(500, 600, 4), cmap='inferno',
                      st_point=None, ed_point=None, lon_cross=None, lat_cross=None,
                      map_extent=(70, 145, 15, 55), h_pos=None):

    x, y, z = hgt['lon'].values, hgt['lat'].values, hgt.values.squeeze()
    crs = ccrs.PlateCarree()
    if not h_pos:
        # h_pos为空，则固定自动计算显示到左上角
        l, b, w, h = ax.get_position().bounds
        # h_pos = [l, b + h - 0.22, 0.25, 0.2]
        map_width = map_extent[1] - map_extent[0]
        map_height = map_extent[3] - map_extent[2]
        if map_width > map_height:
            width_inset = 0.25
            height_inset = width_inset * map_height / map_width
            xpad = -0.02 # ?遗留问题，正常逻辑是加上l+pad，可能是matplotlib自适应引起的
        else:
            height_inset = 0.25
            width_inset = height_inset * map_width / map_height
            xpad = 0.02 # ?遗留问题，正常逻辑是加上l+pad，可能是matplotlib自适应引起的
        ypad = 0.01
        h_pos = [l + xpad, b + h - height_inset - ypad, width_inset, height_inset]

    # ax_inset = fig.add_axes(h_pos, projection=crs)
    ax_inset = ax.get_figure().add_axes(h_pos, projection=crs)
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
        # endpoints = crs.transform_points(ccrs.Geodetic(), *np.vstack([st_point, ed_point]).transpose()[::-1])

        # 支持多点的情况
        st = np.array(st_point).reshape(-1, 2) # [[lat, lon]]
        ed = np.array(ed_point).reshape(-1, 2) # [[lat, lon]]
        endpoints = np.vstack([st, ed[-1, :].reshape(-1, 2)]) # [[lat, lon]]
        endpoints = crs.transform_points(ccrs.Geodetic(), endpoints[:, 1], endpoints[:, 0])
        for i, (plon, plat, _) in enumerate(endpoints):
            ax_inset.text(plon, plat, f'${i + 1}$', color='red', ha='left', va='bottom', fontsize=13, rotation=-15)
        ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
        pass
    
    if lon_cross is None or lat_cross is None:
        if st_point is not None and ed_point is not None:
            ax_inset.plot(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
    else:
        ax_inset.plot(lon_cross, lat_cross, c='k', zorder=2)
    return ax_inset

@kwargs_wrapper
def cross_section_prmsl(ax, prmsl, levels=np.arange(800, 1100, 2.5), cmap='inferno',
                      st_point=None, ed_point=None, lon_cross=None, lat_cross=None,
                      map_extent=(70, 145, 15, 55), h_pos=None):

    x, y, z = prmsl['lon'].values, prmsl['lat'].values, prmsl.values.squeeze()
    crs = ccrs.PlateCarree()
    if not h_pos:
        # h_pos为空，则固定自动计算显示到左上角
        l, b, w, h = ax.get_position().bounds
        # h_pos = [l, b + h - 0.22, 0.25, 0.2]
        map_width = map_extent[1] - map_extent[0]
        map_height = map_extent[3] - map_extent[2]
        if map_width > map_height:
            width_inset = 0.25
            height_inset = width_inset * map_height / map_width
            xpad = -0.02 # ?遗留问题，正常逻辑是加上l+pad，可能是matplotlib自适应引起的
        else:
            height_inset = 0.25
            width_inset = height_inset * map_width / map_height
            xpad = 0.02 # ?遗留问题，正常逻辑是加上l+pad，可能是matplotlib自适应引起的
        ypad = 0.01
        h_pos = [l + xpad, b + h - height_inset - ypad, width_inset, height_inset]

    # ax_inset = fig.add_axes(h_pos, projection=crs)
    ax_inset = ax.get_figure().add_axes(h_pos, projection=crs)
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
        # endpoints = crs.transform_points(ccrs.Geodetic(), *np.vstack([st_point, ed_point]).transpose()[::-1])

        # 支持多点的情况
        st = np.array(st_point).reshape(-1, 2) # [[lat, lon]]
        ed = np.array(ed_point).reshape(-1, 2) # [[lat, lon]]
        endpoints = np.vstack([st, ed[-1, :].reshape(-1, 2)]) # [[lat, lon]]
        endpoints = crs.transform_points(ccrs.Geodetic(), endpoints[:, 1], endpoints[:, 0])
        for i, (plon, plat, _) in enumerate(endpoints):
            ax_inset.text(plon, plat, f'${i + 1}$', color='red', ha='left', va='bottom', fontsize=13, rotation=-15)
        ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
        pass
    
    if lon_cross is None or lat_cross is None:
        if st_point is not None and ed_point is not None:
            ax_inset.plot(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
    else:
        ax_inset.plot(lon_cross, lat_cross, c='k', zorder=2)
    return ax_inset

@kwargs_wrapper
def cross_section_rain(ax, rain, times, title='', title_loc='right', title_fontsize=25, reverse_time=True, xtickfmt='%m月%d日%H时'):
    
    l, b, w, h = ax.get_position().bounds
    ax_inset = ax.get_figure().add_axes([l, b - h*0.4 - 0.1, w, h * 0.4])

    if not title:
        title = f"{rain.attrs['valid_time']}小时降水"
    ax_inset.set_title(title, loc=title_loc, fontsize=title_fontsize)

    xstklbls = mpl.dates.DateFormatter(xtickfmt)
    ax_inset.xaxis.set_major_formatter(xstklbls)
    for label in ax_inset.get_xticklabels():
        label.set_rotation(30)
        label.set_fontsize(15)
        label.set_horizontalalignment('right')
    #要放到以上get_xtcklabels之后，否则get_xticklabels会失效，原因未明
    utl_plotmap.time_ticks_formatter(ax_inset, times, if_minor=True)

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
