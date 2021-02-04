# -*- coding: utf-8 -*-

import xarray as xr
import numpy as np

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



def check_init_time(func):
    @ wraps(func)
    def wrapper(**kwargs):
        init_time=kwargs.pop('init_time', None)

        if init_time is None:
            pass
        elif isinstance(init_time, str):
            if len(init_time) == 10:
                init_time=datetime.datetime.strptime(init_time, '%Y%m%d%H')
            elif len(init_time) == 8:
                init_time=datetime.datetime.strptime(init_time, '%y%m%d%H')
            else:
                raise Exception('init_time must be datetime or str like 2001010100 or str like 01010100')

        kwargs['init_time']=init_time
        ret=func(**kwargs)
        return ret
    return wrapper

if __name__ == '__main__':
    get_map_area('全国')
