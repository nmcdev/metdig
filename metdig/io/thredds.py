import requests

import os
import sys

import datetime
import xarray as xr
import numpy as np
import pandas as pd

import metdig.utl as mdgstda

from .lib import utl_thredds
from .lib import utility as utl

from .lib import config as CONFIG

from metdig.io.MDIException import CFGError


def get_model_grid(init_time=None, data_name=None,  var_name=None, level=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [获取thredds单层单时次数据]

    Keyword Arguments:
        init_time {[datetime]} -- [时间（北京时）] (default: {None})
        data_name {[str]} -- [模式名] (default: {None})
        var_name {[str]} -- [数据要素名] (default: {None})
        level {[int32]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    init_time_utc = init_time - datetime.timedelta(hours=8)  # 世界时

    # 从配置中获取相关信息
    try:
        if level:
            level_type = 'high'
        else:
            level_type = 'surface'

        ip = CONFIG.CONFIG['THREDDS']['IP']
        port = CONFIG.CONFIG['THREDDS']['port']
        thredds_path = utl_thredds.model_thredds_path(data_name=data_name, var_name=var_name, level_type=level_type)
        thredds_var_name = utl_thredds.model_thredds_variable(data_name=data_name, var_name=var_name, level_type=level_type)
        thredds_level = utl_thredds.model_thredds_level(data_name=data_name, var_name=var_name, level_type=level_type, level=level)
        thredds_units = utl_thredds.model_thredds_units(data_name=data_name, level_type=level_type, var_name=var_name)
    except Exception as e:
        raise CFGError(str(e))

    thredds_path = utl.cfgpath_format(thredds_path, init_time_utc, thredds_var_name=thredds_var_name, ip=ip, port=port)

    result = requests.get(thredds_path + '.html')
    if result.status_code == 200:
        data = xr.open_dataset(thredds_path)
    else:
        raise Exception('Can not get data from thredds! {}'.format(thredds_path))

    data = data[thredds_var_name]
    data = data.sel(time=init_time_utc)

    if level:
        data = data.sel(lev=level)

    data = data.load()

    data = data.squeeze().transpose('lat', 'lon')

    # 数据裁剪
    if extent:
        data = data.where((data['lon'] >= extent[0]) & (data['lon'] <= extent[1]) & (
            data['lat'] >= extent[2]) & (data['lat'] <= extent[3]), drop=True)

    # 经纬度从小到大排序好
    data = data.sortby('lat')
    data = data.sortby('lon')

    if level:
        levels = [level]
    else:
        levels = [thredds_level]

    np_data = data.values[np.newaxis, np.newaxis, np.newaxis, np.newaxis, ...]
    stda_data = mdgstda.numpy_to_gridstda(
        np_data, [data_name], levels, [init_time], [0], data.coords['lat'].values, data.coords['lon'].values,
        var_name=var_name, np_input_units=thredds_units,
        data_source='thredds', level_type=level_type)

    return stda_data


def get_model_grids(init_times=None, data_name=None, var_name=None, level=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [读取单层多时次模式网格数据]

    Keyword Arguments:
        init_times {[list]} -- [时间列表] (default: {None})
        data_name {[str]} -- [模式名] (default: {None})
        var_name {[str]} -- [要素名]
        level {[int32]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    if not isinstance(init_times, list):
        init_times = [init_times]

    stda_data = []
    for init_time in init_times:
        try:
            data = get_model_grid(init_time, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and data.size > 0:
                stda_data.append(data)
        except Exception as e:
            print(str(e))
    if stda_data:
        return xr.concat(stda_data, dim='time')
    return None


def get_model_3D_grid(init_time=None, data_name=None, var_name=None, levels=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [读取多层单时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [时间]
        data_name {[str]} -- [模式名] (default: {None})
        var_name {[str]} -- [要素名]
        levels {[list]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    if levels is None:
        levels = [None]
    stda_data = []
    for level in levels:
        try:
            data = get_model_grid(init_time, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and data.size > 0:
                stda_data.append(data)
        except Exception as e:
            print(str(e))

    if stda_data:
        return xr.concat(stda_data, dim='level')
    return None


def get_model_3D_grids(init_times=None, data_name=None, var_name=None, levels=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [读取多层多时次模式网格数据]

    Keyword Arguments:
        init_times {[list]} -- [时间列表] (default: {None})
        data_name {[str]} -- [模式名] (default: {None})
        var_name {[str]} -- [要素名]
        levels {[list]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    if levels is None:
        levels = [None]
    if not isinstance(init_times, list):
        init_times = [init_times]
    # print(init_times, levels, kwargs)

    stda_data = []
    for init_time in init_times:
        temp_data = []
        for level in levels:
            try:
                data = get_model_grid(init_time, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
                if data is not None and data.size > 0:
                    temp_data.append(data)
            except Exception as e:
                # print(str(e))
                continue
        if temp_data:
            temp_data = xr.concat(temp_data, dim='level')
            stda_data.append(temp_data)
    if stda_data:
        return xr.concat(stda_data, dim='time')
    return None


def get_model_points(init_time=None, data_name=None, var_name=None, levels=None, points={}, **kwargs):
    '''

    [读取单层/多层，单时效/多时效 模式网格数据，插值到站点上]

    Keyword Arguments:
        init_times {[list]} -- [时间] (default: {None})
        data_name {[str]} -- [模式名] (default: {None})
        var_name {[str]} -- [要素名]
        levels {[list]} -- [层次，不传代表地面层] (default: {None})
        points {[dict]} -- [站点信息，字典中必须包含经纬度{'lon':[], 'lat':[]}]

    Returns:
        [stda] -- [stda格式数据]
    '''
    # get grids data
    stda_data = get_model_3D_grids(init_time, data_name, var_name, levels)

    if stda_data is not None and stda_data.size > 0:
        return mdgstda.gridstda_to_stastda(stda_data, points)
    return None