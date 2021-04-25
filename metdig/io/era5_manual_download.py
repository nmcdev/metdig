# -*- coding: utf-8 -*-

import datetime
import os
import sys
import math

import cdsapi
import numpy as np
import xarray as xr
import pandas as pd

import sys

import metdig.utl as mdgstda


from metdig.io.lib import config_era5 as CONFIG
from metdig.io.lib import utl_era5


def _era5_download_hourly_pressure_levels(
        savefile,
        year=[2020],
        month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        day=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        time=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
        pressure_level=[200, 500, 700, 850, 925],
        variable='geopotential',
        extent=[50, 160, 0, 70]):
    '''
    下载基本方法，一次下载要素多个时次多个层次到一个文件中
    参数时间均是世界时
    variable为era5下载要素名
    '''
    # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=form
    if os.path.exists(savefile):
        print('{} 存在 不重复下载'.format(savefile))
        return
    else:
        print('{} 下载...'.format(savefile))

    if not os.path.exists(os.path.dirname(savefile)):
        os.makedirs(os.path.dirname(savefile))

    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': variable,
            'pressure_level': list(map(lambda x: str(x), pressure_level)),
            'year': list(map(lambda x: str(x), year)),
            'month': list(map(lambda x: '{:02d}'.format(x), month)),
            'day': list(map(lambda x: '{:02d}'.format(x), day)),
            'time': list(map(lambda x: '{:02d}:00'.format(x), time)),
            'area': [extent[3], extent[0], extent[2], extent[1]],
        },
        savefile)


def _era5_download_hourly_single_levels(
        savefile,
        year=[2020],
        month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        day=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        time=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
        variable='10m_u_component_of_wind',
        extent=[50, 160, 0, 70]):
    '''
    下载基本方法，一次下载要素多个时次到一个文件中，参数时间均是世界时
    '''
    # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview
    if os.path.exists(savefile):
        print('{} 存在 不重复下载'.format(savefile))
        return
    else:
        print('{} 下载...'.format(savefile))

    if not os.path.exists(os.path.dirname(savefile)):
        os.makedirs(os.path.dirname(savefile))

    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': variable,
            'year': list(map(lambda x: str(x), year)),
            'month': list(map(lambda x: '{:02d}'.format(x), month)),
            'day': list(map(lambda x: '{:02d}'.format(x), day)),
            'time': list(map(lambda x: '{:02d}:00'.format(x), time)),
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
                                 '{0:%Y%m%d%H%M}/hourly/{1}/{6}/{0:%Y%m%d%H%M}_{2}_{3}_{4}_{5}.nc'.format(dt_utc, var_name, extent[0], extent[1], extent[2], extent[3], lv)))
                if os.path.exists(cachefile):
                    print('{} 存在 不重复拆分'.format(cachefile))
                else:
                    print('{} 拆分...'.format(cachefile))
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
                             '{0:%Y%m%d%H%M}/hourly/{1}/{0:%Y%m%d%H%M}_{2}_{3}_{4}_{5}.nc'.format(dt_utc, var_name, extent[0], extent[1], extent[2], extent[3])))
            if os.path.exists(cachefile):
                print('{} 存在 不重复拆分'.format(cachefile))
            else:
                print('{} 拆分...'.format(cachefile))
                if not os.path.exists(os.path.dirname(cachefile)):
                    os.makedirs(os.path.dirname(cachefile))
                data.sel(time=dt_utc).to_netcdf(cachefile)


def era5_psl_download(dt_start=None, dt_end=None, var_names=['hgt', 'u', 'v', 'vvel', 'rh', 'tmp', 'pv', 'div'],
                      pressure_level=[200, 500, 700, 850, 925], extent=[50, 160, 0, 70], download_dir=None):
    '''
    参数时间是北京时，不区分小时，默认24小时全下，下载时按照世界时下载，然后按照世界时自动拆分到cache目录下
    var_names为stda要素名
    '''
    dt_start_utc = dt_start - datetime.timedelta(hours=8)  # 世界时
    dt_end_utc = dt_end - datetime.timedelta(hours=8)  # 世界时
    print('----------------------era5_psl_download--------------------------------')
    savedir = download_dir if download_dir else os.path.join(CONFIG.get_cache_dir(), 'manual_download')
    for var_name in var_names:
        # 按要素一次下载一个要素数据
        savefile = os.path.join(savedir,
                                '{}_{:%Y%m%d}_{:%Y%m%d}_{}_{}_{}_{}.nc'.format(
                                    var_name, dt_start_utc, dt_end_utc, extent[0], extent[1], extent[2], extent[3]))
        era5_var = utl_era5.era5_variable(var_name=var_name, level_type='high')
        years, months, days = _get_ymd(dt_start_utc, dt_end_utc)  # 获取本次需要下载的年月日参数

        _era5_download_hourly_pressure_levels(savefile, years, months, days, pressure_level, era5_var, extent)

        # 将下载后的数据拆分到cache目录下
        _split_psl(savefile, var_name, extent)


def era5_sfc_download(dt_start=None, dt_end=None, var_names=['u10m', 'v10m', 'psfc', 'tcwv', 'prmsl'],
                      extent=[50, 160, 0, 70], download_dir=None):
    '''
    参数时间是北京时，不区分小时，默认24小时全下，下载时按照世界时下载，然后按照世界时自动拆分到cache目录下
    var_names为stda要素名
    '''
    dt_start_utc = dt_start - datetime.timedelta(hours=8)  # 世界时
    dt_end_utc = dt_end - datetime.timedelta(hours=8)  # 世界时
    print('----------------------era5_psl_download--------------------------------')
    savedir = download_dir if download_dir else os.path.join(CONFIG.get_cache_dir(), 'manual_download')
    for var_name in var_names:
        # 按要素一次下载一个要素数据
        savefile = os.path.join(savedir,
                                '{}_{:%Y%m%d}_{:%Y%m%d}_{}_{}_{}_{}.nc'.format(
                                    var_name, dt_start_utc, dt_end_utc, extent[0], extent[1], extent[2], extent[3]))
        era5_var = utl_era5.era5_variable(var_name, level_type='surface')
        years, months, days = _get_ymd(dt_start_utc, dt_end_utc)  # 获取本次需要下载的年月日参数

        _era5_download_hourly_single_levels(savefile, years, months, days, era5_var, extent)

        # 将下载后的数据拆分到cache目录下
        _split_sfc(savefile, var_name, extent)


def test():
    import time as timer
    import multiprocessing as mp

    print('pool')
    pool = mp.Pool(processes=2)
    dt_start = datetime.datetime(2020, 1, 2)
    dt_end = datetime.datetime(2020, 1, 3)

    pool.apply_async(era5_psl_download, (dt_start, dt_end, ['hgt']))
    pool.apply_async(era5_sfc_download, (dt_start, dt_end, ['u10m']))

    pool.close()
    pool.join()

    # era5_psl_download(dt_start=datetime.datetime(2020, 1, 2), dt_end=datetime.datetime(2020, 1, 3), var_names=['hgt'])
    # era5_sfc_download(dt_start=datetime.datetime(2020, 1, 2), dt_end=datetime.datetime(2020, 1, 3), var_names=['u10m'])

    # from metdig.io.era5 import get_model_grid
    # data = get_model_grid(init_time=datetime.datetime(2020,1,1,8), var_name='hgt', level=200, extent=[50, 160, 0, 70],)
    # print(data)


if __name__ == '__main__':
    test()
    pass
