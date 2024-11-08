# -*- coding: utf-8 -*-

import xarray as xr
import numpy as np
import pandas as pd
import pyproj
import math
import metpy.interpolate as mpinterp

import inspect
from functools import wraps
import datetime


def cross_extent(st_point=[20, 120.0], ed_point=[50, 130.0], area=None):
    '''
    空间剖面根据起止点计算经纬度范围
    参考metpy.cross_section方法, 弧线方式计算经纬度范围后往外扩一度，以保证剖面线上的点都在范围内
    '''
    
    npts = len(st_point) // 2 # 线段数

    # 等经纬度坐标系
    crs = pyproj.crs.CRS.from_proj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

    lons = []
    lats = []
    for i in range(npts): # 循环每一段线
        _stp = st_point[i * 2:i * 2 + 2] # 开始点[lat, lon]
        _edp = ed_point[i * 2:i * 2 + 2] # 结束点[lat, lon]
        points1 = mpinterp.geodesic(crs, _stp, _edp, 100) 
        lons.append(points1[:, 0].min())
        lons.append(points1[:, 0].max())
        lats.append(points1[:, 1].min())
        lats.append(points1[:, 1].max())
    min_lon = min(lons)
    max_lon = max(lons)
    min_lat = min(lats)
    max_lat = max(lats)
    minor_extent = [math.floor(min_lon) - 1, math.ceil(max_lon) + 1, math.floor(min_lat) - 1, math.ceil(max_lat) + 1]
    if area == None:
        map_extent = [minor_extent[0], minor_extent[1], minor_extent[2], minor_extent[3]]
    else:
        map_extent = get_map_area(area)
    return minor_extent, map_extent

def point_to1dim(point):
    return np.array(point).flatten()


def get_map_area(area):
    if isinstance(area, list) or isinstance(area, tuple):
        if len(area) != 4:
            raise ValueError('area must be str or list(len=4) or tuple(len=4)')
        if area[0] > area[1] or area[2] > area[3]:
            raise ValueError('area must be (minlon, maxlon, minlat, maxlat)')
        return area
    elif isinstance(area, str):
        area_region = {
            # '全国': (60, 145, 15, 55),
            '全球': (-179, 179, -89, 89),
            '南半球': (-179, 179, -89, 0),
            '北半球': (-179, 179, 0, 89),
            '全国': (70, 140, 15, 55),
            '中国及周边': (50, 160, 0, 70),
            '华北': (102, 135, 25, 50),
            '东北': (103, 140, 32, 58),
            '华东': (107, 130, 20, 41),
            '华中': (100, 123, 22, 42),
            '华南': (95, 126, 12, 35),
            '西南': (90, 113, 18, 38),
            '江南': (107, 124, 24, 31),
            '江淮': (112, 123, 29, 35),
            '黄淮': (108, 124, 32, 38),
            '西北': (89, 115, 27, 47),
            '新疆': (70, 101, 30, 52),
            '青藏': (68, 105, 18, 46),
            '东北冷涡':(100,150,30,65),
            '西南涡':(96,124,18,40),
            '南海':(105,125,0,25),
            '欧亚大陆':(10, 170, 0, 80),
            # '江南': (),
            # '江淮': (),
            # '西欧': (),
            # '欧洲': (),
            # '北美': (),
            # '南美': (),
            # '南亚': (),
            # '东南亚': (),
            # '中亚': (),
            # '东北亚': (),
            # '北非': (),
            # '南非': (),
            # '澳洲': (),
        }

        if area not in area_region.keys():
            raise ValueError('Can not get area definition and map_extent(parameter) is empty!')
        return area_region[area]
    else:
        raise ValueError('area must be str or list(len=4) or tuple(len=4)')


def mask_terrian(psfc, stda_input, get_terrain=False):
    if psfc is None or stda_input is None:
        return stda_input
    # time dtime 维度取交集
    time_dim = list(set(psfc['time'].values.tolist()) & set(stda_input['time'].values.tolist()))
    time_dim = pd.Series(pd.to_datetime(time_dim)).to_list()
    time_dim.sort()
    dtime_dim = list(set(psfc['dtime'].values.tolist()) & set(stda_input['dtime'].values.tolist()))
    dtime_dim.sort()
    psfc = psfc.sel(time=time_dim, dtime=dtime_dim)
    stda_input = stda_input.sel(time=time_dim, dtime=dtime_dim)
    #输入的任何维度气压坐标系的stda均能够mask
    if((stda_input.lon.shape[0]==1) and (stda_input.lat.shape[0]==1)):
        psfc_new=psfc.values.repeat(stda_input['level'].size, axis=1)
    else:
        psfc_new = psfc.interp(lon=stda_input['lon'].values,
                           lat=stda_input['lat'].values,
                           kwargs={'fill_value': None},
                           ).values.repeat(stda_input['level'].size, axis=1)
    pressure=stda_input.level.broadcast_like(stda_input)
    if get_terrain:
        return (pressure-psfc_new).where(pressure-psfc_new > 0)  # 保留psfc-level>=0的，小于0的赋值成nan
    else:
        return stda_input.where(pressure-psfc_new <= 0)  # 保留psfc-level>=0的，小于0的赋值成nan


class date_init(object):
    '''
    针对时间参数为None的情况，利用初始化方法(默认为default_set)初始化时间
    Example:
        from metdig.onestep.lib.utility import date_init  

        # 用默认方法初始化
        @date_init('init_time')
        def onestep_func(init_time):
            pass  

        # 指定初始化
        @date_init('init_time', method=yourmethod)
        def onestep_func(init_time):
            pass
    '''
    def default_set(args, defaults):
        '''默认初始化函数'''
        sys_time = datetime.datetime.now()
        if sys_time.hour >= 14:
            # 今天08时
            dt = datetime.datetime(sys_time.year, sys_time.month, sys_time.day, 8)
        elif sys_time.hour >= 2:
            # 昨天20时
            dt = datetime.datetime(sys_time.year, sys_time.month, sys_time.day, 20) - datetime.timedelta(days=1)
        else:
            # 昨天08时
            dt = datetime.datetime(sys_time.year, sys_time.month, sys_time.day, 8) - datetime.timedelta(days=1)
        return dt

    def series_1_36_set(args, defaults):
        '''1小时间隔36个时次初始化时间序列'''
        dt1 = date_init.default_set(args, defaults)
        return [dt1 - datetime.timedelta(hours=i) for i in range(36)]

    def special_series_set(args, defaults):
        '''特殊初始化，如果是data_source=era5则返回固定的时间序列'''
        if ('data_source' in args.keys() and args['data_source'] == 'era5') or \
                ('data_source' not in args.keys() and 'data_source' in defaults.keys() and defaults['data_source'] == 'era5'):
            # 如果传参进来的有且为era5，或者，没有传参且默认参数为era5
            dt = date_init.default_set(args, defaults)
            return [
                datetime.datetime(2020, 7, 25, 16),  # 8
                datetime.datetime(2020, 7, 25, 19),  # 11
                datetime.datetime(2020, 7, 25, 22),  # 14
                datetime.datetime(2020, 7, 26, 1),  # 17
                datetime.datetime(2020, 7, 26, 4),  # 20
                datetime.datetime(2020, 7, 26, 7),  # 23
            ]
        else:
            return date_init.default_set(args, defaults)
        pass

    def __init__(self, *var_args, method=default_set):
        self.var_args = var_args
        self.method = method

    def __call__(self, func):
        @ wraps(func)
        def wrapper(*argv, **kwargs):
            sig = inspect.signature(func)
            defaults = {name: sig.parameters[name].default for name in sig.parameters
                        if sig.parameters[name].default is not inspect.Parameter.empty}  # 默认值
            bound_args = sig.bind(*argv, **kwargs)  # 手动传进来的值
            for var_name in self.var_args:
                if var_name not in defaults.keys():
                    raise Exception('{} set error! please set correct parm on data_init!'.format(var_name))

                dt = kwargs.pop(var_name, None)
                if dt is None:
                    dt = self.method(bound_args.arguments, defaults)
                if isinstance(dt, str):
                    if len(dt) == 10:
                        dt = datetime.datetime.strptime(dt, '%Y%m%d%H')
                    elif len(dt) == 8:
                        dt = datetime.datetime.strptime(dt, '%y%m%d%H')
                    else:
                        raise Exception('time must be datetime or str like 2001010100(%Y%m%d%H) or str like 01010100(%y%m%d%H)')
                kwargs[var_name] = dt
            return func(*argv, **kwargs)
        return wrapper
