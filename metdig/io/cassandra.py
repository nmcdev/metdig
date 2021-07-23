# -*- coding: utf-8 -*-

import os
import sys

import datetime
import xarray as xr
import numpy as np
import pandas as pd

import nmc_met_io.retrieve_micaps_server as nmc_micaps_io
import metdig.io.nmc_micaps_helper as nmc_micaps_helper

from metdig.io.lib import utl_cassandra
from metdig.io.lib import utility as utl

import metdig.utl as mdgstda

import logging
_log = logging.getLogger(__name__)


def get_model_grid(init_time=None, fhour=None, data_name=None, var_name=None, level=None,
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
    # 从配置中获取相关信息
    try:
        if level:
            level_type = 'high'
            cassandra_dir = utl_cassandra.model_cassandra_dir(level_type=level_type, data_name=data_name,
                                                              var_name=var_name, level=level)  # cassandra数据路径
        else:
            level_type = 'surface'
            cassandra_dir = utl_cassandra.model_cassandra_dir(level_type=level_type, data_name=data_name, var_name=var_name)  # cassandra数据路径
        cassandra_units = utl_cassandra.model_cassandra_units(level_type=level_type, data_name=data_name, var_name=var_name)  # cassandra数据单位
        cassandra_level = utl_cassandra.model_cassandra_level(level_type=level_type, data_name=data_name, var_name=var_name, level=level)
    except Exception as e:
        raise Exception(str(e))
    filename = utl.model_filename(init_time, fhour)
    data = nmc_micaps_io.get_model_grid(cassandra_dir, filename=filename)  # ['number', 'time', 'level', 'lat', 'lon'] 注意（nmc_micaps_io返回的维度不统一）
    # 此处建议修改为warnning
    if data is None:
        raise Exception('Can not get data from cassandra! {}{}'.format(cassandra_dir, filename))

    #读取集合预报
    if('number' in list(data.coords.keys())):
        data_name=data.coords['number'].values
    else:
        data_name=[data_name]

    # 数据裁剪
    data = utl.area_cut(data, extent, x_percent, y_percent)

    # 经纬度从小到大排序好
    data = data.sortby('lat')
    data = data.sortby('lon')

    stda_data = None
    if 'data' in data.keys():
        stda_data = mdgstda.xrda_to_gridstda(data['data'],
                                             member_dim='number', level_dim='level', time_dim='time', lat_dim='lat', lon_dim='lon',
                                             member=[data_name], level=[cassandra_level], time=[init_time], dtime=[fhour],
                                             var_name=var_name, np_input_units=cassandra_units,
                                             data_source='cassandra', level_type=level_type)
    else:
        speed_stda = mdgstda.xrda_to_gridstda(data['speed'],
                                              member_dim='number', level_dim='level', time_dim='time', lat_dim='lat', lon_dim='lon',
                                              member=[data_name], level=[cassandra_level], time=[init_time], dtime=[fhour],
                                              var_name=var_name, np_input_units=cassandra_units,
                                              data_source='cassandra', level_type=level_type)
        angle_stda = mdgstda.xrda_to_gridstda(data['angle'],
                                              member_dim='number', level_dim='level', time_dim='time', lat_dim='lat', lon_dim='lon',
                                              member=[data_name], level=[cassandra_level], time=[init_time], dtime=[fhour],
                                              var_name=var_name, np_input_units=cassandra_units,
                                              data_source='cassandra', level_type=level_type)
        if var_name == 'wsp':
            stda_data = speed_stda
        elif var_name == 'wdir':
            stda_data = angle_stda
        else:
            raise Exception('error nmc_met_io.get_model_grid return value keys is not in [data speed angle]!')

    return stda_data


def get_model_grids(init_time=None, fhours=None, data_name=None, var_name=None, level=None,
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


def get_model_3D_grid(init_time=None, fhour=None, data_name=None, var_name=None, levels=None,
                      extent=None, x_percent=0, y_percent=0):
    '''

    [读取多层单时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhour {[int32]} -- [预报时效]
        data_name {[str]} -- [模式名]
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
            data = get_model_grid(init_time, fhour, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and data.size > 0:
                stda_data.append(data)
        except Exception as e:
            _log.info(str(e))
    if stda_data:
        return xr.concat(stda_data, dim='level')
    return None


def get_model_3D_grids(init_time=None, fhours=None, data_name=None, var_name=None, levels=None,
                       extent=None, x_percent=0, y_percent=0):
    '''

    [读取多层多时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhours {[list]} -- [预报时效]
        data_name {[str]} -- [模式名]
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


def get_model_points(init_time=None, fhours=None, data_name=None, var_name=None, levels=None, points={}):
    '''

    [读取单层/多层，单时效/多时效 模式网格数据，插值到站点上]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhours {[list]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [要素名]
        levels {[list]} -- [层次，不传代表地面层] (default: {None})
        points {[dict]} -- [站点信息，字典中必须包含经纬度{'lon':[], 'lat':[]}]

    Returns:
        [stda] -- [stda格式数据]
    '''
    # get grids data
    stda_data = get_model_3D_grids(init_time, fhours, data_name, var_name, levels)

    if stda_data is not None and stda_data.size > 0:
        return mdgstda.gridstda_to_stastda(stda_data, points)
    return None


def get_obs_stations(obs_time=None, data_name=None, var_name=None, level=None, id_selected=None,
                     extent=None, x_percent=0, y_percent=0, is_save_other_info=False):
    '''

    [获取单层单时次观测站点数据]

    Keyword Arguments:
        obs_time {[datetime]} -- [观测时间]
        data_name {[str]} -- [观测类型]
        var_name {[str]} -- [要素名]
        level {[int]} -- [层次，如果是地面观测站则不传，如果是探空层则传层次]
        id_selected {[list or item]} -- [站号，站号列表或单站] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})
        is_save_other_info {bool} -- [是否保存从nmc_met_io中读取到的其它信息] (default: {False})

    Returns:
        [stda] -- [stda格式数据]
    '''
    # 从配置中获取相关信息
    try:
        cassandra_path = utl_cassandra.obs_cassandra_dir(data_name=data_name, var_name=var_name)  # cassandra数据路径
        cassandra_units = utl_cassandra.obs_cassandra_units(data_name=data_name, var_name=var_name)  # cassandra数据单位
    except Exception as e:
        raise Exception(str(e))

    cassandra_path = utl.cfgpath_format_todatestr(cassandra_path, level=level)  # 带日期格式的路径
    cassandra_dir = os.path.dirname(cassandra_path) + '/'  # 可以直接使用的目录
    filename = os.path.basename(cassandra_path)  # 带日期格式的文件名
    filename = datetime.datetime.strftime(obs_time, filename)

    # ['ID', 'lon', 'lat', 'time', ......] ('ID', 'i4'), ('lon', 'f4'), ('lat', 'f4'), ('numb', 'i2')]
    data = nmc_micaps_io.get_station_data(cassandra_dir, filename=filename)
    if data is None:
        raise Exception('Can not get data from cassandra! {}{}'.format(cassandra_dir, filename))

    # 设置ID列为索引列
    data = data.set_index('ID')
    # print(data.index.dtype)
    # print(data)
    # print(data.columns) # [lon', 'lat', 'Alt', 'Grade', 'Rain_1h', '1004', 'time']'

    # 经纬度范围裁剪
    data = utl.area_cut(data, extent, x_percent, y_percent)

    # 站点选择
    data = utl.sta_select_id(data, id_selected)

    # print(data.index)

    # 数据列转换成stda标准的名称
    data = utl_cassandra.obs_rename_colname(data)

    # 层次初始化，如果为地面层次，初始化为0
    if level:
        levels = np.full((len(data)), level)
    else:
        levels = np.full((len(data)), 0)

    # 其它坐标信息列
    other_input = {}
    if is_save_other_info:
        for other_name in list(set(list(data.columns)).difference(set(['lon', 'lat', 'ID', 'time', var_name]))):  # 保存其它信息列:
            other_input[other_name] = data[other_name].values
    # print(other_input.keys())
    # print(other_input)
    # exit()

    # 转成stda
    return mdgstda.numpy_to_stastda(
        data[var_name].values, [data_name], levels, data['time'].values, 0, data.index, data['lat'].values, data['lon'].values,
        np_input_units=cassandra_units, var_name=var_name, other_input=other_input,
        data_source='cassandra', data_name=data_name
    )


def get_obs_stations_multitime(obs_times=None, data_name=None, var_name=None, id_selected=None,
                               extent=None, x_percent=0, y_percent=0, is_save_other_info=False):
    '''

    [获取单层多时次观测站点数据]

    Keyword Arguments:
        obs_times {[list]} -- [观测时间列表]
        data_name {[str]} -- [观测类型]
        var_name {[str]} -- [要素名]
        id_selected {[list or item]} -- [站号，站号列表或单站] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    datas = []
    attrs = {}
    for obs_time in obs_times:
        try:
            data = get_obs_stations(obs_time, data_name, var_name, id_selected=id_selected, extent=extent,
                                    x_percent=x_percent, y_percent=y_percent, is_save_other_info=is_save_other_info)

            if data is not None and len(data) > 0:
                attrs = data.attrs
                datas.append(data)

        except Exception as e:
            _log.info(str(e))

    if datas:
        df = pd.concat(datas, ignore_index=True)
        df.attrs = attrs
        return df

    return None


def get_fy_awx(obs_time=None, data_name=None, var_name=None, channel=None, extent=None, x_percent=0, y_percent=0, isnearesttime=False):
    """[获取卫星观测数据]

    Args:
        obs_time ([datetime], optional): [观测时间]. Defaults to None.
        data_name ([str], optional): [观测类型]. Defaults to None.
        var_name ([str], optional): [要素名]. Defaults to None.
        channel ([int or str], optional): [卫星通道]. Defaults to None.
        extent ([tuple], optional): [裁剪区域，如(50, 150, 0, 65)]. Defaults to None.
        x_percent (int, optional): [根据裁剪区域经度方向扩充百分比]. Defaults to 0.
        y_percent (int, optional): [根据裁剪区域纬度方向扩充百分比]. Defaults to 0.
        isnearesttime (bool, optional): [如果obs_time非空，是否需要读取离obs_time最近的实况]. Defaults to False.

    Returns:
        [stda] -- [stda格式数据]
    """

    # 从配置中获取相关信息
    try:
        cassandra_path = utl_cassandra.sate_cassandra_dir(data_name=data_name, var_name=var_name, channel=channel)  # cassandra数据路径
        cassandra_units = utl_cassandra.sate_cassandra_units(data_name=data_name, var_name=var_name, channel=channel)  # cassandra数据单位
    except Exception as e:
        raise Exception(str(e))

    cassandra_path = utl.cfgpath_format_todatestr(cassandra_path, channel=channel)  # 带日期格式的路径
    cassandra_dir = os.path.dirname(cassandra_path) + '/'  # 可以直接使用的目录
    cassandra_filename = os.path.basename(cassandra_path)  # 带日期格式的文件名

    filename, obs_time = nmc_micaps_helper.get_obs_filename(cassandra_dir, cassandra_filename, obs_time=obs_time, isnearesttime=isnearesttime)  # 文件名

    data = nmc_micaps_io.get_fy_awx(cassandra_dir, filename=filename)  # nmc_micaps_io返回的维度固定为 ['time', 'channel', 'lat', 'lon']
    if data is None:
        raise Exception('Can not get data from cassandra! {}{}'.format(cassandra_dir, filename))

    # 数据裁剪
    data = utl.area_cut(data, extent, x_percent, y_percent)

    # 经纬度从小到大排序好
    data = data.sortby('lat')
    data = data.sortby('lon')

    # 转成stda
    stda_data = mdgstda.xrda_to_gridstda(data['image'],
                                         level_dim='channel', time_dim='time', lat_dim='lat', lon_dim='lon',
                                         member=[data_name], level=[channel], time=[obs_time],
                                         var_name=var_name, np_input_units=cassandra_units, data_source='cassandra')

    return stda_data


def get_tlogp(obs_time=None, data_name=None, var_name=None, id_selected=None,
              extent=None, x_percent=0, y_percent=0, is_save_other_info=False):
    """[探空tlogp数据]

    Args:
        obs_time ([datetime], optional): [观测时间]. Defaults to None.
        data_name ([str], optional): [观测类型]. Defaults to None.
        var_name ([str], optional): [要素名]. Defaults to None.
        id_selected {[list or item]} -- [站号，站号列表或单站] default: None.
        extent ([tuple], optional): [裁剪区域，如(50, 150, 0, 65)]. Defaults to None.
        x_percent (int, optional): [根据裁剪区域经度方向扩充百分比]. Defaults to 0.
        y_percent (int, optional): [根据裁剪区域纬度方向扩充百分比]. Defaults to 0.
        is_save_other_info {bool} -- [是否保存从nmc_met_io中读取到的其它信息] (default: {False})

    Returns:
        [stda] -- [stda格式数据]
    """
    # 从配置中获取相关信息
    try:
        cassandra_path = utl_cassandra.obs_cassandra_dir(data_name=data_name, var_name=var_name)  # cassandra数据路径
        cassandra_units = utl_cassandra.obs_cassandra_units(data_name=data_name, var_name=var_name)  # cassandra数据单位
    except Exception as e:
        raise Exception(str(e))

    cassandra_path = utl.cfgpath_format_todatestr(cassandra_path)  # 带日期格式的路径
    cassandra_dir = os.path.dirname(cassandra_path) + '/'  # 可以直接使用的目录
    filename = os.path.basename(cassandra_path)  # 带日期格式的文件名
    filename = datetime.datetime.strftime(obs_time, filename)

    # ['ID', 'lon', 'lat', 'alt', 'time', 'p', 'h', 't', 'td', 'wd', 'ws]
    data = nmc_micaps_io.get_tlogp(cassandra_dir, filename=filename)
    if data is None:
        raise Exception('Can not get data from cassandra! {}{}'.format(cassandra_dir, filename))

    # 设置ID列为索引列# print(data)
    data = data.set_index('ID')

    # 经纬度范围裁剪
    data = utl.area_cut(data, extent, x_percent, y_percent)

    # 站点选择
    data = utl.sta_select_id(data, id_selected)

    # 数据列转换成stda标准的名称
    data = data.rename(columns={'h': 'hgt', 't': 'tmp', 'td': 'td', 'wd': 'wdir', 'ws': 'wsp'})

    # 层次初始化
    levels = data['p'].values

    # 其它坐标信息列
    other_input = {}
    if is_save_other_info:
        for other_name in ['alt']:  # 保存其它信息列:
            other_input[other_name] = data[other_name].values

    # 转成stda
    return mdgstda.numpy_to_stastda(
        data[var_name].values, [data_name], levels, data['time'].values, 0, data.index, data['lat'].values, data['lon'].values,
        np_input_units=cassandra_units, var_name=var_name, other_input=other_input,
        data_source='cassandra', data_name=data_name
    )


def get_radar_mosaic(obs_time=None, data_name=None, var_name=None, extent=None, x_percent=0, y_percent=0, isnearesttime=False):
    """[雷达回波全国拼图数据]

    Args:
        obs_time ([datetime], optional): [观测时间]. Defaults to None.
        data_name ([str], optional): [观测类型]. Defaults to None.
        var_name ([str], optional): [要素名]. Defaults to None.
        extent ([tuple], optional): [裁剪区域，如(50, 150, 0, 65)]. Defaults to None.
        x_percent (int, optional): [根据裁剪区域经度方向扩充百分比]. Defaults to 0.
        y_percent (int, optional): [根据裁剪区域纬度方向扩充百分比]. Defaults to 0.
        isnearesttime (bool, optional): [如果obs_time非空，是否需要读取离obs_time最近的实况]. Defaults to False.

    Returns:
        [stda] -- [stda格式数据]
    """
    # 从配置中获取相关信息
    try:
        cassandra_path = utl_cassandra.radar_cassandra_dir(data_name=data_name, var_name=var_name)  # cassandra数据路径
        cassandra_units = utl_cassandra.radar_cassandra_units(data_name=data_name, var_name=var_name)  # cassandra数据单位
    except Exception as e:
        raise Exception(str(e))

    cassandra_path = utl.cfgpath_format_todatestr(cassandra_path)  # 带日期格式的路径
    cassandra_dir = os.path.dirname(cassandra_path) + '/'  # 可以直接使用的目录
    cassandra_filename = os.path.basename(cassandra_path)  # 带日期格式的文件名

    filename, obs_time = nmc_micaps_helper.get_obs_filename(cassandra_dir, cassandra_filename, obs_time=obs_time, isnearesttime=isnearesttime)  # 文件名

    data = nmc_micaps_io.get_radar_mosaic(cassandra_dir, filename=filename)  # nmc_micaps_io返回的维度固定为，['time', 'lat', 'lon']
    if data is None:
        raise Exception('Can not get data from cassandra! {}{}'.format(cassandra_dir, filename))

    # 数据裁剪
    data = utl.area_cut(data, extent, x_percent, y_percent)

    # 经纬度从小到大排序好
    data = data.sortby('lat')
    data = data.sortby('lon')
    # print(data)

    # 转成stda
    stda_data = mdgstda.xrda_to_gridstda(data['data'],
                                         time_dim='time', lat_dim='lat', lon_dim='lon',
                                         member=[data_name],  time=[obs_time],
                                         var_name=var_name, np_input_units=cassandra_units, data_source='cassandra')

    return stda_data


def get_wind_profiler_bytimerange(obs_st_time=None, obs_ed_time=None, data_name=None, var_name=None, id_selected=None):
    """[获取时间范围内的风廓线数据]

    Args:
        obs_st_time ([datetime], optional): [观测开始时间]. Defaults to None.
        obs_ed_time ([datetime], optional): [观测结束时间]. Defaults to None.
        id_selected ([int or str], optional): [站号]. Defaults to None.
        data_name ([str], optional): [观测类型]. Defaults to None.
        var_name ([str], optional): [要素名]. Defaults to None.

    Returns:
        [stda] -- [stda格式数据]
    """
    # 从配置中获取相关信息
    try:
        cassandra_path = utl_cassandra.obs_cassandra_dir(data_name=data_name, var_name=var_name)  # cassandra数据路径
        cassandra_units = utl_cassandra.obs_cassandra_units(data_name=data_name, var_name=var_name)  # cassandra数据单位
    except Exception as e:
        raise Exception(str(e))

    cassandra_path = utl.cfgpath_format_todatestr(cassandra_path, ID=id_selected)  # 带日期格式的路径
    cassandra_dir = os.path.dirname(cassandra_path) + '/'  # 可以直接使用的目录
    cassandra_filename = os.path.basename(cassandra_path)  # 带日期格式的文件名

    filenames, obs_times = nmc_micaps_helper.get_obs_filenames(cassandra_dir, cassandra_filename, obs_st_time=obs_st_time, obs_ed_time=obs_ed_time)

    datas = []
    attrs = {}
    obs_times.sort(reverse=False)  # 按照日期从小到大排序
    for obs_time in obs_times:
        try:
            data = get_wind_profiler_bytime(obs_time=obs_time, data_name=data_name, var_name=var_name, id_selected=id_selected, isnearesttime=False)
            if data is not None and len(data) > 0:
                attrs = data.attrs
                datas.append(data)

        except Exception as e:
            _log.info(str(e))

    if datas:
        df = pd.concat(datas, ignore_index=True)
        df.attrs = attrs
        return df

    return None


def get_wind_profiler_bytime(obs_time=None, data_name=None, var_name=None, id_selected=None, isnearesttime=False):
    """[获取风廓线数据]

    Args:
        obs_time ([datetime], optional): [观测时间]. Defaults to None.
        id_selected ([int or str], optional): [站号]. Defaults to None.
        data_name ([str], optional): [观测类型]. Defaults to None.
        var_name ([str], optional): [要素名]. Defaults to None.
        isnearesttime (bool, optional): [如果obs_time非空，是否需要读取离obs_time最近的实况]. Defaults to False.

    Returns:
        [stda] -- [stda格式数据]
    """
    # 从配置中获取相关信息
    try:
        cassandra_path = utl_cassandra.obs_cassandra_dir(data_name=data_name, var_name=var_name)  # cassandra数据路径
        cassandra_units = utl_cassandra.obs_cassandra_units(data_name=data_name, var_name=var_name)  # cassandra数据单位
    except Exception as e:
        raise Exception(str(e))

    cassandra_path = utl.cfgpath_format_todatestr(cassandra_path, ID=id_selected)  # 带日期格式的路径
    cassandra_dir = os.path.dirname(cassandra_path) + '/'  # 可以直接使用的目录
    cassandra_filename = os.path.basename(cassandra_path)  # 带日期格式的文件名

    filename, obs_time = nmc_micaps_helper.get_obs_filename(cassandra_dir, cassandra_filename, obs_time=obs_time, isnearesttime=isnearesttime)  # 文件名

    data = nmc_micaps_helper.get_wind_profiler(cassandra_dir, filename=filename)
    if data is None:
        raise Exception('Can not get data from cassandra! {}{}'.format(cassandra_dir, filename))

    data = data.rename(columns={
        'stationId': 'id',
        'observationTime': 'time',
        'longitude': 'lon',
        'latitude': 'lat',
        'samplingHeight': 'level',
        'horizontalWindDirection': 'wdir',
        'horizontalWindSpeed': 'wsp',
        'verticalWindSpeed': 'w',
    })

    # 转成stda
    return mdgstda.numpy_to_stastda(
        data[var_name].values, [data_name], data['level'].values, data['time'].values, 0, data['id'].values, data['lat'].values, data['lon'].values,
        np_input_units=cassandra_units, var_name=var_name, other_input={},
        data_source='cassandra', data_name=data_name
    )


'''
def get_station_dataset(init_time, fhours, data_name, var_name):
    stda_data = []
    for fhour in fhours:
        data = get_station_data(init_time, fhour, data_name, var_name)
        stda_data.append(data)
    stda_data = pd.concat(stda_data)
    return stda_data
'''


if __name__ == '__main__':
    # init_time = datetime.datetime(2020, 7, 25, 8)
    # x = get_model_grid(init_time=init_time, fhour=0, data_name='ecmwf', var_name='tmp', level=850)
    # init_time = datetime.datetime(2020, 8 , 3, 8)
    # x = get_model_grid(init_time=init_time, fhour=6, data_name='grapes_gfs', var_name='theta', level=850)
    # init_time = datetime.datetime(2020, 8, 8, 8)
    # x = get_model_grid(init_time=init_time, fhour=0, data_name='ecmwf', var_name='td2m')
    # print(np.min(x.values), np.max(x.values), np.mean(x.values))
    # print(x)

    obs_time = datetime.datetime(2021, 6, 6, 5, 6, 0)
    df = get_wind_profiler_bytime(obs_time=obs_time, id_selected=51463, data_name='wind_profiler', var_name='wdir')
    print(df)

    # obs_time = datetime.datetime(2021, 6, 8, 8, 10, 1)
    # df = get_radar_mosaic(obs_time=obs_time, data_name='achn', var_name='cref', isnearesttime=True)
    # print(df)

    # obs_st_time = datetime.datetime(2021, 6, 6, 5)
    # obs_ed_time = datetime.datetime(2021, 6, 8, 8)
    # df = get_wind_profiler_bytimerange(obs_st_time, obs_ed_time, id_selected='51463', data_name='wind_profiler', var_name='wdir')
    # print(df)
