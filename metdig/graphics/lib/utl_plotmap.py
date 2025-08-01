# -*- coding: utf-8 -*-

import sys
import pkg_resources
import os
import math
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl

from cartopy.io.shapereader import Reader
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import PathPatch
import matplotlib.patheffects as mpatheffects
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import metdig.graphics.lib.utility as utl

import shapefile
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import Point as ShapelyPoint
from  metdig.graphics.lib.utility import kwargs_wrapper

pkg_name = 'metdig.graphics'


def indicate_points(ax,sta_info,stda=None,size=20,zorder=10,ha='left',va_text='top',color='black',point_color='black'):
    #if_adjust [bool] 是否自适应不相互重叠 #需要安装 pip install adjustText
    #sta_info={'lon':[94.123,97.123,100.123,103.123],'lat':[29.123,30.123,30.13,30.123],'id':['测试1','测试2','测试3','测试4']}
    alltxt=[]
    for iid,id in enumerate(sta_info['id']):
        if(stda is None):
            s=ax.scatter(sta_info['lon'][iid],sta_info['lat'][iid],color=point_color,zorder=zorder)
            s.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                mpatheffects.Normal()])
            t=ax.text(sta_info['lon'][iid],sta_info['lat'][iid],str(sta_info['name'][iid]),size=size,zorder=zorder, ha=ha,va=va_text,color=color)
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                mpatheffects.Normal()])
            alltxt.append(t)
        if(stda is not None):
            s=ax.scatter(sta_info['lon'][iid],sta_info['lat'][iid],color=point_color,zorder=zorder)
            s.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                    mpatheffects.Normal()])

            num_area=stda.interp(lon=('points',[sta_info['lon'][iid]]), lat=('points', [sta_info['lat'][iid]]))
            num = ax.text(sta_info['lon'][iid],sta_info['lat'][iid],'%.1f ' % np.squeeze(num_area.values)+'\n'+sta_info['id'][iid],
                family='SimHei', ha=ha, va=va_text, size=size-2, zorder=zorder)

            num.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                mpatheffects.Normal()])
            alltxt.append(num)
    return(alltxt)

def shp2clip_pro_id(originfig, ax, shpfile, num_list):
    sf = shapefile.Reader(shpfile)
    vertices = []  # 这块是已经修改的地方
    codes = []  # 这块是已经修改的地方

    shape_recs = sf.shapeRecords()

    for i in range(len(shape_recs)):
        # if shape_rec.record[3] == region:  # 这里需要找到和region匹配的唯一标识符，record[]中必有一项是对应的。

        #if(len(shape_rec.record) ==1):continue

        if i in num_list:  # 这块是已经修改的地方
            shape_rec = shape_recs[i]
            pts = shape_rec.shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]
            path = Path(vertices, codes)
            # extents = path.get_extents()
            patch = PathPatch(path, transform=ax.transData, facecolor='none', edgecolor='black')
    for contour in originfig.collections:
        contour.set_clip_path(patch)
    
    try:
        clabels=originfig.labelTextsList
        if(clabels is not None):
            clip_map_shapely = ShapelyPolygon(vertices)
            for text_object in clabels:
                if not clip_map_shapely.contains(ShapelyPoint(text_object.get_position())):
                    text_object.set_visible(False)
    except:
        return path, patch

    return path, patch

def shp2clip_by_region_name(originfig, ax, region_name_list):
    province = pkg_resources.resource_filename('meteva', "resources/maps/Province")

    province_ch_name = ["北京","天津","河北","山西","内蒙古",
                        "辽宁","吉林","黑龙江","上海","江苏",
                        "浙江","安徽","福建","江西", "山东",
                        "河南","湖北","湖南","广东","广西",
                        "海南","重庆","四川","贵州","云南",
                        "西藏","陕西","甘肃","青海","宁夏",
                        "新疆","台湾","香港","澳门"]

    province_name =["beijing","tianjin","hebei","shanxi","neimenggu",
                    "liaoning", "jilin", "heilongjiang", "shanghai", "jiangsu",
                    "zhejiang", "anhui", "fujian", "jiangxi", "shandong",
                    "henan", "hubei", "hunan", "guangdong", "guangxi",
                    "hainan", "chongqing", "sichuan", "guizhou", "yunnan",
                    "xizang", "shanxi", "gansu", "qinghai", "ningxia",
                    "xinjiang", "taiwan", "xianggang", "aomen"]


    region_id_list = []
    #print(region_name_list)
    for region_name in region_name_list:
        if region_name.lower()=="china" or region_name=="中国":
            region_id_list.extend(np.arange(34).tolist())
        else:
            for i in range(len(province_name)):
                if region_name.find(province_ch_name[i])>=0:
                    region_id_list.append(i)
                if region_name.lower().find(province_name[i])>=0:
                    region_id_list.append(i)

    #print(region_id_list)
    region_id_list = list(set(region_id_list))
    print(province)
    shp2clip_pro_id(originfig, ax, province, region_id_list)


def time_ticks_formatter(ax,times,if_minor=False):
    times=pd.to_datetime(times)
    hours_total=np.abs((times[len(times)-1]-times[0]).total_seconds()/3600.)
    '''
    if(hours_total > 84):
        ax.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 20)))  # 单位是小时
        if if_minor:
            ax.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=(8, 14, 20, 2)))  # 单位是小时
    elif(hours_total > 24):
        ax.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 14, 20, 2)))  # 单位是小时
        if if_minor:
            ax.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=(8, 11, 14, 17, 20, 23, 2, 5)))  # 单位是小时
    elif(hours_total > 12):
        ax.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 11, 14, 17, 20, 23, 2, 5)))  # 单位是小时
        if if_minor:
            ax.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=list(range(0,24,1))))  # 单位是小时
    else:
        ax.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=list(range(0,24,1))))  # 单位是小时
    '''
    # 时间间隔调密
    if(hours_total > 84):
        ax.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 14, 20, 2)))  # 单位是小时
        if if_minor:
            ax.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=(8, 11, 14, 17, 20, 23, 2, 5)))  # 单位是小时
    elif(hours_total > 24):
        ax.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 11, 14, 17, 20, 23, 2, 5)))  # 单位是小时
        if if_minor:
            ax.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=list(range(0,24,1))))  # 单位是小时
    else:
        ax.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=list(range(0,24,1))))  # 单位是小时



def lon2txt(lon, fmt='%g'):
    """
    Format the longitude number with degrees.

    :param lon: longitude
    :param fmt:
    :return:

    :Examples:
    >>> lon2txt(135)
     '135°E'
    >>> lon2txt(-30)
     '30°W'
    >>> lon2txt(250)
     '110°W'
    """
    lon = (lon + 360) % 360
    if lon > 180:
        lonlabstr = u'%s°W' % fmt
        lonlab = lonlabstr % abs(lon - 360)
    elif lon < 180 and lon != 0:
        lonlabstr = u'%s°E' % fmt
        lonlab = lonlabstr % lon
    else:
        lonlabstr = u'%s°' % fmt
        lonlab = lonlabstr % lon
    return lonlab


def lat2txt(lat, fmt='%g'):
    """
    Format the latitude number with degrees.
    :param lat:
    :param fmt:
    :return:

    :Examples:
    >>> lat2txt(60)
     '60°N'
    >>> lat2txt(-30)
     '30°S'
    """
    if lat < 0:
        latlabstr = '%s°S' % fmt
        latlab = latlabstr % abs(lat)
    elif lat > 0:
        latlabstr = '%s°N' % fmt
        latlab = latlabstr % lat
    else:
        latlabstr = '%s°' % fmt
        latlab = latlabstr % lat
    return latlab

def auto_create_xytick(map_extent, xy_equal_space=True, xy_start_use_extent=True):
    """自动生成合适的x,y轴刻度

    Args:
        map_extent (tuple): 区域范围，(lon_min, lon_max, lat_min, lat_max)
        xy_equal_space (bool, optional): 经度方向和维度方向的刻度间隔是否保持一致. Defaults to True.
        xy_start_use_extent (bool, optional): 经度方向和维度方向的起始刻度是否使用map_extentt. Defaults to True.

    Returns:
        tuple: xticks, yticks
    """
    tickstep = [0.1, 0.2, 0.5, 1, 2, 5, 10, 15, 20, 30, 40, 50]
    xstep = None
    ystep = None
    for step in tickstep: # 从细分辨率开始找，找到合适的为止
        _xticks = np.arange(-360, 360+0.0001, step, dtype='float32')
        _xticks = _xticks[(_xticks >= map_extent[0]) & (_xticks <= map_extent[1])]
        if step >= 1:
            # 整数间隔的最多n个刻度
            if len(_xticks) <= 10:
                xstep = step
                break
        else:
            # 1位小数间隔的最多n个刻度
            if len(_xticks) <= 6:
                xstep = step
                break
    for step in tickstep: # 从细分辨率开始找，找到合适的为止
        _yticks = np.arange(-90, 90.0001, step, dtype='float32')
        _yticks = _yticks[(_yticks >= map_extent[2]) & (_yticks <= map_extent[3])]
        if step >= 1:
            # 整数间隔的最多n个刻度
            if len(_yticks) <= 10: 
                ystep = step
                break
        else:
            # 1位小数间隔的最多n个刻度
            if len(_yticks) <= 6:
                ystep = step
                break
    _xticks = None
    _yticks = None
    if xstep is not None and ystep is not None:
        if xy_equal_space:
            # 保证y轴刻度步长和x轴刻度步长相同，用大的步长的那个
            if xstep < ystep:
                xstep = ystep
            else:
                ystep = xstep
        if xy_start_use_extent:
            _xticks = np.arange(map_extent[0], map_extent[1]+0.0001, xstep, dtype='float32')
            _xticks = _xticks[(_xticks >= map_extent[0]) & (_xticks <= map_extent[1])]
            _yticks = np.arange(map_extent[2], map_extent[3]+0.0001, ystep, dtype='float32')
            _yticks = _yticks[(_yticks >= map_extent[2]) & (_yticks <= map_extent[3])]
        else:
            _xticks = np.arange(-360, 360+0.0001, xstep, dtype='float32')
            _xticks = _xticks[(_xticks >= map_extent[0]) & (_xticks <= map_extent[1])]
            _yticks = np.arange(-90, 90.0001, ystep, dtype='float32')
            _yticks = _yticks[(_yticks >= map_extent[2]) & (_yticks <= map_extent[3])]
    # print(xstep, ystep)
    # print(map_extent)
    # print(_xticks)
    # print(_yticks)
    return _xticks, _yticks
    
@kwargs_wrapper
def add_ticks_auto(ax, map_extent, xticks=None, yticks=None, labelsize=16, add_grid=False, xy_equal_space=True, xy_start_use_extent=True,**kwargs):
    """自动生成等经纬度刻度标签

    Args:
        ax (_type_): ax对象
        xticks (list, optional): 经度方向的刻度，如果外部给定则不自动生成. Defaults to None.
        yticks (list, optional): 纬度方向的刻度，如果外部给定则不自动生成. Defaults to None.
        map_extent (tuple, optional): 区域范围，(lon_min, lon_max, lat_min, lat_max). Defaults to None.
        labelsize (int, optional): 刻度标签大小. Defaults to 16.
        add_grid (bool, optional): 是否加入网格线. Defaults to False.
        xy_equal_space (bool, optional): 经度方向和维度方向的刻度间隔是否保持一致，当xticks和yticks均为None时才生效. Defaults to True.
        xy_start_use_extent (bool, optional): 经度方向和维度方向的起始刻度是否使用ax的extent，当xticks和yticks均为None时才生效. Defaults to True.
    """

    # 自动生成刻度
    _xticks, _yticks = auto_create_xytick(map_extent, xy_equal_space=xy_equal_space, xy_start_use_extent=xy_start_use_extent)

    # 如果给了刻度，则不使用自动生成的
    if xticks is not None:
        _xticks = np.array(xticks, dtype='float32')
    if yticks is not None:
        _yticks = np.array(yticks, dtype='float32')
    if _xticks is not None:
        if len(_xticks) == 1:
            xfmt = '%.1f'
        else:
            xfmt = '%.0f' if abs(_xticks[1] - _xticks[0]) >= 1 else '%.1f'
        _xlabels = list(map(lambda _: lon2txt(_, fmt=xfmt), _xticks))
        ax.set_xticks(_xticks, crs=ccrs.PlateCarree())
        ax.set_xticklabels(_xlabels)
        ax.tick_params(axis='x', labelsize=labelsize, **kwargs)
    if _yticks is not None:
        if len(_yticks) == 1:
            yfmt = '%.1f'
        else:
            yfmt = '%.0f' if abs(_yticks[1] - _yticks[0]) >= 1 else '%.1f'
        _ylabels = list(map(lambda _: lat2txt(_, fmt=yfmt), _yticks))
        ax.set_yticks(_yticks, crs=ccrs.PlateCarree())
        ax.set_yticklabels(_ylabels)
        ax.tick_params(axis='y', labelsize=labelsize, **kwargs)

    if add_grid and _xticks is not None and _yticks is not None:
        ax.gridlines(crs=ccrs.PlateCarree(), xlocs=_xticks, ylocs=_yticks, linewidth=1, color='gray', alpha=0.5, linestyle='--', zorder=100)

@kwargs_wrapper
def add_ticks(ax, xticks=None, yticks=None, labelsize=16, crs=ccrs.PlateCarree(), add_grid=False ,**kwargs):
    if xticks is not None:
        xticks = np.array(xticks)
        xticks = np.where(xticks > 180, xticks - 360, xticks) # 0-360转-180 180
        ax.set_xticks(xticks, crs=crs)
        lon_formatter = LongitudeFormatter(zero_direction_label=False)
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.tick_params(axis='x', labelsize=labelsize, **kwargs)
    if yticks is not None:
        ax.set_yticks(yticks, crs=crs)
        lat_formatter = LatitudeFormatter()
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.tick_params(axis='y', labelsize=labelsize, **kwargs)
    
    if add_grid:
        ax.gridlines(crs=crs, xlocs=xticks, ylocs=yticks, linewidth=1, color='gray', alpha=0.5, linestyle='--', zorder=100)


@kwargs_wrapper
def add_ticks_NorthPolarStereo(ax, map_extent=[-180,180,0,90], add_grid=True, add_ticks=True):
    if add_grid:
        gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=100)
        gl.xlocator = mpl.ticker.FixedLocator(np.arange(-180, 181, 30))
        gl.ylocator = mpl.ticker.FixedLocator([0, 15, 30, 45, 60, 75, 90])
    if add_ticks:
        # for label alignment
        va = 'center' # also bottom, top
        ha = 'center' # right, left
        # degree_symbol=u'\u00B0'
         # for locations of (meridional/longitude) labels
        lond = np.arange(-150, 181, 30)
        latd = np.full(len(lond),map_extent[2])
        for (alon, alat) in zip(lond, latd):
            projx1, projy1 = ax.projection.transform_point(alon, alat, ccrs.Geodetic())
            if alon>0 and alon<180:
                ha = 'left'
                va = 'center'
            if alon<0:
                ha = 'right'
                va = 'center'
            if np.abs(alon-180)<0.01:
                ha = 'center'
                va = 'bottom'
            if alon==0.:
                ha = 'center'
                va = 'top'
            if (alon<360.):
                alon = int(alon)
                if alon > 0:
                    txt = f'{alon}°E'
                else:
                    txt = f'{abs(alon)}°W'
                ax.text(projx1, projy1, txt, va=va, ha=ha, color='black')
        # for locations of (meridional/longitude) labels
        # select longitude: 315 for label positioning
        # lond2 = 315*np.ones(len(lond))
        latd2 = np.array([0, 15, 30, 45, 60, 75, 90])
        latd2 = latd2[latd2>=map_extent[2]]
        lond2 =  315*np.ones(len(latd2))

        va, ha = 'center', 'center'
        for (alon, alat) in zip(lond2, latd2):
            projx1, projy1 = ax.projection.transform_point(alon, alat, ccrs.Geodetic())
            # txt =  ' {0} '.format(str(int(alat)))+degree_symbol
            txt = f'{int(alat)}°N'
            ax.text(projx1, projy1, txt, va=va, ha=ha, color='black') 

    
@kwargs_wrapper
def forcast_info(ax, x=0.1 ,y=0.99 ,info=None ,transform=None , size=12, va='top',
                    ha='left', bbox=dict(facecolor='#FFFFFFCC', edgecolor='black', pad=3.0),zorder=20,**kwargs):
    ax.text(x, y, info, transform=ax.transAxes, size=size, va=va, ha=ha, bbox=bbox,zorder=zorder) 

@kwargs_wrapper
def add_china_map_2cartopy_public(ax, name='province', facecolor='none',
                                  edgecolor='c', lw=2,crs=ccrs.PlateCarree(), **kwargs):
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
    names = {
            'world':'worldmap',
            'nation': "NationalBorder", 
             'province': "Province",
            #  'county': "County",  # 无资源，暂时注释
             'river': "hyd1_4l",
             'river_high': "hyd2_4l",
             'coastline': 'ne_10m_coastline'}

    # get shape filename
    shpfile = pkg_resources.resource_filename(pkg_name, "resources/shapefile/" + names[name] + ".shp")

    # add map
    ax.add_geometries(
        Reader(shpfile).geometries(), 
        facecolor=facecolor, edgecolor=edgecolor, lw=lw,crs=crs, **kwargs)


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


def adjust_extent_to_aspect_ratio(map_extent, target_aspect_ratio):
    """放大地图的范围，使其满足长宽比例

    Args:
        map_extent (list): 地图范围 [开始经度，结束经度，开始纬度，结束纬度]，如[70, 140, 15, 55]
        target_aspect_ratio (float): 长宽比例,如1.5

    Returns:
        list: 新的地图范围
    """
    west, east, south, north = map_extent
    center_lon = (west + east) / 2
    center_lat = (south + north) / 2

    current_width = east - west
    current_height = north - south

    # 计算当前长宽比
    current_aspect_ratio = current_width / current_height

    if current_aspect_ratio < target_aspect_ratio:
        # 需要扩大宽度
        half_diff = (target_aspect_ratio * current_height - current_width) / 2
        west -= half_diff
        east += half_diff
    elif current_aspect_ratio > target_aspect_ratio:
        # 需要扩大高度
        half_diff = ((current_width / target_aspect_ratio) - current_height) / 2
        south -= half_diff
        north += half_diff

    # 确保边界在合法范围内
    west = max(west, -180)
    east = min(east, 180)
    south = max(south, -90)
    north = min(north, 90)

    return [math.floor(west), math.ceil(east), math.floor(south), math.ceil(north)]


def add_cartopy_background(ax, name='RD'):
    # http://earthpy.org/cartopy_backgroung.html
    # C:\ProgramData\Anaconda3\Lib\site-packages\cartopy\data\raster\natural_earth
    bg_dir = pkg_resources.resource_filename(pkg_name, 'resources/backgrounds/')
    os.environ["CARTOPY_USER_BACKGROUNDS"] = bg_dir
    ax.background_img(name=name, resolution='high')


def add_city_on_map(ax, map_extent=None, size=7, small_city=False, zorder=10,city_type='provincial_capital',city_slt=None, **kwargs):
    """
    :param ax: `matplotlib.figure`, The `figure` instance used for plotting
    :param x: x position padding in pixels
    :city_type: str, provincial_capital or county
    :city_slt: list, 指定显示的城市
    :param kwargs:
    :return: `matplotlib.image.FigureImage`
             The `matplotlib.image.FigureImage` instance created.
    """
    if map_extent is None:
        map_extent = list(ax.get_xlim()) + list(ax.get_ylim())

    dlon = map_extent[1] - map_extent[0]
    dlat = map_extent[3] - map_extent[2]

    fnames={'provincial_capital':'city_province.csv',
           'county':'county.csv'}
    try:
        fname = fnames[city_type]
        fpath = "resources/stations/" + fname
    except KeyError:
        raise ValueError('can not find the file city_province.000 in the resources')

    city = pd.read_csv(pkg_resources.resource_filename(pkg_name, fpath), encoding='gbk', comment='#')

    lon = city['lon'].values
    lat = city['lat'].values
    city_names = city['Name'].values

    # 步骤一（替换sans-serif字体） #得删除C:\Users\HeyGY\.matplotlib 然后重启vs，刷新该缓存目录获得新的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if(city_type == 'provincial_capital'):
        for i in range(0, len(city_names)):
            if((lon[i] > map_extent[0] + dlon * 0.05) and (lon[i] < map_extent[1] - dlon * 0.05) and
            (lat[i] > map_extent[2] + dlat * 0.05) and (lat[i] < map_extent[3] - dlat * 0.05)):
                if (city_slt == None):
                    if(city_names[i] != '香港' and city_names[i] != '南京' and city_names[i] != '石家庄' and city_names[i] != '天津'):
                        r = city_names[i]
                        t = ax.text(lon[i], lat[i], city_names[i], family='SimHei', ha='right', va='top', size=size, zorder=zorder, **kwargs)
                    else:
                        t = ax.text(lon[i], lat[i], city_names[i], family='SimHei', ha='left', va='top', size=size, zorder=zorder, **kwargs)
                    t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                        mpatheffects.Normal()])
                    ax.scatter(lon[i],lat[i], c='black', s=25, zorder=zorder, **kwargs)
                else:
                    for islt in city_slt:
                        if(city_names[i]==islt):
                            t = ax.text(lon[i], lat[i], city_names[i], family='SimHei', ha='left', va='top', size=size, zorder=zorder, **kwargs)
                            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                        mpatheffects.Normal()])
                            ax.scatter(lon[i],lat[i], c='black', s=25, zorder=zorder, **kwargs)
    else:
        for i in range(0, len(city_names)):
            if((lon[i] > map_extent[0] + dlon * 0.05) and (lon[i] < map_extent[1] - dlon * 0.05) and
            (lat[i] > map_extent[2] + dlat * 0.05) and (lat[i] < map_extent[3] - dlat * 0.05)):
                if (city_slt == None):
                    t = ax.text(lon[i]+(map_extent[1]-map_extent[0])*0.01, lat[i], city_names[i], family='SimHei', ha='left', va='top', size=size, zorder=zorder, **kwargs)
                    t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                        mpatheffects.Normal()])
                    ax.scatter(lon[i], lat[i], c='black', s=25, zorder=zorder, **kwargs)
                else:
                    for islt in city_slt:
                        if(city_names[i]==islt):
                            t = ax.text(lon[i], lat[i], city_names[i], family='SimHei', ha='left', va='top', size=size, zorder=zorder, **kwargs)
                            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                        mpatheffects.Normal()])
                            ax.scatter(lon[i], lat[i], c='black', s=25, zorder=zorder, **kwargs)
    return

def add_south_china_sea_plt(map_extent=[107, 120, 2, 20], pos=[0.1, 0.1, .2, .4], **kwargs):

    # draw main figure
    plotcrs = ccrs.PlateCarree(central_longitude=100.)
    ax = plt.axes(pos, projection=plotcrs)
    datacrs = ccrs.PlateCarree()
    ax.set_extent(map_extent, crs=datacrs)
    ax.coastlines('50m', edgecolor='black', linewidth=0.5, zorder=50)
    add_china_map_2cartopy_public(ax, name='nation', edgecolor='black', lw=0.8, zorder=40)
    '''
    ax.add_feature(cfeature.OCEAN)
    add_cartopy_background(ax, name='RD')  # ax.background_img(name='RD', resolution='high')
    '''
    ax.add_feature(cfeature.LAND, facecolor='#EBDBB2')
    ax.add_feature(cfeature.OCEAN, facecolor='#C8EBFA')
    return ax


def add_south_china_sea_png(pos=[0.1, 0.1, .2, .4], name='simple', **kwargs):
    fname_suffix = {
        'simple': 'simple.png',
        'RD': 'RD.png',
        'white': 'white.png',
    }
    try:
        fname = fname_suffix[name]
        fpath = "resources/south_china/" + fname
    except KeyError:
        raise ValueError('Unknown south_china name or selection')
    img = plt.imread(pkg_resources.resource_filename(pkg_name, fpath))

    ax = plt.axes(pos)
    ax.imshow(img, zorder=0)
    ax.axis('off')
    return ax

def create_south_china_png(outfile='./south_china.png'):
    # 创建南海静态图
    fig = plt.figure(figsize=(0.9, 1.24))
    ax = fig.add_subplot(projection=ccrs.PlateCarree())
    datacrs = ccrs.PlateCarree()
    ax.set_extent([107, 120, 2, 20], crs=datacrs)
    ax.coastlines('50m', edgecolor='black', linewidth=0.5, zorder=50)
    add_china_map_2cartopy_public(ax, name='nation', edgecolor='black', lw=0.8, zorder=40)

    # ax.add_feature(cfeature.OCEAN)
    # add_cartopy_background(ax, name='RD')  # ax.background_img(name='RD', resolution='high')
    ax.add_feature(cfeature.LAND, facecolor='#EBDBB2')
    ax.add_feature(cfeature.OCEAN, facecolor='#C8EBFA')

    from metdig.graphics.lib.utility import get_imgbuf_from_fig
    import PIL
    imagebuf = get_imgbuf_from_fig(fig)
    imagebuf = imagebuf[2:-2, 2:-2, :] # 去掉2个像素的黑边框
    PIL.Image.fromarray(imagebuf.astype(np.uint8), mode='RGBA').save(outfile)

    # plt.savefig('./south_china.png', dpi=200, bbox_inches='tight')

    plt.close()


def add_city_values_on_map(ax, data, map_extent=None, size=13, zorder=10, cmap=None, transform=ccrs.PlateCarree(), small_city=False,**kwargs):
    
    if map_extent is None:
        map_extent = list(ax.get_xlim()) + list(ax.get_ylim())
        
    dlon = map_extent[1] - map_extent[0]
    dlat = map_extent[3] - map_extent[2]
    # province city
    try:
        if(small_city):
            fname = 'county.csv'
        else:
            fname = 'city_province.csv'
        fpath = "resources/stations/" + fname
    except KeyError:
        raise ValueError('can not find the file city_province.csv in the resources')

    city = pd.read_csv(pkg_resources.resource_filename(pkg_name, fpath), encoding='gbk', comment='#')

    lon = city['lon'].values
    lat = city['lat'].values
    city_names = city['Name'].values

    number_city = data.interp(lon=('points', lon), lat=('points', lat))

    # 步骤一（替换sans-serif字体） #得删除C:\Users\HeyGY\.matplotlib 然后重启vs，刷新该缓存目录获得新的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    if(small_city):
        for i in range(0, len(city_names)):
            if((lon[i] > map_extent[0] + dlon * 0.05) and (lon[i] < map_extent[1] - dlon * 0.05) and
            (lat[i] > map_extent[2] + dlat * 0.05) and (lat[i] < map_extent[3] - dlat * 0.05)):
                num = ax.text(lon[i],lat[i],
                            '%.1f' % np.squeeze(number_city.values)[i],
                            family='SimHei', ha='left', va='bottom', size=size, zorder=zorder, transform=transform, **kwargs)
                num.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                    mpatheffects.Normal()])
    else:                                
        for i in range(0, len(city_names)):
            if((lon[i] > map_extent[0] + dlon * 0.05) and (lon[i] < map_extent[1] - dlon * 0.05) and
            (lat[i] > map_extent[2] + dlat * 0.05) and (lat[i] < map_extent[3] - dlat * 0.05)):
                if((np.array(['香港', '南京', '石家庄', '天津', '济南', '上海']) != city_names[i]).all()):
                    r = city_names[i]
                    num = ax.text(lon[i],lat[i],
                                '%.1f' % np.squeeze(number_city.values)[i],
                                family='SimHei', ha='right', va='bottom', size=size, zorder=zorder, transform=transform, **kwargs)
                else:
                    num = ax.text(lon[i],lat[i],
                                '%.1f' % np.squeeze(number_city.values)[i],
                                family='SimHei', ha='left', va='bottom', size=size, zorder=zorder, transform=transform, **kwargs)
                num.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                                    mpatheffects.Normal()])
    return
