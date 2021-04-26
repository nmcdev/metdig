# -*- coding: utf-8 -*-

import sys
import pkg_resources
import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from cartopy.io.shapereader import Reader
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.text import TextPath
from matplotlib.patches import PathPatch
import matplotlib.patheffects as mpatheffects
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import metdig.graphics.lib.utility as utl

pkg_name = 'metdig.graphics'

def add_ticks(ax, xticks=None, yticks=None, crs=ccrs.PlateCarree(), **kwargs):
    if xticks is not None:
        ax.set_xticks(xticks, crs=crs)
        lon_formatter = LongitudeFormatter(zero_direction_label=False)
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.tick_params(axis='x', **kwargs)
    if yticks is not None:
        ax.set_yticks(yticks, crs=crs)
        lat_formatter = LatitudeFormatter()
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.tick_params(axis='y', **kwargs)

def add_china_map_2cartopy_public(ax, name='province', facecolor='none',
                                  edgecolor='c', lw=2, **kwargs):
    """
    Draw china boundary on cartopy map.
    :param ax: matplotlib axes instance.
    :param name: map name.
    :param facecolor: fill color, default is none.
    :param edgecolor: edge color.
    :param lw: line width.
    :return: None
    """

    # map name
    names = {'nation': "NationalBorder", 
             'province': "Province",
            #  'county': "County",  # 无资源，暂时注释
             'river': "hyd1_4l",
             'river_high': "hyd2_4l",
             'coastline': 'ne_10m_coastline'}

    # get shape filename
    shpfile = pkg_resources.resource_filename(pkg_name, "resources/shapefile/" + names[name] + ".shp")

    # add map
    ax.add_geometries(
        Reader(shpfile).geometries(), ccrs.PlateCarree(),
        facecolor=facecolor, edgecolor=edgecolor, lw=lw, **kwargs)


def adjust_map_ratio(ax, map_extent=None, datacrs=None):
    '''
    adjust the map_ratio in the projection of AlbersEqualArea in different area
    :ax = Axes required
    :map_extent=map_extent required
    :datacrs data projection reqired
    :return none
    '''
    map_ratio = (map_extent[1] - map_extent[0]) / (map_extent[3] - map_extent[2])
    ax.set_extent(map_extent, crs=datacrs)
    d_y = map_extent[3] - map_extent[2]
    map_extent2 = map_extent
    for i in range(0, 10000):
        map_ratio_real = (ax.get_extent()[1] - ax.get_extent()[0]) / 2. / ((ax.get_extent()[3] - ax.get_extent()[2]) / 2.)
        if(abs(map_ratio_real - map_ratio) < 0.001):
            break
        if(i == 0):
            if(map_ratio_real - map_ratio > 0):
                d_y = d_y + d_y * 0.001
            if(map_ratio_real - map_ratio <= 0):
                d_y = d_y - d_y * 0.001
            bottom = (map_extent[2] + map_extent[3]) / 2 - d_y / 2
            top = (map_extent[2] + map_extent[3]) / 2 + d_y / 2
            map_extent2 = [map_extent[0], map_extent[1], bottom, top]
        if(i > 0):
            d_y = map_extent2[3] - map_extent2[2]
            if(map_ratio_real - map_ratio > 0):
                d_y = d_y + d_y * 0.001
            if(map_ratio_real - map_ratio <= 0):
                d_y = d_y - d_y * 0.001
            bottom = (map_extent2[2] + map_extent2[3]) / 2 - d_y / 2
            top = (map_extent2[2] + map_extent2[3]) / 2 + d_y / 2
            map_extent2 = [map_extent2[0], map_extent2[1], bottom, top]
        ax.set_extent(map_extent2, crs=datacrs)
    return map_extent2


def add_cartopy_background(ax, name='RD'):
    # http://earthpy.org/cartopy_backgroung.html
    # C:\ProgramData\Anaconda3\Lib\site-packages\cartopy\data\raster\natural_earth
    bg_dir = pkg_resources.resource_filename(pkg_name, 'resources/backgrounds/')
    os.environ["CARTOPY_USER_BACKGROUNDS"] = bg_dir
    ax.background_img(name=name, resolution='high')


def add_city_on_map(ax, map_extent=None, size=7, small_city=False, zorder=10, **kwargs):
    """
    :param ax: `matplotlib.figure`, The `figure` instance used for plotting
    :param x: x position padding in pixels
    :param kwargs:
    :return: `matplotlib.image.FigureImage`
             The `matplotlib.image.FigureImage` instance created.
    """
    if map_extent is None:
        map_extent = list(ax.get_xlim()) + list(ax.get_ylim())

    dlon = map_extent[1] - map_extent[0]
    dlat = map_extent[3] - map_extent[2]

    # small city
    # if(small_city):
    #     try:
    #         fname = 'small_city.000'
    #         fpath = "resources/" + fname
    #     except KeyError:
    #         raise ValueError('can not find the file small_city.000 in the resources')
    #     city = read_micaps_17(pkg_resources.resource_filename(
    #         pkg_name, fpath))

    #     lon=city['lon'].values.astype(np.float)
    #     lat=city['lat'].values.astype(np.float)
    #     city_names=city['Name'].values

    #     for i in range(0,len(city_names)):
    #         if((lon[i] > map_extent[0]+dlon*0.05) and (lon[i] < map_extent[1]-dlon*0.05) and
    #         (lat[i] > map_extent[2]+dlat*0.05) and (lat[i] < map_extent[3]-dlat*0.05)):
    #                 #ax.text(lon[i],lat[i],city_names[i], family='SimHei-Bold',ha='right',va='top',size=size-4,color='w',zorder=zorder,**kwargs)
    #             ax.text(lon[i],lat[i],city_names[i], family='SimHei',ha='right',va='top',size=size-4,color='black',zorder=zorder,**kwargs)
    #         ax.scatter(lon[i], lat[i], c='black', s=25, alpha=0.5,zorder=zorder, **kwargs)
    # province city
    try:
        fname = 'city_province.000'
        fpath = "resources/stations/" + fname
    except KeyError:
        raise ValueError('can not find the file city_province.000 in the resources')

    city = utl.read_micaps_17(pkg_resources.resource_filename(pkg_name, fpath))

    lon = city['lon'].values.astype(np.float) / 100.
    lat = city['lat'].values.astype(np.float) / 100.
    city_names = city['Name'].values

    # 步骤一（替换sans-serif字体） #得删除C:\Users\HeyGY\.matplotlib 然后重启vs，刷新该缓存目录获得新的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    for i in range(0, len(city_names)):
        if((lon[i] > map_extent[0] + dlon * 0.05) and (lon[i] < map_extent[1] - dlon * 0.05) and
           (lat[i] > map_extent[2] + dlat * 0.05) and (lat[i] < map_extent[3] - dlat * 0.05)):
            if(city_names[i] != '香港' and city_names[i] != '南京' and city_names[i] != '石家庄' and city_names[i] != '天津'):
                r = city_names[i]
                t = ax.text(lon[i], lat[i], city_names[i], family='SimHei', ha='right', va='top', size=size, zorder=zorder, **kwargs)
            else:
                t = ax.text(lon[i], lat[i], city_names[i], family='SimHei', ha='left', va='top', size=size, zorder=zorder, **kwargs)
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                mpatheffects.Normal()])
            ax.scatter(int(lon[i]) + 100 * (lon[i] - int(lon[i])) / 60., int(lat[i]) + 100 * (lat[i] - int(lat[i])) / 60., c='black', s=25, zorder=zorder, **kwargs)
    return

def add_south_china_sea_plt(map_extent=[107, 120, 2, 20], pos=[0.1, 0.1, .2, .4], **kwargs):

    # draw main figure
    plotcrs = ccrs.PlateCarree(central_longitude=100.)
    ax = plt.axes(pos, projection=plotcrs)
    datacrs = ccrs.PlateCarree()
    ax.set_extent(map_extent, crs=datacrs)
    ax.add_feature(cfeature.OCEAN)
    ax.coastlines('50m', edgecolor='black', linewidth=0.5, zorder=50)
    add_china_map_2cartopy_public(ax, name='nation', edgecolor='black', lw=0.8, zorder=40)
    #ax.background_img(name='RD', resolution='high')
    add_cartopy_background(ax, name='RD')
    return ax


def add_south_china_sea_png(pos=[0.1, 0.1, .2, .4], size='medium', **kwargs):
    fname_suffix = {
        # 'small': 'small.png',
        'medium': 'medium.png',
        # 'large': 'large.png',
        # 'Xlarge': 'Xlarge.png',
    }
    try:
        fname = fname_suffix[size]
        fpath = "resources/south_china/" + fname
    except KeyError:
        raise ValueError('Unknown south_china size or selection')
    img = plt.imread(pkg_resources.resource_filename(pkg_name, fpath))

    ax = plt.axes(pos)
    ax.imshow(img, zorder=0)
    ax.axis('off')
    return ax

def add_city_values_on_map(ax, data, map_extent=None, size=13, zorder=10, cmap=None, transform=ccrs.PlateCarree(), **kwargs):
    
    if map_extent is None:
        map_extent = list(ax.get_xlim()) + list(ax.get_ylim())
        
    dlon = map_extent[1] - map_extent[0]
    dlat = map_extent[3] - map_extent[2]
    # province city
    try:
        fname = 'city_province.000'
        fpath = "resources/stations/" + fname
    except KeyError:
        raise ValueError('can not find the file city_province.000 in the resources')

    city = utl.read_micaps_17(pkg_resources.resource_filename(pkg_name, fpath))

    lon = city['lon'].values.astype(np.float) / 100.
    lat = city['lat'].values.astype(np.float) / 100.
    city_names = city['Name'].values

    number_city = data.interp(lon=('points', lon), lat=('points', lat))

    # 步骤一（替换sans-serif字体） #得删除C:\Users\HeyGY\.matplotlib 然后重启vs，刷新该缓存目录获得新的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    for i in range(0, len(city_names)):
        if((lon[i] > map_extent[0] + dlon * 0.05) and (lon[i] < map_extent[1] - dlon * 0.05) and
           (lat[i] > map_extent[2] + dlat * 0.05) and (lat[i] < map_extent[3] - dlat * 0.05)):
            if((np.array(['香港', '南京', '石家庄', '天津', '济南', '上海']) != city_names[i]).all()):
                r = city_names[i]
                num = ax.text(int(lon[i]) + 100 * (lon[i] - int(lon[i])) / 60.,
                              int(lat[i]) + 100 * (lat[i] - int(lat[i])) / 60.,
                              '%.1f' % np.squeeze(number_city.values)[i],
                              family='SimHei', ha='right', va='bottom', size=size, zorder=zorder, transform=transform, **kwargs)
            else:
                num = ax.text(int(lon[i]) + 100 * (lon[i] - int(lon[i])) / 60.,
                              int(lat[i]) + 100 * (lat[i] - int(lat[i])) / 60.,
                              '%.1f' % np.squeeze(number_city.values)[i],
                              family='SimHei', ha='left', va='bottom', size=size, zorder=zorder, transform=transform, **kwargs)
            num.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                  mpatheffects.Normal()])
    return
