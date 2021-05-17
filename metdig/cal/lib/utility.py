# -*- coding: utf-8 -*-

import xarray as xr
import pandas as pd
import numpy as np

from metpy.units import units 

import metdig.utl as mdgstda

def stda_to_quantity(data):
    '''

    []

    Arguments:
        data {[stda]} -- [stda data]

    Returns:
        [quantity] -- [description]
    '''
    if isinstance(data, xr.DataArray):
        return data.values * units(data.attrs['var_units'])
    elif isinstance(data, pd.DataFrame):
        # return data.iloc[:, data.attrs['data_start_columns']:].values * units(data.attrs['var_units']) # 弃用
        return data.stda.data.values.squeeze() * units(data.attrs['var_units']) # 此处加squeeze保证只有一列的时候返回的是个一维数组，只有一行一列的返回的是一个数值
    else:
        raise Exception('stda_to_quantity Failed! type(data) must be pd.DataFrame or xr.DataArray!')


def stda_to_numpy(data):
    '''

    []

    Arguments:
        data {[stda]} -- [stda data]

    Returns:
        [ndarray] -- [description]
    '''

    if isinstance(data, xr.DataArray):
        return data.values
    elif isinstance(data, pd.DataFrame):
        # return data.iloc[:, data.attrs['data_start_columns']:].values # 弃用
        return data.stda.data.values.squeeze() # 此处加squeeze保证只有一列的时候返回的是个一维数组，只有一行一列的返回的是一个数值


def quantity_to_stda_byreference(var_name, data, reference_variables):
    '''

    [根据reference_variables(stda格式)，将data(Quantity)转换成功stda格式，其中坐标信息均来自于reference_variables。
    注意，此处data需要外部转换好单位再进入此函数，此函数不涉及单位转换]

    Arguments:
        data {[quantity]} -- [需要转换的数据]
        reference_variables {[stda]} -- [参考stda数据，经纬度等维度信息均参考此变量]

    Raises:
        Exception -- [description]
    '''
    if isinstance(reference_variables, xr.DataArray):
        stda_data = mdgstda.numpy_to_gridstda(
            np.array(data),
            reference_variables['member'].values, reference_variables['level'].values, reference_variables['time'].values,
            reference_variables['dtime'].values, reference_variables['lat'].values, reference_variables['lon'].values,
            var_name=var_name, np_input_units=str(data.units),
        )
        return stda_data

    elif isinstance(reference_variables, pd.DataFrame):
        stda_data = mdgstda.stastda_copy(reference_variables, iscopy_otherdim=True, iscopy_value=False)
        stda_data.attrs = mdgstda.get_stda_attrs(var_name=var_name)
        stda_data.attrs['data_start_columns'] = reference_variables.attrs['data_start_columns']
        member = reference_variables.stda.member[0]
        stda_data[member] = np.array(data)
        return stda_data

    else:
        raise Exception('stda_to_Quantity Failed! type(reference_variables) must be pd.DataFrame or xr.DataArray!')

