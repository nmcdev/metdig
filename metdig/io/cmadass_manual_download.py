# -*- coding: utf-8 -*-

import datetime
import os
import sys
import math
from concurrent import futures

import numpy as np
import xarray as xr
import pandas as pd

import sys

import metdig


from metdig.io.lib import config as CONFIG

import logging
_log = logging.getLogger(__name__)


def _cmadass_download_hourly_pressure_levels(
        init_time,
        fhours=[24, 48, 72],
        levels=[200, 500, 700, 850, 925],
        var_name='hgt',
        data_name='cma_gfs',
        extent=[50, 160, 0, 70]):
    '''
    目前先采用已有的get_model_3D_grids，如果后续api提供一次性下载多维函数，则修改该模块
    '''
    metdig.io.cmadaas.get_model_3D_grids(init_time=init_time, fhours=fhours, data_name=data_name, var_name=var_name,
                                         levels=levels, extent=extent)


def _cmadass_download_hourly_single_levels(
        init_time,
        fhours=[24, 48, 72],
        var_name='u10m',
        data_name='cma_gfs',
        extent=[50, 160, 0, 70]):
    '''
    目前先采用已有的get_model_3D_grids，如果后续api提供一次性下载多维函数，则修改该模块
    '''
    metdig.io.cmadaas.get_model_3D_grids(init_time=init_time, fhours=fhours, data_name=data_name, var_name=var_name,
                                         extent=extent)


def cmadass_psl_download_usepool(
        init_time, data_name='cma_gfs', var_names=['hgt', 'u', 'v', 'vvel', 'rh', 'tmp', 'pv', 'div', 'spfh', 'vort'],
        levels=[200, 225, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700,
                750, 775, 800, 825, 850, 875, 900, 925, 950, 975, 1000],
        fhours=np.arange(0, 24, 1).tolist(),
        extent=[50, 160, 0, 70],
        max_pool=2):
    '''
    参数时间是北京时
    采用多线程下载
    '''
    with futures.ThreadPoolExecutor(max_workers=max_pool) as executor:
        tasks = []
        for var_name in var_names:
            tasks.append(executor.submit(_cmadass_download_hourly_pressure_levels,
                                         init_time, fhours, levels, var_name, data_name, extent))

        futures.wait(tasks, return_when=futures.ALL_COMPLETED)


def cmadass_sfc_download_usepool(
        init_time, data_name='cma_gfs',
        var_names=['u10m', 'u100m', 'v10m', 'v100m', 'psfc', 'tcwv', 'prmsl', 't2m', 'td2m', 'rain01', 'cape', 'cin', 'k_idx'],
        fhours=np.arange(0, 24, 1).tolist(),
        extent=[50, 160, 0, 70],
        max_pool=2):
    '''
    参数时间是北京时
    采用多线程下载
    '''
    with futures.ThreadPoolExecutor(max_workers=max_pool) as executor:
        tasks = []
        for var_name in var_names:
            tasks.append(executor.submit(_cmadass_download_hourly_single_levels,
                                         init_time, fhours, var_name, data_name, extent))

        futures.wait(tasks, return_when=futures.ALL_COMPLETED)


def test():
    init_time = datetime.datetime(2021, 7, 17, 0)  # 北京时
    # fhours = [0, 4, 6, 9, 12]
    fhours = [8]

    cmadass_psl_download_usepool(init_time, data_name='cma_gfs', var_names=['hgt', 'u', 'v'], fhours=fhours)
    cmadass_sfc_download_usepool(init_time, data_name='cma_gfs', var_names=['u10m', 'v10m'], fhours=fhours)


if __name__ == '__main__':
    test()
    pass
