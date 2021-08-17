import requests

import os
import sys

import datetime
import xarray as xr
import numpy as np
import pandas as pd

import metdig.utl as mdgstda

from metdig.io.lib import thredds_model_cfg
from metdig.io.lib import utility as utl

from metdig.io.lib import config as CONFIG

import logging
_log = logging.getLogger(__name__)


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
        thredds_path = thredds_model_cfg().model_thredds_path(data_name=data_name, var_name=var_name, level_type=level_type)
        thredds_var_name = thredds_model_cfg().model_thredds_variable(data_name=data_name, var_name=var_name, level_type=level_type)
        thredds_level = thredds_model_cfg().model_thredds_level(data_name=data_name, var_name=var_name, level_type=level_type, level=level)
        thredds_units = thredds_model_cfg().model_thredds_units(data_name=data_name, level_type=level_type, var_name=var_name)
    except Exception as e:
        raise Exception(str(e))

    thredds_path = utl.cfgpath_format_todatestr(thredds_path, thredds_var_name=thredds_var_name, ip=ip, port=port)
    thredds_path = datetime.datetime.strftime(init_time_utc, thredds_path)

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
    data = utl.area_cut(data, extent, x_percent, y_percent)

    # 经纬度从小到大排序好
    data = data.sortby('lat')
    data = data.sortby('lon')

    stda_data = mdgstda.xrda_to_gridstda(data,
                                         lat_dim='lat', lon_dim='lon',
                                         member=[data_name], level=[thredds_level], time=[init_time],
                                         var_name=var_name, np_input_units=thredds_units,
                                         data_source='thredds', level_type=level_type)
    return stda_data


def get_model_grids(init_times=None, data_name=None, var_name=None, level=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [读取单层多时次模式网格数据]

    Keyword Arguments:
        init_times {[list or time]} -- [时间列表] (default: {None})
        data_name {[str]} -- [模式名] (default: {None})
        var_name {[str]} -- [要素名]
        level {[int32]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    init_times = utl.parm_tolist(init_times)

    stda_data = []
    for init_time in init_times:
        try:
            data = get_model_grid(init_time, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and data.size > 0:
                stda_data.append(data)
        except Exception as e:
            _log.info(str(e))
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
        levels {[list or time]} -- [层次，不传代表地面层] (default: {None})
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
            data = get_model_grid(init_time, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and data.size > 0:
                stda_data.append(data)
        except Exception as e:
            _log.info(str(e))

    if stda_data:
        return xr.concat(stda_data, dim='level')
    return None


def get_model_3D_grids(init_times=None, data_name=None, var_name=None, levels=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [读取多层多时次模式网格数据]

    Keyword Arguments:
        init_times {[list or time]} -- [时间列表] (default: {None})
        data_name {[str]} -- [模式名] (default: {None})
        var_name {[str]} -- [要素名]
        levels {[list or number]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    init_times = utl.parm_tolist(init_times)
    levels = utl.parm_tolist(levels)

    stda_data = []
    for init_time in init_times:
        temp_data = []
        for level in levels:
            try:
                data = get_model_grid(init_time, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
                if data is not None and data.size > 0:
                    temp_data.append(data)
            except Exception as e:
                _log.info(str(e))
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
        levels {[list or number]} -- [层次，不传代表地面层] (default: {None})
        points {[dict]} -- [站点信息，字典中必须包含经纬度{'lon':[], 'lat':[]}]

    Returns:
        [stda] -- [stda格式数据]
    '''
    levels = utl.parm_tolist(levels)

    # get grids data
    stda_data = get_model_3D_grids(init_time, data_name, var_name, levels)

    if stda_data is not None and stda_data.size > 0:
        return mdgstda.gridstda_to_stastda(stda_data, points)
    return None
