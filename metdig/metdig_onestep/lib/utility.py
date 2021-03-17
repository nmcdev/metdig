# -*- coding: utf-8 -*-

import xarray as xr
import numpy as np

import inspect
from functools import wraps
import datetime


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
            '全国': (70, 140, 15, 55),
            '中国及周边': (50, 160, 0, 70),
            '华北': (103, 129, 30, 50),
            '东北': (103, 140, 32, 58),
            '华东': (107, 130, 20, 41),
            '华中': (100, 123, 22, 42),
            '华南': (100, 126, 12, 30),
            '西南': (90, 113, 18, 38),
            '西北': (89, 115, 27, 47),
            '新疆': (70, 101, 30, 52),
            '青藏': (68, 105, 18, 46),
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


def mask_terrian(psfc, level, stda_input):
    psfc_new = psfc.interp(lon=stda_input['lon'].values,
                           lat = stda_input['lat'].values,
                           kwargs = {'fill_value': None},
                           )
    return stda_input.where(psfc_new.values - level >= 0)  # 保留psfc-level>=0的，小于0的赋值成nan


class date_init(object):
    '''
    针对时间参数为None的情况，利用初始化方法(默认为default_set)初始化时间
    Example:
        from metdig.metdig_onestep.lib.utility import date_init  

        # 用默认方法初始化
        @date_init('init_time')
        def onestep_func(init_time):
            pass  
        
        # 指定初始化
        @date_init('init_time', method=yourmethod)
        def onestep_func(init_time):
            pass
    '''
    def default_set(**kwargs):
        # 默认初始化函数
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
    
    def series_1_36_set(**kwargs):
        # 1小时间隔36个时次初始化时间序列
        dt1 = date_init.default_set(**kwargs)
        return [dt1 - datetime.timedelta(hours=i) for i in range(36)]
    
    def special_series_set(**kwargs):
        # 特殊初始化，如果是data_source=era5则返回固定的时间序列
        if kwargs['data_source'] == 'era5':
            dt = date_init.default_set(**kwargs)
            return [
                datetime.datetime(2020, 7, 25, 16), # 8
                datetime.datetime(2020, 7, 25, 19), # 11
                datetime.datetime(2020, 7, 25, 22), # 14
                datetime.datetime(2020, 7, 26, 1), # 17
                datetime.datetime(2020, 7, 26, 4), # 20
                datetime.datetime(2020, 7, 26, 7), # 23
            ]
        else:
            return date_init.default_set(**kwargs)
        pass


    def __init__(self, *var_args, method=default_set):
        self.var_args = var_args
        self.method = method

    def __call__(self, func):
        func_args, func_varargs, func_keywords, func_defaults = inspect.getargspec(func)
        @ wraps(func)
        def wrapper(**kwargs):    
            for var_name in self.var_args:
                if var_name not in func_args:
                    raise Exception('{} set error! please set correct parm on data_init!'.format(var_name))

                dt = kwargs.pop(var_name, None)
                if dt is None:
                    dt = self.method(**kwargs)
                if isinstance(dt, str):
                    if len(dt) == 10:
                        dt = datetime.datetime.strptime(dt, '%Y%m%d%H')
                    elif len(dt) == 8:
                        dt = datetime.datetime.strptime(dt, '%y%m%d%H')
                    else:
                        raise Exception('time must be datetime or str like 2001010100 or str like 01010100')
                kwargs[var_name] = dt
            return func(**kwargs)
        return wrapper
