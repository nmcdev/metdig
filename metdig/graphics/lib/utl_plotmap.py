# -*- coding: utf-8 -*-

import sys
import pkg_resources
import os
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
