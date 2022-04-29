# -*- coding: utf-8 -*-

import os
import sys

import datetime
import xarray as xr
import numpy as np
import pandas as pd

from metdig.io.lib import config as CONFIG
from metdig.io.lib import utility as utl

import metdig.utl as mdgstda

import logging
# logging.basicConfig(format='', level=logging.INFO)  # 此处加这一句代表忽略下属_log作用，直接将_log输出到命令行，测试用
_log = logging.getLogger(__name__)


def split_stda_to_cache_sfc(stda, var_name, data_name='custom', var_units='', is_overwrite=True, **attrs_kwargs):
    '''

    [拆分自定义地面stda至metdig缓存目录]

    Keyword Arguments:
        stda {[xarray]} -- [stda格式数据]
        var_name {[str]} -- [数据要素名]
        data_name {[str]} -- [模式名]
        var_units {[str]} -- [数据对应的单位。默认不给定单位即传进来的stda数据为标准格式，自动赋予stda标准单位属性。如给定单位则进行单位转换]
        is_overwrite {[bool]} -- [是否重写，默认重写覆盖]
    '''
    if stda.level.size > 1:
        raise Exception('stda error: the length of the level dimension must be 1!')

    stda.name = var_name
    for time in stda.time.values:
        for dtime in stda.dtime.values:
            cachefile = os.path.join(CONFIG.get_cache_dir(),
                                     f'CUSTOM_DATA/{data_name}/{var_name}/{pd.to_datetime(time):%Y%m%d%H%M%S}.{dtime:03d}.nc')

            if os.path.exists(cachefile) and is_overwrite == False:
                _log.info(f'{cachefile} 存在，不覆盖！')
                continue

            # 转换为stda标准格式存放
            data = stda.sel(time=time, dtime=dtime)
            data = data.expand_dims(time=[time], dtime=[dtime])
            data = data.transpose('member', 'level', 'time', 'dtime', 'lat', 'lon')

            # 单位及属性
            stda_attrs = mdgstda.get_stda_attrs(var_name=var_name, **attrs_kwargs)
            if var_units:
                data.values, data_units = mdgstda.numpy_units_to_stda(data.values, var_units, stda_attrs['var_units']) # 单位转换
                stda_attrs['var_units'] = data_units
            data.attrs = stda_attrs

            if not os.path.exists(os.path.dirname(cachefile)):
                os.makedirs(os.path.dirname(cachefile))

            _log.info(f'save to {cachefile}')
            data.to_netcdf(cachefile)


def split_stda_to_cache_psl(stda, var_name, data_name='custom', var_units='', is_overwrite=True, **attrs_kwargs):
    '''

    [拆分自定义高空stda至metdig缓存目录]

    Keyword Arguments:
        stda {[xarray]} -- [stda格式数据]
        var_name {[str]} -- [数据要素名]
        data_name {[str]} -- [模式名]
        var_units {[str]} -- [数据对应的单位。默认不给定单位即传进来的stda数据为标准格式，自动赋予stda标准单位属性。如给定单位则进行单位转换]
        is_overwrite {[bool]} -- [是否重写，默认重写覆盖]
    '''
    stda.name = var_name
    for level in stda.level.values:

        for time in stda.time.values:
            for dtime in stda.dtime.values:
                cachefile = os.path.join(CONFIG.get_cache_dir(),
                                         f'CUSTOM_DATA/{data_name}/{var_name}/{level}/{pd.to_datetime(time):%Y%m%d%H%M%S}.{dtime:03d}.nc')

                if os.path.exists(cachefile) and is_overwrite == False:
                    _log.info(f'{cachefile} 存在，不覆盖！')
                    continue

                # 转换为stda标准格式存放
                data = stda.sel(level=level, time=time, dtime=dtime)
                data = data.expand_dims(level=[level], time=[time], dtime=[dtime])
                data = data.transpose('member', 'level', 'time', 'dtime', 'lat', 'lon')
                
                # 单位及属性
                stda_attrs = mdgstda.get_stda_attrs(var_name=var_name, **attrs_kwargs)
                if var_units:
                    data.values, data_units = mdgstda.numpy_units_to_stda(data.values, var_units, stda_attrs['var_units']) # 单位转换
                    stda_attrs['var_units'] = data_units
                data.attrs = stda_attrs

                if not os.path.exists(os.path.dirname(cachefile)):
                    os.makedirs(os.path.dirname(cachefile))

                _log.info(f'save to {cachefile}')
                data.to_netcdf(cachefile)


def get_model_grid(init_time=None, fhour=None, data_name='custom', var_name=None, level=None,
                   extent=None, x_percent=0, y_percent=0):
    '''

    [读取单层单时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhour {[int32]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [数据要素名]
        level {[int32]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    if level:
        cachefile = os.path.join(CONFIG.get_cache_dir(),
                                 f'CUSTOM_DATA/{data_name}/{var_name}/{level}/{init_time:%Y%m%d%H%M%S}.{fhour:03d}.nc')
    else:
        cachefile = os.path.join(CONFIG.get_cache_dir(),
                                 f'CUSTOM_DATA/{data_name}/{var_name}/{init_time:%Y%m%d%H%M%S}.{fhour:03d}.nc')

    if not os.path.exists(cachefile):
        raise Exception(f'Can not get data from {cachefile}')

    data = xr.load_dataarray(cachefile)

    # 数据裁剪
    data = utl.area_cut(data, extent, x_percent, y_percent)

    return data


def get_model_grids(init_time=None, fhours=None, data_name='custom', var_name=None, level=None,
                    extent=None, x_percent=0, y_percent=0):
    '''

    [读取单层多时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhours {[list]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [要素名]
        level {[int32]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    fhours = utl.parm_tolist(fhours)

    stda_data = []
    for fhour in fhours:
        try:  # 待斟酌
            data = get_model_grid(init_time, fhour, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
        except:  # 待斟酌
            continue
        if data is not None and data.size > 0:
            stda_data.append(data)
    if stda_data:
        return xr.concat(stda_data, dim='dtime')
    else:
        raise Exception('Can not get data from cassandra! {}{}'.format(data_name, var_name))


def get_model_3D_grid(init_time=None, fhour=None, data_name='custom', var_name=None, levels=None,
                      extent=None, x_percent=0, y_percent=0):
    '''

    [读取多层单时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhour {[int32]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [要素名]
        levels {[list or number]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    levels = utl.parm_tolist(levels)

    stda_data = []
    for level in levels:
        try:
            data = get_model_grid(init_time, fhour, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and data.size > 0:
                stda_data.append(data)
        except Exception as e:
            _log.info(str(e))
    if stda_data:
        return xr.concat(stda_data, dim='level')
    return None


def get_model_3D_grids(init_time=None, fhours=None, data_name='custom', var_name=None, levels=None,
                       extent=None, x_percent=0, y_percent=0):
    '''

    [读取多层多时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhours {[list]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [要素名]
        levels {[list or number]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    fhours = utl.parm_tolist(fhours)
    levels = utl.parm_tolist(levels)

    stda_data = []
    for fhour in fhours:
        temp_data = []
        for level in levels:
            try:
                data = get_model_grid(init_time, fhour, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
                if data is not None and data.size > 0:
                    temp_data.append(data)
            except Exception as e:
                # 若需要,请修改为warning
                _log.info(str(e))
                continue
        if temp_data:
            temp_data = xr.concat(temp_data, dim='level')
            stda_data.append(temp_data)
    if stda_data:
        return xr.concat(stda_data, dim='dtime')
    return None


def get_model_points(init_time=None, fhours=None, data_name='custom', var_name=None, levels=None, points={}):
    '''

    [读取单层/多层，单时效/多时效 模式网格数据，插值到站点上]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhours {[list or number]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [要素名]
        levels {[list or number]} -- [层次，不传代表地面层] (default: {None})
        points {[dict]} -- [站点信息，字典中必须包含经纬度{'lon':[], 'lat':[]}]

    Returns:
        [stda] -- [stda格式数据]
    '''
    fhours = utl.parm_tolist(fhours)
    levels = utl.parm_tolist(levels)

    # get grids data
    stda_data = get_model_3D_grids(init_time, fhours, data_name, var_name, levels)

    if stda_data is not None and stda_data.size > 0:
        return mdgstda.gridstda_to_stastda(stda_data, points)
    return None


def test():
    '''
    import metdig
    # 测试拆分高空
    data = metdig.io.cassandra.get_model_3D_grids(
        init_time=datetime.datetime(2020, 7, 20, 8), fhours=[0, 24], levels=[500, 850],
        data_name='ecmwf', var_name='hgt')
    # print(data)
    split_stda_to_cache_psl(data, 'hgt')

    # 测试拆分地面stda至cache目录
    data = metdig.io.cassandra.get_model_3D_grids(
        init_time=datetime.datetime(2020, 8, 8, 8), fhours=[3, 6, 9, 12],
        data_name='ecmwf', var_name='rain03')
    # print(data)
    split_stda_to_cache_sfc(data, 'rain03')
    '''

    '''
    # 测试读取自定义高空数据
    data = get_model_3D_grids(
        init_time=datetime.datetime(2020, 7, 20, 8), fhours=[0, 24], levels=[500, 850],
        data_name='custom', var_name='hgt')
    print(data)

    # 测试读取自定义地面数据
    data = get_model_3D_grids(
        init_time=datetime.datetime(2020, 8, 8, 8), fhours=[3, 6, 9, 12],
        data_name='custom', var_name='rain03')
    print(data)
    '''
    pass


if __name__ == '__main__':
    test()
