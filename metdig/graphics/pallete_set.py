# -*- coding: utf-8 -*-


import sys
import os
import locale
import datetime
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.path as mpath
import matplotlib.patheffects as mpatheffects

from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from metpy.plots import SkewT

from meteva.base.tool.plot_tools import add_china_map_2basemap

import metdig.graphics.lib.utl_plotmap as utl_plotmap
import metdig.graphics.lib.utility as utl
from  metdig.graphics.lib.utility import kwargs_wrapper
from cartopy.io.img_tiles import Stamen,GoogleTiles

def plt_base_env():
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')
        
@kwargs_wrapper
def horizontal_pallete(fig=None,ax=None,figsize=(16, 9), crs=ccrs.PlateCarree(), map_extent=(60, 145, 15, 55),
                       title='', title_loc='left', title_fontsize=18, forcast_info='', nmc_logo=False,
                       add_coastline=True,add_china=True, add_province=True,add_river=True,add_city=True,add_county=False, add_county_city=False, add_nation=True,
                       add_background_style='borders', add_south_china_sea=False, add_grid=False, add_ticks=False,
                       background_zoom_level=5,add_tag=True,**kwargs):
    """[水平分布图画板设置]]

    Args:
        ax ():[绘图对象].用于用户传入自己的ax绘图拓展
        figsize (tuple, optional): [画板大小]. Defaults to (16, 9).
        crs ([type], optional): [画板投影类型投影]. Defaults to ccrs.PlateCarree().
        map_extent (tuple, optional): [绘图区域]. Defaults to (60, 145, 15, 55).
        title (str, optional): [标题]. Defaults to ''.
        title_fontsize (int, optional): [标题字体大小]. Defaults to 23.
        forcast_info (str, optional): [预报或其它描述信息]. Defaults to ''.
        nmc_logo (bool, optional): [是否增加logo]. Defaults to False.
        add_china (bool, optional): [是否增加中国边界线]. Defaults to True.
        add_city (bool, optional): [是否增加城市名称]. Defaults to True.
        add_background_style (str, [None, False, 'RD', 'YB', 'satellite', 'terrain', 'road']): [是否增加背景底图，None/False(无填充),RD(陆地海洋),YB(陆地海洋),satellite/terrain/road(卫星图像)，]. Defaults to 'RD'.
        add_south_china_sea (bool, optional): [是否增加南海]. Defaults to True.
        add_grid (bool, optional): [是否绘制网格线]]. Defaults to True.
        add_ticks (bool, optional): [是否绘制刻度]. Defaults to False.
        background_zoom_level (int, optional): [背景地图是卫星地图时需要手动设置zoomlevel]. Defaults to 10.
        add_tag(bool, optional): [是否标注metdig信息]. Defaults to True.

    Returns:
        [type]: [description]
    """    
    if isinstance(crs, ccrs.NorthPolarStereo):
        # 北极极射投影，关闭如下参数
        add_province = False
        add_river = False
        add_city = False
        add_county_city = False
        add_background_style = ''
        add_south_china_sea = False
        if map_extent[2] < 0:
            map_extent = (-180,180,0,90)
        else:
            map_extent = (-180,180, map_extent[2],90)
    elif isinstance(crs, ccrs.LambertConformal):
        # lambert投影，关闭如下参数
        add_south_china_sea = False
        # 设中心经纬度
        crs = ccrs.LambertConformal(central_longitude=((map_extent[0]+ map_extent[1])/2), central_latitude=((map_extent[2]+ map_extent[3])/2))
    elif isinstance(crs, ccrs.PlateCarree):
        # 等经纬度投影
        if map_extent[1] > 180:
            # # modify by wzj 2025.4.25 跨180度特殊情况，如果用户没有手动设置中心经度，强制设置中心经度为180
            if crs.proj4_params['lon_0'] == 0:
                crs = ccrs.PlateCarree(central_longitude=180)
  

    plt_base_env()  # 初始化字体中文等
    if fig is None:
        fig = plt.figure(figsize=figsize)
    if ax is None: # 
        ax = fig.add_subplot(projection=crs)

    # 标题
    ax.set_title(title, loc=title_loc, fontsize=title_fontsize)

    # set_map_extent
    if isinstance(crs, ccrs.PlateCarree):
        # 等经纬度投影
        if((map_extent[1]-map_extent[0] > 350) and (map_extent[3]-map_extent[2] > 170)):
            ax.set_global()
        else:
            # map_extent2 = utl_plotmap.adjust_map_ratio(ax, map_extent=map_extent, datacrs=ccrs.PlateCarree())
            # modify by wzj 2025.4.25, 修复当map_extent[1]超过180时的bug，数据默认都是0度中心经度，现在底层默认extent和ticks都以0度
            # ax.set_extent(map_extent, crs=crs)
            ax.set_extent(map_extent, crs=ccrs.PlateCarree())
    elif isinstance(crs, ccrs.NorthPolarStereo):
        # 非等经纬度投影，设置extent会出错
        ax.set_extent(map_extent, crs=ccrs.PlateCarree())
        #######以下为网格线的参数######
        theta = np.linspace(0, 2*np.pi, 100)
        center, radius = [0.5, 0.5], 0.5
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = mpath.Path(verts * radius + center)
        # 设置axes边界，为圆形边界，否则为正方形的极地投影
        ax.set_boundary(circle, transform=ax.transAxes)
    elif isinstance(crs, ccrs.LambertConformal):
        # lambert非等经纬度投影
        ax.set_extent([map_extent[0],map_extent[1],map_extent[2],map_extent[3]])
        vertices = [(lon, map_extent[2]) for lon in range(map_extent[0], map_extent[1] + 1, 1)] + [(lon, map_extent[3]) for lon in range(map_extent[1], map_extent[0] - 1, -1)]
        boundary = mpath.Path(vertices)
        ax.set_boundary(boundary, transform=ccrs.PlateCarree())
        pass

    # add grid lines
    # if add_grid: 
    #     gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=100)
    #     gl.xlocator = mpl.ticker.FixedLocator(np.arange(-180, 181, 10))
    #     gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 10))

    # 海岸线，省界，河流等中国边界信息
    if add_coastline:
        if(isinstance(add_coastline,bool)):
            utl_plotmap.add_china_map_2cartopy_public(ax, name='coastline', edgecolor='gray', lw=0.5, zorder=19, alpha=1,crs=ccrs.PlateCarree())
        else:
            utl_plotmap.add_china_map_2cartopy_public(ax, name='coastline', edgecolor='gray', lw=0.5, zorder=19,crs=ccrs.PlateCarree(),kwargs=add_coastline)

    if add_china:
        if(isinstance(add_china,bool)):
            utl_plotmap.add_china_map_2cartopy_public(ax, name='nation', edgecolor='gray', lw=1.5, zorder=19,crs=ccrs.PlateCarree())
        else:
            utl_plotmap.add_china_map_2cartopy_public(ax, name='nation', edgecolor='gray', lw=1.5, zorder=19,crs=ccrs.PlateCarree(),kwargs=add_china)

    if add_province:
        if(isinstance(add_province,bool)):
            utl_plotmap.add_china_map_2cartopy_public(ax, name='province', edgecolor='gray', lw=1, zorder=19,crs=ccrs.PlateCarree())
        else:
            utl_plotmap.add_china_map_2cartopy_public(ax, name='province', edgecolor='gray', lw=1, zorder=19,crs=ccrs.PlateCarree(),kwargs=add_province)

    
    if add_river:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=0, alpha=0.5,crs=ccrs.PlateCarree())
        # add_china_map_2basemap(ax, name="province", edgecolor='gray', lw=0.5, encoding='gbk', zorder=0) 
        # add_china_map_2basemap(ax, name="nation", edgecolor='black', lw=0.8, encoding='gbk', zorder=0) 
    if add_county:
        add_china_map_2basemap(ax, name="county", edgecolor='#D9D9D9', lw=0.7, encoding='gbk',zorder=19) 
        # add_china_map_2basemap(ax, name="river", edgecolor='#74b9ff', lw=0.8, encoding='gbk', zorder=1) 
        pass

    # 城市名称
    if add_city:
        # small_city = False
        # if(map_extent[1] - map_extent[0] < 25):
        #     small_city = True
        utl_plotmap.add_city_on_map(ax, map_extent=map_extent, transform=ccrs.PlateCarree(),
                                    zorder=101, size=13)
    if add_county_city:
        # small_city = False
        # if(map_extent[1] - map_extent[0] < 25):
        #     small_city = True
        utl_plotmap.add_city_on_map(ax, map_extent=map_extent, transform=ccrs.PlateCarree(),
                                    zorder=101, size=13, city_type='county')

    # 背景图
    if add_background_style == 'borders':
        # ax.add_feature(cfeature.OCEAN, facecolor='#EDFBFE')
        # ax.add_feature(cfeature.LAND, facecolor='#FCF6EA')
        # add_china_map_2basemap(ax, name="world", edgecolor='gray', lw=0.1, encoding='gbk',zorder=19) 
        utl_plotmap.add_china_map_2cartopy_public(ax, name='world', edgecolor='gray', lw=1, zorder=19,crs=ccrs.PlateCarree())
    elif add_background_style == 'RD':
        utl_plotmap.add_china_map_2cartopy_public(ax, name='world', edgecolor='gray', lw=1, zorder=19,crs=ccrs.PlateCarree())
        # add_china_map_2basemap(ax, name="world", edgecolor='gray', lw=0.5, encoding='gbk',zorder=19) 
        # ax.add_feature(cfeature.OCEAN)
        utl_plotmap.add_cartopy_background(ax, name='RD')
    elif add_background_style == 'YB':
        ax.add_feature(cfeature.LAND, facecolor='#EBDBB2')
        ax.add_feature(cfeature.OCEAN, facecolor='#C8EBFA')
    elif add_background_style == 'satellite':
        request = utl.TDT_img()  # 卫星图像
        ax.add_image(request, background_zoom_level)  # level=10 缩放等级
    elif add_background_style == 'terrain':
        # request = utl.TDT_Hillshade()  # 地形阴影
        # ax.add_image(request, background_zoom_level)  # level=10 缩放等
        request = utl.TDT_ter()  # 地形
        ax.add_image(request, background_zoom_level,alpha=1)  # level=10 缩放等

    elif add_background_style == 'terrain2':
        tiler = Stamen('terrain-background')
        ax.add_image(tiler, background_zoom_level) #,interpolation='spline36'

    elif add_background_style == 'terrain3':
        request = utl.TDT_ter2()  # 地形
        # request = GoogleTiles(style='terrain')
            # url='http://mt1.google.com/vt/lyrs={style}&x={x}&y={y}&z={z}')  # 谷歌地形
        ax.add_image(request, background_zoom_level)  

    elif add_background_style == 'terrain4':
        request = utl.TDT_Hillshade()  # 地形阴影
        ax.add_image(request, background_zoom_level)  # level=10 缩放等
        # request = utl.TDT_ter()  # 地形
        # ax.add_image(request, background_zoom_level,alpha=0.5)  # level=10 缩放等


    elif add_background_style == 'road':
        request = utl.TDT()  # 卫星图像
        ax.add_image(request, background_zoom_level)  # level=10 缩放等级

    # 增加坐标和网格线
    if isinstance(crs, ccrs.PlateCarree):
        if add_ticks:
            if(isinstance(add_ticks,bool)):
                # modify by wzj 2025.4.25 更改为自动生成刻度，避免绘图区域变小后，刻度显示不整齐
                # utl_plotmap.add_ticks(ax,xticks=np.arange(map_extent[0], map_extent[1]+1, 10),
                #                     yticks=np.arange(map_extent[2], map_extent[3]+1, 10),add_grid=add_grid)
                utl_plotmap.add_ticks_auto(ax, map_extent,add_grid=add_grid)
            else:
                # utl_plotmap.add_ticks(ax,xticks=np.arange(map_extent[0], map_extent[1]+1, 10),
                #                     yticks=np.arange(map_extent[2], map_extent[3]+1, 10),add_grid=add_grid,kwargs=add_ticks)
                utl_plotmap.add_ticks_auto(ax, map_extent,add_grid=add_grid,kwargs=add_ticks)
            # plt.tick_params(labelsize=15)
            # ax.set_yticks(np.arange(map_extent[2], map_extent[3]+1, 10), crs=crs)
            # ax.set_xticks(np.arange(map_extent[0], map_extent[1]+1, 10), crs=crs)
            # lon_formatter = LongitudeFormatter(dateline_direction_label=True)
            # lat_formatter = LatitudeFormatter()
            # ax.xaxis.set_major_formatter(lon_formatter)
            # ax.yaxis.set_major_formatter(lat_formatter)
        else:  
            if add_grid:
                gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=100)
                gl.xlocator = mpl.ticker.FixedLocator(np.arange(-180, 181, 10))
                gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 10))
    elif isinstance(crs, ccrs.NorthPolarStereo):
        utl_plotmap.add_ticks_NorthPolarStereo(ax, map_extent, add_grid=add_grid, add_ticks=add_ticks)

    elif isinstance(crs, ccrs.LambertConformal):
        if add_ticks:
            # ticks方法无法使用，用text代替
            xticks = np.arange(map_extent[0],  map_extent[1]+1, 10)
            yticks = np.arange(map_extent[2], map_extent[3]+1, 10)
            for lon in xticks:
                if lon > 0:
                    lon_str = f"{lon}°E"
                else:
                    lon_str = f"{abs(lon)}°W"
                ax.text(lon, map_extent[2]-1, lon_str, va='top', ha='center', transform=ccrs.PlateCarree(), fontsize=15)
            for lat in yticks:
                if lat > 0:
                    lat_str = f"{lat}°N"
                else:
                    lat_str = f"{abs(lat)}°S"
                ax.text(map_extent[0]-1, lat, lat_str, va='center', ha='right', transform=ccrs.PlateCarree(), fontsize=15)
        if add_grid:
            gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=100)
            gl.xlocator = mpl.ticker.FixedLocator(np.arange(-180, 181, 10))
            gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 10))


    # 南海
    if add_south_china_sea:
        l, b, w, h = ax.get_position().bounds
        utl_plotmap.add_south_china_sea_png(pos=[l + w - 0.1, b+0.005, 0.11, 0.211], name='simple')  # 直接贴图

    # 预报/分析描述信息
    if forcast_info:
        if(isinstance(forcast_info,str)):
            # ax.text(0.01, 0.99, forcast_info, transform=ax.transAxes, size=12, va='top',
            #         ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0),zorder=20)
            utl_plotmap.forcast_info(ax,x=0.01,y=0.99,info=forcast_info,transform=ax.transAxes)
        else:
            utl_plotmap.forcast_info(ax,x=0.01,y=0.99,info=forcast_info, transform=ax.transAxes, size=12, va='top',
                    ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0),zorder=20,kwargs=forcast_info)
    # logo

    if nmc_logo:
        l, b, w, h = ax.get_position().bounds
        # utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h - 0.1, .1, .1], which='nmc', size='Xlarge') # 左上角
        utl.add_logo_extra_in_axes(pos=[l + w - 0.08, b + h - 0.1, .1, .1], which='nmc', size='Xlarge')  # 右上角

    # 添加 powered by metdig
    if(add_tag):
        t=ax.text(0.01, 0.028, 'Powered by MetDig', transform=ax.transAxes, size=15,
                color='black', alpha=1.0, va='bottom',  ha='left', zorder=100)  # 左下角图的里面
        t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                    mpatheffects.Normal()])
        t=ax.text(0.01, 0.003, 'https://github.com/nmcdev/metdig', transform=ax.transAxes, size=10,
                color='black', alpha=1.0, va='bottom',  ha='left', zorder=100)  # 左下角图的里面
        t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                    mpatheffects.Normal()])
    # ax.text(1.00, -0.12, 'Powered by MetDig', transform=ax.transAxes, size=14, color='gray', alpha=1.0, va='bottom',  ha='right')  # 右下角图的外面，colorbar的下边
    # ax.text(1.00, -0.005, 'Powered by MetDig', transform=ax.transAxes, size=14, color='gray', alpha=1.0, va='top',  ha='right' )  # 右下角图的外面刻度线的位置
    return fig, ax

@kwargs_wrapper
def cross_lonpres_pallete(fig=None, ax=None, figsize=(22, 15), levels=None, index=None, lon_cross=None, lat_cross=None, st_point=None, ed_point=None, 
                          title='', forcast_info='', title_loc='right', title_fontsize=25,
                          nmc_logo=False, add_tag=True, logyaxis=True, yoffset=0,**kwargs):
    
    plt_base_env()  # 初始化字体中文等

    if fig is None:
        fig = plt.figure(figsize=figsize)
    if ax is None: 
        ax = fig.add_subplot()

    ax.set_title(title, loc=title_loc, fontsize=title_fontsize)

    for label in ax.get_yticklabels():
        label.set_fontsize(15)

    # Adjust the y-axis to be logarithmic
    if(logyaxis):
        ax.set_yscale('symlog')
    if levels is not None:
        if levels[0] < levels[-1]:
            levels = levels[::-1] # 保证levels是从大到小的
        ax.set_yticklabels(np.arange(levels[0], levels[-1]-1, -100))
        ax.set_ylim(levels[0], levels[-1])
        ax.set_yticks(np.arange(levels[0], levels[-1]-1, -100))
        # ax.set_ylim(levels.max(), levels.min())
        yoffset = abs(levels[0] - levels[-1]) * yoffset
        ax.set_ylim(levels.max() + yoffset, levels.min() - yoffset)
    else:
        ax.set_yticklabels([1000, 925, 850, 700, 600, 500, 400, 300, 200, 100])
        ax.set_yticks([1000, 925, 850, 700, 600, 500, 400, 300, 200, 100])
        ax.set_ylim(1000, 100)


    if index is not None and lon_cross is not None and index is not lat_cross:
        # 先以index为x轴刻度，把刻度替换成经纬度
        ax.set_xlim(index[0], index[-1])
        x_ticks = np.linspace(index[0], index[-1], 10).astype('int32')
        ax.set_xticks(x_ticks)
        x_labels = []
        for x, y in zip(lon_cross[ax.get_xticks().astype('int32')], lat_cross[ax.get_xticks().astype('int32')]):
            if x > 0:
                x = f'{x:.2f}°E'
            else:
                x = f'{abs(x):.2f}°W'

            if y > 0:
                y = f'{y:.2f}°N'
            else:
                y = f'{abs(y):.2f}°S'
            x_labels.append(f'{x}\n{y}')
        ax.set_xticklabels(x_labels)

        # 在x轴上标上points记号1-N
        if st_point is not None and ed_point is not None:
            st = np.array(st_point).reshape(-1, 2) # [[lat, lon]]
            ed = np.array(ed_point).reshape(-1, 2) # [[lat, lon]]
            endpoints = np.vstack([st, ed[-1, :].reshape(-1, 2)]) # [[lat, lon]]
            for i, (plat, plon) in enumerate(endpoints):
                idx = np.argmin((lon_cross - plon) ** 2 + (lat_cross - plat) ** 2)
                if idx == 0:
                    ax.text(index[idx], ax.get_ylim()[0], f'${i + 1}$', color='red', ha='right', va='bottom', fontsize=16, zorder=101, rotation=-15)
                elif idx == len(index) - 1:
                    ax.text(index[idx], ax.get_ylim()[0], f'${i + 1}$', color='red', ha='left', va='bottom', fontsize=16, zorder=101, rotation=-15)
                else:
                    ax.text(index[idx], ax.get_ylim()[0], f'${i + 1}$', color='red', ha='center', va='bottom', fontsize=16, zorder=101, rotation=-15)

    for label in ax.get_xticklabels():
        label.set_fontsize(15)

    # ax.set_ylabel('Pressure (hPa)', fontsize=15)
    ax.set_ylabel('气压 (hPa)', fontsize=15)
    ax.set_xlabel('经度/纬度', fontsize=15)

    if forcast_info:
        ax.text(0.01, 1.005, forcast_info, transform=ax.transAxes, size=11, va='bottom',
                ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='white', pad=0.0))

    if nmc_logo:
        l, b, w, h = ax.get_position().bounds
        # utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h, 0.07, 0.07], which='nmc', size='Xlarge')# 左上角
        utl.add_logo_extra_in_axes(pos=[l + w - 0.08, b + h - 0.1, .1, .1], which='nmc', size='Xlarge')  # 右上角

    if(add_tag):
        ax.text(0.002, 0.001, 'Powered by MetDig', transform=ax.transAxes, size=14,
                color='gray', alpha=1.0, va='bottom',  ha='left', zorder=100)  # 左下角图的里面
    return fig, ax

@kwargs_wrapper
def cross_timepres_pallete(fig=None, ax=None, figsize=(22, 15), levels=None, times=None, title='', forcast_info='', title_loc='right', title_fontsize=25,
                           nmc_logo=False, reverse_time=True, logyaxis=True, yoffset=0, add_tag=True, xtickfmt='%m月%d日%H时',if_minor=True,**kwargs):
    """[时间剖面画板初始化]

    Args:
        figsize (tuple, optional): [图形比例大小]. Defaults to (16, 9).
        levels ([type], optional): [垂直层次坐标]. Defaults to None.
        times ([type], optional): [时间坐标]. Defaults to None.
        title (str, optional): [画板标题]. Defaults to ''.
        forcast_info (str, optional): [时间信息标注]. Defaults to ''.
        reverse_time (bool, optional): [时间轴是否反转]. Defaults to True.

    Returns:
        [type]: [description]
    """
    if(reverse_time):
        times = times[::-1]

    plt_base_env()  # 初始化字体中文等

    if fig is None:
        fig = plt.figure(figsize=figsize)
    if ax is None:
        ax = fig.add_subplot()
    

    ax.set_title(title, loc=title_loc, fontsize=title_fontsize)

    xstklbls = mpl.dates.DateFormatter(xtickfmt)
    ax.xaxis.set_major_formatter(xstklbls)

    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_fontsize(15)
        label.set_horizontalalignment('right')

    #要放到以上get_xtcklabels之后，否则get_xticklabels会失效，原因未明
    utl_plotmap.time_ticks_formatter(ax,times,if_minor=if_minor)

    for label in ax.get_yticklabels():
        label.set_fontsize(15)

    if(logyaxis):
        ax.set_yscale('symlog')
    # ax.set_ylabel('Pressure (hPa)', fontsize=15)
    ax.set_ylabel('气压 （hPa）', fontsize=15)
    if levels is not None:
        if levels[0] < levels[-1]:
            levels = levels[::-1] # 保证levels是从大到小的
        ax.set_yticklabels(np.arange(levels[0], levels[-1]-1, -100))
        ax.set_ylim(levels[0], levels[-1])
        ax.set_yticks(np.arange(levels[0], levels[-1]-1, -100))
        # ax.set_ylim(levels.max(), levels.min())
        yoffset = abs(levels[0] - levels[-1]) * yoffset
        ax.set_ylim(levels.max() + yoffset, levels.min() - yoffset)
    else:
        ax.set_yticklabels([1000, 925, 850, 700, 600, 500, 400, 300, 200, 100])
        ax.set_yticks([1000, 925, 850, 700, 600, 500, 400, 300, 200, 100])
        ax.set_ylim(1000, 100)

    ax.set_xlim(times[0], times[-1])

    if forcast_info:
        ax.text(0.01, 1.005, forcast_info, transform=ax.transAxes, size=11, va='bottom',
                ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='white', pad=0.0))

    if nmc_logo:
        l, b, w, h = ax.get_position().bounds
        # utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h, 0.07, 0.07], which='nmc', size='Xlarge')# 左上角
        utl.add_logo_extra_in_axes(pos=[l + w - 0.08, b + h - 0.1, .1, .1], which='nmc', size='Xlarge')  # 右上角
    if add_tag:
        ax.text(0.002, 0.001, 'Powered by MetDig', transform=ax.transAxes, size=14,
                color='gray', alpha=1.0, va='bottom',  ha='left', zorder=100)  # 左下角图的里面
    return fig, ax

@kwargs_wrapper
def cross_timeheight_pallete(figsize=(22, 15), heights=None, times=None, title='', forcast_info='', title_loc='right', title_fontsize=25,
                             nmc_logo=False, reverse_time=True,add_tag=True,ylim=[0,5000],xtickfmt='%m月%d日%H时',if_minor=True,**kwargs):
    if(reverse_time):
        times = times[::-1]

    plt_base_env()  # 初始化字体中文等

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot()

    ax.set_title(title, loc=title_loc, fontsize=title_fontsize)

    xstklbls = mpl.dates.DateFormatter(xtickfmt)
    ax.xaxis.set_major_formatter(xstklbls)
    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_fontsize(15)
        label.set_horizontalalignment('right')
    #要放到以上get_xtcklabels之后，否则get_xticklabels会失效，原因未明
    utl_plotmap.time_ticks_formatter(ax,times,if_minor=if_minor)

    for label in ax.get_yticklabels():
        label.set_fontsize(15)

    ax.set_ylabel('高度/m', fontsize=15)
    ax.set_yticklabels([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])
    ax.set_yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])
    ax.set_ylim(ylim)
    ax.set_xlim(times[0], times[-1])

    if forcast_info:
        ax.text(0.01, 1.005, forcast_info, transform=ax.transAxes, size=11, va='bottom',
                ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='white', pad=0.0))

    if nmc_logo:
        l, b, w, h = ax.get_position().bounds
        # utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h, 0.07, 0.07], which='nmc', size='Xlarge')# 左上角
        utl.add_logo_extra_in_axes(pos=[l + w - 0.08, b + h - 0.1, .1, .1], which='nmc', size='Xlarge')  # 右上角
    if add_tag:
        ax.text(0.002, 0.001, 'Powered by MetDig', transform=ax.transAxes, size=14, color='gray', alpha=1.0, va='bottom',  ha='left')  # 左下角图的里面
    return fig, ax

@kwargs_wrapper
def time_series_left_right_bottom_v2(figsize=(16, 4.5), if_add_right=True,if_add_bottom=True, title_left='', title_right='', label_leftax='', label_rightax='', label_bottomax='',**kwargs):

    plt_base_env()  # 初始化字体中文等

    fig = plt.figure(figsize=figsize)

    if(if_add_right):
        ax_left = HostAxes(fig, [0.1, 0.28, .8, .62])
        fig.add_axes(ax_left)
        ax_left.axis['left'].label.set_fontsize(15)
        ax_left.axis['left'].major_ticklabels.set_fontsize(15)
        ax_right = ParasiteAxes(ax_left, sharex=ax_left)
        # append axes
        ax_left.parasites.append(ax_right)
        ax_left.axis['right'].set_visible(False)
        ax_left.axis['right'].set_visible(False)
        ax_right.axis['right'].set_visible(True)
        ax_right.axis['right'].major_ticklabels.set_visible(True)
        ax_right.axis['right'].label.set_visible(True)
        ax_right.axis['right'].label.set_fontsize(15)
        ax_right.axis['right'].major_ticklabels.set_fontsize(15)
        ax_right.set_ylabel(label_rightax)
    else:
        ax_left=fig.add_axes([0.1, 0.28, .8, .62])
        ax_left.tick_params(axis='y',labelsize=10)
        ax_left.tick_params(axis='x',labelsize=10)
        ax_right=None

    plt.title(title_left, loc='left', fontsize=21)
    plt.title(title_right, loc='right', fontsize=15)
    ax_left.grid(axis='x', which='minor', ls='--')
    ax_left.grid(axis='both', which='major')
    ax_left.tick_params(length=10)
    ax_left.set_ylabel(label_leftax)
    ax_left.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H'))  # 设置格式
    ax_left.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 20)))  # 单位是小时
    ax_left.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=(8, 11, 14, 17, 20, 23, 2, 5)))  # 单位是小时
    ax_left.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))  # 将此y轴次刻度标签设置为1的倍数
    ax_left.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5))  # 将此y轴主刻度标签设置为5的倍数

    if(if_add_bottom):
        ax_left.set_xticklabels([' '])
        ax_bottom = plt.axes([0.1, 0.16, .8, .12])
        ax_bottom.grid(axis='x', which='both', ls='--')
        ax_bottom.tick_params(length=5, axis='x')
        ax_bottom.tick_params(length=0, axis='y')
        ax_bottom.tick_params(axis='x', labelsize=15)
        ax_bottom.set_ylabel(label_bottomax, fontsize=15)
        # ax_bottom.axis('off')
        ax_bottom.set_yticklabels([' '])
        ax_bottom.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H'))  # 设置格式
        ax_bottom.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 20)))  # 单位是小时
        ax_bottom.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=(8, 11, 14, 17, 20, 23, 2, 5)))  # 单位是小时
        ax_bottom.text(0.90, -1.2, 'Powered by MetDig', transform=ax_bottom.transAxes, size=14,
                    color='gray', alpha=1.0, va='bottom',  ha='left', zorder=100)  # 左下角图的里面
    else:
        # metdig 标识
        ax_left.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H'))  # 设置格式
        ax_left.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 20)))  # 单位是小时
        ax_left.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=(8, 11, 14, 17, 20, 23, 2, 5)))  # 单位是小时
        ax_left.text(0.90, -0.2, 'Powered by MetDig', transform=ax_left.transAxes, size=14,
                    color='gray', alpha=1.0, va='bottom',  ha='left', zorder=100)  # 左下角图的里面
        ax_bottom=None
    return fig, ax_left, ax_right, ax_bottom

@kwargs_wrapper
def time_series_left_right_bottom(times=None,figsize=(16, 4.5), title_left='', title_right='', label_leftax='', label_rightax='', label_bottomax='',add_tag=True,**kwargs):

    plt_base_env()  # 初始化字体中文等

    fig = plt.figure(figsize=figsize)

    ax_left = HostAxes(fig, [0.1, 0.28, .8, .62])
    ax_right = ParasiteAxes(ax_left, sharex=ax_left)

    # append axes
    ax_left.parasites.append(ax_right)

    # invisible right axis of ax

    ax_left.axis['right'].set_visible(False)
    ax_left.axis['right'].set_visible(False)
    ax_left.axis['left'].label.set_fontsize(15)
    ax_left.axis['left'].major_ticklabels.set_fontsize(15)
    ax_left.tick_params(length=10)
    ax_left.tick_params(axis='y', labelsize=100)
    ax_left.set_ylabel(label_leftax)
    ax_left.set_xticklabels([' '])
    ax_left.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H'))  # 设置格式
    
    utl_plotmap.time_ticks_formatter(ax_left,times,if_minor=True)
    ax_left.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))  # 将此y轴次刻度标签设置为1的倍数
    ax_left.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5))  # 将此y轴主刻度标签设置为5的倍数
    # ax_left.grid(axis='y', which='major', linewidth=0.8)
    # ax_left.grid(axis='both', which='both', linewidth=0.8)
    ax_left.grid(axis='both', which='major', linewidth=1)

    fig.add_axes(ax_left)

    utl_plotmap.time_ticks_formatter(ax_right,times,if_minor=True)

    ax_right.axis['right'].set_visible(True)
    ax_right.axis['right'].major_ticklabels.set_visible(True)
    ax_right.axis['right'].label.set_visible(True)
    ax_right.axis['right'].label.set_fontsize(15)
    ax_right.axis['right'].major_ticklabels.set_fontsize(15)
    ax_right.axis['right'].major_ticklabels.set_color('#067907')
    ax_right.set_ylabel(label_rightax,color='#067907')
    ax_right.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(5))  # 将此y轴次刻度标签设置为1的倍数
    ax_right.yaxis.set_major_locator(mpl.ticker.MultipleLocator(10))  # 将此y轴主刻度标签设置为5的倍数
    # ax_right.grid(axis='y', which='major', linewidth=0.8,color='#067907')
    ax_right.grid(axis='both', which='minor', ls='--',linewidth=0.4)

    plt.title(title_left, loc='left', fontsize=21)
    plt.title(title_right, loc='right', fontsize=15)

    ax_bottom = plt.axes([0.1, 0.16, .8, .12])
    ax_bottom.grid(axis='x', which='major', linewidth=1)
    ax_bottom.grid(axis='x', which='minor', ls='--',linewidth=0.4)
    ax_bottom.tick_params(length=5, axis='x')
    ax_bottom.tick_params(length=0, axis='y')
    ax_bottom.tick_params(axis='x', labelsize=15)
    ax_bottom.set_ylabel(label_bottomax, fontsize=15)
    ax_bottom.set_yticklabels([' '])
    ax_bottom.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H'))  # 设置格式
    utl_plotmap.time_ticks_formatter(ax_bottom,times,if_minor=True)

    if(add_tag):
        ax_bottom.text(0.00, -1.2, 'Powered by MetDig', transform=ax_bottom.transAxes, size=14,
                    color='gray', alpha=1.0, va='bottom',  ha='left', zorder=100)  # 左下角图的里面
    return fig, ax_left, ax_right, ax_bottom

@kwargs_wrapper
def skewt_pallete(figsize=(9, 9), title='', title_fontsize=23, forcast_info='', nmc_logo=False,
        bottom=1000,top=100,left=-40,right=60,add_tag=True,**kwargs):

    plt_base_env()  # 初始化字体中文等

    fig = plt.figure(figsize=figsize)

    skew = SkewT(fig, rotation=45)

    skew.ax.set_title(title, loc='left', fontsize=title_fontsize)

    skew.ax.set_ylim(bottom, top)
    skew.ax.set_xlim(left, right)

    if forcast_info:
        # skew.ax.text(0.01, 0.99, forcast_info, transform=skew.ax.transAxes, size=11, va='top',
        #              ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0))
        skew.ax.text(0.01, 1.005, forcast_info, transform=skew.ax.transAxes, size=11, va='bottom',
                     ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='white', pad=0.0))

    if nmc_logo:
        l, b, w, h = skew.ax.get_position().bounds
        utl.add_logo_extra_in_axes(pos=[l - 0.0, b + h - 0.075, .07, .07], which='nmc', size='Xlarge')  # 左上角
        # utl.add_logo_extra_in_axes(pos=[l + w - 0.1, b , .1, .1], which='nmc', size='Xlarge')  # 右下角
    if add_tag:
        skew.ax.text(0.00, 0.001, 'Powered by MetDig', transform=skew.ax.transAxes, size=14,
                    color='gray', alpha=1.0, va='bottom',  ha='left', zorder=100)  # 左下角图的里面
    return fig, skew

@kwargs_wrapper
def twod_pallete(figsize=(14, 12), title='', forcast_info='', nmc_logo=False,add_tag=True,logyaxis=False,
        bottom=1000,top=100,left=260,right=400,
        xlabel='K',ylabel='hPa',yticklabels=np.arange(1000, 100, -100),yticks=np.arange(1000, 100, -100),**kwargs):

    plt_base_env()  # 初始化字体中文等

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot()

    ax.set_title(title, loc='right', fontsize=23)

    # Adjust the y-axis to be logarithmic
    if(logyaxis):
        ax.set_yscale('symlog')
    ax.set_yticklabels(yticklabels)
    ax.set_yticks(yticks)
    ax.set_ylim(bottom, top)
    ax.set_ylabel(ylabel)

    ax.set_xlim(left, right)
    ax.set_xlabel(xlabel)


    if forcast_info:
        ax.text(0.01, 1.005, forcast_info, transform=ax.transAxes, size=11, va='bottom',
                ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='white', pad=0.0))

    if nmc_logo:
        l, b, w, h = ax.get_position().bounds
        # utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h, 0.07, 0.07], which='nmc', size='Xlarge')# 左上角
        utl.add_logo_extra_in_axes(pos=[l + w - 0.08, b + h - 0.1, .1, .1], which='nmc', size='Xlarge')  # 右上角

    if(add_tag):
        ax.text(0.00, 0.001, 'Powered by MetDig', transform=ax.transAxes, size=14,
                color='gray', alpha=1.0, va='bottom',  ha='left', zorder=100)  # 左下角图的里面
    return fig, ax