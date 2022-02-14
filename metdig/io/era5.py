# -*- coding: utf-8 -*-

import datetime
import os
import sys
import math

import cdsapi
import numpy as np
from sympy import N
import xarray as xr

import sys

import metdig.utl as mdgstda

from metdig.io.lib import utility as utl
from metdig.io.lib import era5_cfg
from metdig.io.lib import config as CONFIG

from metdig.io import era5_manual_download

import logging
logging.basicConfig(format='', level=logging.INFO)  # 此处加这一句代表忽略下属_log作用，直接将_log输出到命令行，测试用
_log = logging.getLogger(__name__)

"""
class ERA5DataService(object):
    '''

    [era5 数据下载工具类。 一次只下载单时次单层次数据, init_time为世界时
    备注：
    1.参数variable均为era5网站下的要素名，详细可以看各个函数下网址链接
    2.参数savefile为保存在本地的全路径
         ]
    '''

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

        if(init_time.year > 1978):
            data_code='reanalysis-era5-pressure-levels'
        else:
            data_code='reanalysis-era5-pressure-levels-preliminary-back-extension'

        c = cdsapi.Client()

        c.retrieve(
            # 'reanalysis-era5-pressure-levels-preliminary-back-extension',
            data_code,
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

        if(init_time.year > 1978):
            data_code='reanalysis-era5-single-levels'
        else:
            data_code='reanalysis-era5-single-levels-preliminary-back-extension'

        c = cdsapi.Client()

        c.retrieve(
            #'reanalysis-era5-single-levels-preliminary-back-extension',
            data_code,
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
"""



def _era5download(era5_bjtimes, var_names, levels, extent, x_percent, y_percent):
    '''
    调用手动下载部分批量下载，自动拆分到缓存目录下，参数为北京时
    '''
    _era5_bjtimes = utl.parm_tolist(era5_bjtimes)
    _levels = utl.parm_tolist(levels)

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

    # 获取本次需要下载的年月日参数
    # 后续还得优化内容包括：
    # 1.根据实际本地已有的数据再下载
    # 2.跨年/月/日数据由于era5下载api会导致多下载数据，短期数据影响不大，长时间数据建议
    def anycache(era5_utctime):
        # 只要有一个缓存文件不存在，就返回False，如果全存在，则返回True
        for var_name in var_names:
            for level in _levels:
                if level is None:
                    cache_file = CONFIG.get_era5cache_file(era5_utctime, var_name, extent, level=level, find_area=True)
                else:
                    cache_file = CONFIG.get_era5cache_file(era5_utctime, var_name, extent, level=None, find_area=True)
                if not os.path.exists(cache_file):
                    return False
        return True
    years = []
    months = []
    days = []
    hours = []
    for era5_bjtime in _era5_bjtimes:
        era5_utctime = era5_bjtime - datetime.timedelta(hours=8)  # 世界时

        if anycache(era5_utctime) == False:
            years.append(era5_utctime.year)
            months.append(era5_utctime.month)
            days.append(era5_utctime.day)
            hours.append(era5_utctime.hour)

    years = list(sorted(set(years)))
    months = list(sorted(set(months)))
    days = list(sorted(set(days)))
    hours = list(sorted(set(hours)))

    if len(years) == 0:
        return

    # 单线程下载
    if all(_levels) == True:
        era5_manual_download.era5_psl_download(_era5_bjtimes[0], _era5_bjtimes[-1], var_names, levels, 
                                               extent=extent, download_dir=None, is_overwrite=False,
                                               years=years, months=months, days=days, hour=hours)
    else:
        era5_manual_download.era5_sfc_download(_era5_bjtimes[0], _era5_bjtimes[-1], var_names, 
                                               extent=extent, download_dir=None, is_overwrite=False,
                                               years=years, months=months, days=days, hour=hours)

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
    _era5download(init_time, [var_name], level, extent, x_percent, y_percent) # 调用手动下载模块批量下载

    init_time_utc = init_time - datetime.timedelta(hours=8)  # 世界时
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

        era5_var = era5_cfg().era5_variable(var_name=var_name, level_type=level_type)
        era5_level = era5_cfg().era5_level(var_name=var_name, level_type=level_type, level=level)
        era5_units = era5_cfg().era5_units(level_type=level_type, var_name=var_name)
    except Exception as e:
        raise Exception(str(e))

    '''
    弃用，此处只读取，更改为调用手动下载模块提前下载
    if not os.path.exists(cache_file):
        if level:
            ERA5DataService().download_hourly_pressure_levels(init_time_utc, era5_var, level, cache_file, extent=extent)
        else:
            ERA5DataService().download_hourly_single_levels(init_time_utc, era5_var, cache_file, extent=extent)
    '''

    # 此处读到的dataset应该只有一个数据集，维度=[time=1,latitude,longitude]，因为下载的时候均是单层次下载
    data = xr.open_dataset(cache_file)
    data = data.to_array()
    data = data.squeeze().transpose('latitude', 'longitude')
    data = data.rename({'latitude': 'lat', 'longitude': 'lon'})

    # 数据裁剪，此处不传xpercent，因为之前已经扩大范围了时候已经扩大范围了
    data = utl.area_cut(data, extent)

    # 经纬度从小到大排序好
    data = data.sortby('lat')
    data = data.sortby('lon')

    stda_data = mdgstda.xrda_to_gridstda(data,
                                         lat_dim='lat', lon_dim='lon',
                                         member=['era5'], level=[era5_level], time=[init_time],
                                         var_name=var_name, np_input_units=era5_units,
                                         data_source='cds', level_type=level_type)
    return stda_data


def get_model_grids(init_times=None, var_name=None, level=None, extent=None, x_percent=0, y_percent=0, **kwargs):
    '''

    [读取单层多时次模式网格数据]

    Keyword Arguments:
        init_times {[list or time]} -- [再分析时间列表] (default: {None})
        var_name {[str]} -- [要素名]
        level {[int32]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    _era5download(init_time, [var_name], level, extent, x_percent, y_percent) # 调用手动下载模块批量下载

    init_times = utl.parm_tolist(init_times)

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
        levels {[list or number]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    _era5download(init_time, [var_name], levels, extent, x_percent, y_percent) # 调用手动下载模块批量下载

    levels = utl.parm_tolist(levels)

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
        init_times {[list or time]} -- [再分析时间列表] (default: {None})
        var_name {[str]} -- [要素名]
        levels {[list or number]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    _era5download(init_times, [var_name], levels, extent, x_percent, y_percent) # 调用手动下载模块批量下载

    init_times = utl.parm_tolist(init_times)
    levels = utl.parm_tolist(levels)

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
        init_times {[list or time]} -- [再分析时间] (default: {None})
        var_name {[str]} -- [要素名]
        levels {[list]} -- [层次，不传代表地面层] (default: {None})
        points {[dict]} -- [站点信息，字典中必须包含经纬度{'lon':[], 'lat':[]}]

    Returns:
        [stda] -- [stda格式数据]
    '''
    levels = utl.parm_tolist(levels)

    # get grids data
    stda_data = get_model_3D_grids(init_time, var_name, levels)

    if stda_data is not None and stda_data.size > 0:
        return mdgstda.gridstda_to_stastda(stda_data, points)
    return None


if __name__ == '__main__':

    # data = get_model_3D_grids([
    #     datetime.datetime(2020, 8, 2, 8),
    #     datetime.datetime(2020, 8, 3, 8),
    #     datetime.datetime(2020, 8, 4, 8)
    # ], 'u10m')
    # print(data)

    data = get_model_grid(datetime.datetime(2020, 8, 2, 8), 'u10m')
    print(data)
    pass