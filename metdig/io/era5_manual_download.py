# -*- coding: utf-8 -*-

import datetime
import os
import sys
import math
import multiprocessing

import cdsapi
import numpy as np
import xarray as xr
import pandas as pd

import sys

import metdig.utl as mdgstda


from metdig.io.lib import config as CONFIG
from metdig.io.lib import era5_cfg

import logging
_log = logging.getLogger(__name__)


def _era5_download_hourly_pressure_levels(
        savefile,
        year=[2020],
        month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        day=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        hour=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
        pressure_level=[200, 500, 700, 850, 925],
        variable='geopotential',
        extent=[50, 160, 0, 70],
        is_overwrite=True):
    '''
    下载基本方法，一次下载要素多个时次多个层次到一个文件中
    参数时间均是世界时
    variable为era5下载要素名
    is_overwrite==True时会重复下载，覆盖已经存在的数据
    '''
    # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=form
    if os.path.exists(savefile) and is_overwrite == False:
        _log.info('{} 存在 不重复下载'.format(savefile))
        return
    else:
        _log.info('{} 下载...'.format(savefile))

    if not os.path.exists(os.path.dirname(savefile)):
        os.makedirs(os.path.dirname(savefile))

    if(year > 1978):
        data_code='reanalysis-era5-pressure-levels'
    else:
        data_code='reanalysis-era5-pressure-levels-preliminary-back-extension'

    c = cdsapi.Client(quiet=True)

    c.retrieve(
        # 'reanalysis-era5-pressure-levels',
        # 'reanalysis-era5-pressure-levels-preliminary-back-extension',
        data_code,
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': variable,
            'pressure_level': list(map(lambda x: str(x), pressure_level)),
            'year': list(map(lambda x: str(x), year)),
            'month': list(map(lambda x: '{:02d}'.format(x), month)),
            'day': list(map(lambda x: '{:02d}'.format(x), day)),
            'time': list(map(lambda x: '{:02d}:00'.format(x), hour)),
            'area': [extent[3], extent[0], extent[2], extent[1]],
        },
        savefile)


def _era5_download_hourly_single_levels(
        savefile,
        year=[2020],
        month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        day=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        hour=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
        variable='10m_u_component_of_wind',
        extent=[50, 160, 0, 70],
        is_overwrite=True):
    '''
    下载基本方法，一次下载要素多个时次到一个文件中，参数时间均是世界时
    is_overwrite==True时会重复下载，覆盖已经存在的数据
    '''
    # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview
    if os.path.exists(savefile) and is_overwrite == False:
        _log.info('{} 存在 不重复下载'.format(savefile))
        return
    else:
        _log.info('{} 下载...'.format(savefile))

    if not os.path.exists(os.path.dirname(savefile)):
        os.makedirs(os.path.dirname(savefile))

    c = cdsapi.Client(quiet=True)

    if(year > 1978):
        data_code='reanalysis-era5-single-levels'
    else:
        data_code='reanalysis-era5-single-levels-preliminary-back-extension'
    c.retrieve(
        #'reanalysis-era5-single-levels',
        data_code,
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': variable,
            'year': list(map(lambda x: str(x), year)),
            'month': list(map(lambda x: '{:02d}'.format(x), month)),
            'day': list(map(lambda x: '{:02d}'.format(x), day)),
            'time': list(map(lambda x: '{:02d}:00'.format(x), hour)),
            'area': [extent[3], extent[0], extent[2], extent[1]],
        },
        savefile)


def _get_ymd(dt_start, dt_end):
    # 根据两个日期获取下载的ear5年月日参数
    years = []
    months = []
    days = []
    while dt_start <= dt_end:
        years.append(dt_start.year)
        months.append(dt_start.month)
        days.append(dt_start.day)
        dt_start += datetime.timedelta(days=1)

    years = list(sorted(set(years)))
    months = list(sorted(set(months)))
    days = list(sorted(set(days)))

    return years, months, days


def _split_psl(savefile, var_name, extent):
    # 拆分下载的psl数据到cache目录下
    if os.path.exists(savefile):
        data = xr.load_dataarray(savefile)
        for dt_utc in data['time'].values:
            dt_utc = pd.to_datetime(dt_utc)
            for lv in data['level'].values:
                # cache目录为世界时
                cachefile = os.path.join(
                    os.path.join(CONFIG.get_cache_dir(),
                                 'ERA5_DATA/{0:%Y%m%d%H%M}/hourly/{1}/{6}/{0:%Y%m%d%H%M}_{2}_{3}_{4}_{5}.nc'.format(dt_utc, var_name, extent[0], extent[1], extent[2], extent[3], lv)))
                if os.path.exists(cachefile):
                    _log.info('{} 存在 不重复拆分'.format(cachefile))
                else:
                    _log.info('{} 拆分...'.format(cachefile))
                    if not os.path.exists(os.path.dirname(cachefile)):
                        os.makedirs(os.path.dirname(cachefile))
                    data.sel(time=dt_utc, level=lv).to_netcdf(cachefile)


def _split_sfc(savefile, var_name, extent):
    # 拆分下载的sfc数据到cache目录下
    if os.path.exists(savefile):
        data = xr.load_dataarray(savefile)
        for dt_utc in data['time'].values:
            dt_utc = pd.to_datetime(dt_utc)
            # cache目录为世界时
            cachefile = os.path.join(
                os.path.join(CONFIG.get_cache_dir(),
                             'ERA5_DATA/{0:%Y%m%d%H%M}/hourly/{1}/{0:%Y%m%d%H%M}_{2}_{3}_{4}_{5}.nc'.format(dt_utc, var_name, extent[0], extent[1], extent[2], extent[3])))
            if os.path.exists(cachefile):
                _log.info('{} 存在 不重复拆分'.format(cachefile))
            else:
                _log.info('{} 拆分...'.format(cachefile))
                if not os.path.exists(os.path.dirname(cachefile)):
                    os.makedirs(os.path.dirname(cachefile))
                data.sel(time=dt_utc).to_netcdf(cachefile)


def era5_psl_download(dt_start=None, dt_end=None, var_names=['hgt', 'u', 'v', 'vvel', 'rh', 'tmp', 'pv', 'div','spfh'],
                      pressure_level=[200, 500, 700, 850, 925],
                      hour=np.arange(0,24,3).tolist(),
                      extent=[50, 160, 0, 70], download_dir=None, is_overwrite=True):
    '''
    参数时间是北京时，下载时按照世界时下载，然后按照世界时自动拆分到cache目录下
    var_names为stda要素名
    is_overwrite==True时会重复下载，覆盖已经存在的数据
    '''
    dt_start_utc = dt_start - datetime.timedelta(hours=8)  # 世界时
    dt_end_utc = dt_end - datetime.timedelta(hours=8)  # 世界时
    _log.info('----------------------era5_psl_download--------------------------------')
    savedir = download_dir if download_dir else os.path.join(CONFIG.get_cache_dir(), 'ERA5_DATA/manual_download')
    for var_name in var_names:
        # 按要素一次下载一个要素数据
        savefile = os.path.join(savedir,
                                '{}_{:%Y%m%d}_{:%Y%m%d}_{}_{}_{}_{}.nc'.format(
                                    var_name, dt_start_utc, dt_end_utc, extent[0], extent[1], extent[2], extent[3]))
        era5_var = era5_cfg().era5_variable(var_name=var_name, level_type='high')
        years, months, days = _get_ymd(dt_start_utc, dt_end_utc)  # 获取本次需要下载的年月日参数
        _era5_download_hourly_pressure_levels(savefile=savefile, year=years, month=months, day=days, hour=hour,
                                              pressure_level=pressure_level, variable=era5_var, extent=extent, is_overwrite=is_overwrite)

        # 将下载后的数据拆分到cache目录下
        _split_psl(savefile, var_name, extent)


def era5_sfc_download(dt_start=None, dt_end=None, var_names=['u10m','u100m', 'v10m','v100m', 'psfc', 'tcwv', 'prmsl','t2m','td2m'],
                      hour=np.arange(0,24,3).tolist(),
                      extent=[50, 160, 0, 70], download_dir=None, is_overwrite=True):
    '''
    参数时间是北京时，下载时按照世界时下载，然后按照世界时自动拆分到cache目录下
    var_names为stda要素名
    is_overwrite==True时会重复下载，覆盖已经存在的数据
    '''
    dt_start_utc = dt_start - datetime.timedelta(hours=8)  # 世界时
    dt_end_utc = dt_end - datetime.timedelta(hours=8)  # 世界时
    _log.info('----------------------era5_psl_download--------------------------------')
    savedir = download_dir if download_dir else os.path.join(CONFIG.get_cache_dir(), 'ERA5_DATA/manual_download')
    for var_name in var_names:
        # 按要素一次下载一个要素数据
        savefile = os.path.join(savedir,
                                '{}_{:%Y%m%d}_{:%Y%m%d}_{}_{}_{}_{}.nc'.format(
                                    var_name, dt_start_utc, dt_end_utc, extent[0], extent[1], extent[2], extent[3]))
        era5_var = era5_cfg().era5_variable(var_name, level_type='surface')
        years, months, days = _get_ymd(dt_start_utc, dt_end_utc)  # 获取本次需要下载的年月日参数

        _era5_download_hourly_single_levels(savefile=savefile, year=years, month=months, day=days, hour=hour,
                                            variable=era5_var, extent=extent, is_overwrite=is_overwrite)

        # 将下载后的数据拆分到cache目录下
        _split_sfc(savefile, var_name, extent)


def era5_psl_download_usepool(dt_start=None, dt_end=None, var_names=['hgt', 'u', 'v', 'vvel', 'rh', 'tmp', 'pv', 'div','spfh'],
                              pressure_level=[200,225,250,300,350,400,450,500,550,600,650,700,
                              750,775,800,825,850,875,900,925,950,975,1000],
                              hour=np.arange(0,24,1).tolist(),
                              extent=[50, 160, 0, 70], download_dir=None, max_pool=2, is_overwrite=True):
    '''
    参数时间是北京时，下载时按照世界时下载，然后按照世界时自动拆分到cache目录下
    var_names为stda要素名
    采用多进程下载
    '''
    pool = multiprocessing.Pool(processes=max_pool)
    for var_name in var_names:
        pool.apply_async(era5_psl_download, (dt_start, dt_end, [var_name], pressure_level, hour, extent, download_dir, is_overwrite))
    pool.close()
    pool.join()


def era5_sfc_download_usepool(dt_start=None, dt_end=None, var_names=['u10m','u100m', 'v10m','v100m', 'psfc', 'tcwv', 'prmsl','t2m','td2m'],
                              hour=np.arange(0,24,1).tolist(),
                              extent=[50, 160, 0, 70], download_dir=None, max_pool=2, is_overwrite = True):
    '''
    参数时间是北京时，下载时按照世界时下载，然后按照世界时自动拆分到cache目录下
    var_names为stda要素名
    采用多进程下载
    '''
    pool = multiprocessing.Pool(processes=max_pool)
    for var_name in var_names:
        pool.apply_async(era5_sfc_download, (dt_start, dt_end, [var_name], hour, extent, download_dir, is_overwrite))
    pool.close()
    pool.join()


def test():
    dt_start = datetime.datetime(2020, 1, 2)  # 北京时
    dt_end = datetime.datetime(2020, 1, 3)
    hour = [0, 4, 6, 9, 12]

    era5_psl_download_usepool(dt_start, dt_end, var_names=['hgt', 'u', 'v'], hour=hour)
    era5_sfc_download_usepool(dt_start, dt_end, var_names=['u10m', 'v10m'], hour=hour)


if __name__ == '__main__':
    test()
    pass
