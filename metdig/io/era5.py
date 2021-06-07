# -*- coding: utf-8 -*-

import datetime
import os
import sys
import math

import cdsapi
import numpy as np
import xarray as xr

import sys

import metdig.utl as mdgstda

from .lib import utl_era5
from .lib import config as CONFIG

import logging
_log = logging.getLogger(__name__)

class ERA5DataService(object):
    """

    [era5 数据下载工具类。 一次只下载单时次单层次数据, init_time为世界时
    备注：
    1.参数variable均为era5网站下的要素名，详细可以看各个函数下网址链接
    2.参数savefile为保存在本地的全路径
         ]
    """

    def __init__(self):
        pass

    def download_hourly_pressure_levels(self, init_time, variable, pressure_level, savefile, extent=[50, 160, 0, 70]):
        # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=form
        if os.path.exists(savefile):
            _log.info('{} exists 不重复下载'.format(savefile))
            return
        # 只能下载如下层次数据
        access_lvls = ['1', '2', '3', '5', '7', '10', '20', '30', '50', '70', '100', '125',
                       '150', '175', '200', '225', '250', '300', '350', '400', '450', '500', '550', '600',
                       '650', '700', '750', '775', '800', '825', '850', '875', '900', '925', '950', '975', '1000'
                       ]
        pressure_level = str(pressure_level)
        if pressure_level not in access_lvls:
            raise Exception('download_hourly_pressure_levels pressure_level 参数错误，仅能下载以下层次:' + ','.join(access_lvls))

        if not os.path.exists(os.path.dirname(savefile)):
            os.makedirs(os.path.dirname(savefile))

        c = cdsapi.Client()

        c.retrieve(
            'reanalysis-era5-pressure-levels',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'variable': variable,
                'pressure_level': pressure_level,
                'year': '{}'.format(init_time.year),
                'month': '{:02d}'.format(init_time.month),
                'day': '{:02d}'.format(init_time.day),
                'time': '{:02d}:00'.format(init_time.hour),
                'area': [extent[3], extent[0], extent[2], extent[1]],
            },
            savefile)

    def download_hourly_single_levels(self, init_time, variable, savefile, extent=[50, 160, 0, 70]):
        # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview
        if os.path.exists(savefile):
            _log.info('{} exists 不重复下载'.format(savefile))
            return

        if not os.path.exists(os.path.dirname(savefile)):
            os.makedirs(os.path.dirname(savefile))

        c = cdsapi.Client()

        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'variable': variable,
                'year': '{}'.format(init_time.year),
                'month': '{:02d}'.format(init_time.month),
                'day': '{:02d}'.format(init_time.day),
                'time': '{:02d}:00'.format(init_time.hour),
                'area': [extent[3], extent[0], extent[2], extent[1]],
            },
            savefile)


def get_model_grid(init_time=None, var_name=None, level=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [获取era5再分析单层单时次数据，注意：缓存的目录为世界时]

    Keyword Arguments:
        init_time {[datetime]} -- [再分析时间（北京时）] (default: {None})
        var_name {[str]} -- [数据要素名] (default: {None})
        level {[int32]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [type] -- [description]
    '''
    
    init_time_utc = init_time- datetime.timedelta(hours=8) # 世界时
    if extent:
        # 数据预先扩大xy percent
        delt_x = (extent[1] - extent[0]) * x_percent
        delt_y = (extent[3] - extent[2]) * y_percent
        extent = (extent[0] - delt_x, extent[1] + delt_x, extent[2] - delt_y, extent[3] + delt_y)
        extent = (math.floor(extent[0]), math.ceil(extent[1]), math.floor(extent[2]), math.ceil(extent[3]))
        extent = (
            extent[0] if extent[0] >= -180 else -180,
            extent[1] if extent[1] <= 180 else 180,
            extent[2] if extent[2] >= -90 else -90,
            extent[3] if extent[3] <= 90 else 90,
        )
    else:
        extent = [50, 160, 0, 70]  # 数据下载默认范围

    # 从配置中获取相关信息
    try:
        if level:
            level_type = 'high'
            cache_file = CONFIG.get_era5cache_file(init_time_utc, var_name, extent, level=level, find_area=True)
        else:
            level_type = 'surface'
            cache_file = CONFIG.get_era5cache_file(init_time_utc, var_name, extent, level=None, find_area=True)

        era5_var = utl_era5.era5_variable(var_name=var_name, level_type=level_type)
        era5_level = utl_era5.era5_level(var_name=var_name, level_type=level_type, level=level)
        era5_units = utl_era5.era5_units(level_type=level_type, var_name=var_name)
    except Exception as e:
        raise Exception(str(e))
    
    if not os.path.exists(cache_file):
        if level:
            ERA5DataService().download_hourly_pressure_levels(init_time_utc, era5_var, level, cache_file, extent=extent)
        else:
            ERA5DataService().download_hourly_single_levels(init_time_utc, era5_var, cache_file, extent=extent)

    # 此处读到的dataset应该只有一个数据集，维度=[time=1,latitude,longitude]，因为下载的时候均是单层次下载
    data = xr.open_dataset(cache_file)
    data = data.to_array()
    data = data.squeeze().transpose('latitude', 'longitude')
    data = data.rename({'latitude': 'lat', 'longitude': 'lon'})

    # 数据裁剪
    if extent:
        data = data.where((data['lon'] >= extent[0]) & (data['lon'] <= extent[1]) & (data['lat'] >= extent[2]) & (data['lat'] <= extent[3]), drop=True)

    # 经纬度从小到大排序好
    data = data.sortby('lat')
    data = data.sortby('lon')

    if level:
        levels = [level]
    else:
        levels = [era5_level]

    np_data = data.values[np.newaxis, np.newaxis, np.newaxis, np.newaxis, ...]
    stda_data = mdgstda.numpy_to_gridstda(
        np_data, ['era5'], levels, [init_time], [0], data.coords['lat'].values, data.coords['lon'].values,
        var_name=var_name, np_input_units=era5_units,
        data_source='cds', level_type=level_type)

    return stda_data


def get_model_grids(init_times=None, var_name=None, level=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [读取单层多时次模式网格数据]

    Keyword Arguments:
        init_times {[list]} -- [再分析时间列表] (default: {None})
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
            data = get_model_grid(init_time, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and data.size > 0:
                stda_data.append(data)
        except Exception as e:
            _log.info(str(e))
    if stda_data:
        return xr.concat(stda_data, dim='time')
    return None


def get_model_3D_grid(init_time=None, var_name=None, levels=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [读取多层单时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [再分析时间]
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
            data = get_model_grid(init_time, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and data.size > 0:
                stda_data.append(data)
        except Exception as e:
            _log.info(str(e))

    if stda_data:
        return xr.concat(stda_data, dim='level')
    return None


def get_model_3D_grids(init_times=None, var_name=None, levels=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [读取多层多时次模式网格数据]

    Keyword Arguments:
        init_times {[list]} -- [再分析时间列表] (default: {None})
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
                data = get_model_grid(init_time, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
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


def get_model_points(init_time=None, var_name=None, levels=None, points={}, **kwargs):
    '''

    [读取单层/多层，单时效/多时效 模式网格数据，插值到站点上]

    Keyword Arguments:
        init_times {[list]} -- [再分析时间] (default: {None})
        var_name {[str]} -- [要素名]
        levels {[list]} -- [层次，不传代表地面层] (default: {None})
        points {[dict]} -- [站点信息，字典中必须包含经纬度{'lon':[], 'lat':[]}]

    Returns:
        [stda] -- [stda格式数据]
    '''
    # get grids data
    stda_data = get_model_3D_grids(init_time, var_name, levels)

    if stda_data is not None and stda_data.size > 0:
        return mdgstda.gridstda_to_stastda(stda_data, points)
    return None


if __name__ == '__main__':
    obj = ERA5DataService()
    init_time = datetime.datetime(2020, 8, 2, 8)
    # data = get_model_grid(init_time, 'hgt', level=500, extent=[70, 140, 10, 60])
    # extent = [50, 160, 0, 70]
    extent = (70, 140, 15, 55)
    print(extent)
    # data = get_model_grid(init_time, 'hgt', level=500, extent=extent) # 587.42365
    data = get_model_grid(init_time, 'spfh', level=500, extent=extent)  # 587.42365
    print(extent)
    print(data)

    # C:\Users\Administrator\.metera5\cache\202008030800\hourly\hgt\500\202008030800_56_154_11_59.nc
    # get_model_grid(init_time, 'hgt', level=100)
    # get_model_grid(init_time, 'hgt', level=200)
    # get_model_grid(init_time, 'u', level=100)

    # get_model_grid(init_time, 'u10m')
