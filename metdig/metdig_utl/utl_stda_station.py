# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import xarray as xr
import numpy as np
import pandas as pd
from copy import deepcopy


import metdig.metdig_utl as mdgstda

def numpy_to_stastda(np_input, members, levels, times, dtimes, ids, lats, lons, 
                     np_input_units='', var_name='', other_input={}, 
                     **attrs_kwargv):
    '''
    
    [numpy数组转stda站点标准格式]
    
    Arguments:
        np_input {[list or ndarray]} -- [numpy或者list数据]
        members {[list or ndarray]} -- [成员列表]
        levels {[list or ndarray or number]} -- [层次列表]
        times {[list] or ndarray or number} -- [起报时间列表]
        dtimes {[list or ndarray or number]} -- [预报失效列表]
        ids {[list or ndarray or number]} -- [站点名列表]
        lats {[list or ndarray or number]} -- [纬度列表]
        lons {[list or ndarray or number]} -- [经度列表]
        **attrs_kwargv {[type]} -- [其它相关属性，如：data_source='cassandra', level_type='high']
    
    Keyword Arguments:
        np_input_units {[str]} -- [np_input数据对应的单位，自动转换为能查询到的stda单位]
        other_input {dict} -- [其它坐标信息] (default: {{}})
        var_name {str} -- [要素名] (default: {''})
    
    Returns:
        [STDA] -- [STDA网格数据]
    '''

    # get attrs
    stda_attrs = mdgstda.get_stda_attrs(var_name=var_name, **attrs_kwargv)

    other_input_names = list(other_input.keys())

    # 初始化stda
    df = pd.DataFrame(columns=['level', 'time', 'dtime', 'id', 'lon', 'lat'] + other_input_names + list(members))
    # 数据列 单位转换成stda标准单位
    _temp_data, stda_attrs['var_units'] = mdgstda.numpy_units_to_stda(np_input, np_input_units, stda_attrs['var_units'])
    _member_len = len(list(members))
    _temp_data = _temp_data.reshape((int(_temp_data.size/_member_len), _member_len))
    for i,m in enumerate(members):
        df[m] = _temp_data[:,i]

    # 7+N列：其它坐标信息列
    for other_name in other_input_names:
        df[other_name] = other_input[other_name]
    # 1-6列：基本列
    df['level'] = levels
    df['time'] = times
    df['dtime'] = dtimes
    df['id'] = ids
    df['lon'] = lons
    df['lat'] = lats

    # 属性
    df.attrs = stda_attrs
    df.attrs['data_start_columns'] = 6 + len(other_input.keys())

    return df


def gridstda_to_stastda(grid_stda_data, points={}):
    '''

    [stda网格数据，插值到站点上，返回stda格点数据]

    Arguments:
        grid_stda_data {[type]} -- [stda网格数据]

    Keyword Arguments:
        points {dict} -- [如：points={'lon': [116.3833], 'lat': [39.9]}] (default: {{}})

    Returns:
        [type] -- [stda格点数据]
    '''

    points['lon'] = np.array(points['lon'])
    points['lat'] = np.array(points['lat'])

    # id如果不存在，则赋值默认值为空字符串
    if 'id' in points.keys():
        points['id'] = np.array(points['id'])
    else:
        points['id'] = np.arange(1, points['lon'].size + 1)
    other = list(set(points.keys()).difference(set(['lon', 'lat', 'id'])))  # points中除去lon lat id之外的其它坐标信息名称

    # get points data
    points_xr = grid_stda_data.interp(lon=('points', points['lon']), lat=('points', points['lat']))
    # print(points_xr)
    # print(points_xr.values.shape)

    # get attrs
    attrs = deepcopy(grid_stda_data.attrs)
    attrs['data_start_columns'] = 6 + len(other)

    # points data to pd.DataFrame
    columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat'] + other + list(grid_stda_data['member'].values)
    lines = []
    for i_lv, _lv in enumerate(points_xr['level'].values):
        for i_t, _t in enumerate(points_xr['time'].values):
            for i_d, _d in enumerate(points_xr['dtime'].values):
                _d = int(_d)
                for i_id, _id in enumerate(points['id']):
                    _other = [points[_o][i_id] for _o in other]  # 除去lon lat id之外的其它坐标信息名称对应的数据
                    _lon = points['lon'][i_id]
                    _lat = points['lat'][i_id]
                    _data = points_xr.values[:, i_lv, i_t, i_d, i_id]
                    line = [_lv, _t, _d, _id, _lon, _lat] + _other + list(_data)
                    lines.append(line)

    df = pd.DataFrame(lines, columns=columns)
    df.attrs = attrs

    return df


def stastda_copy(data, iscopy_otherdim=True, iscopy_value=True):
    '''

    [站点stda复制操作，不复制任何属性]

    Arguments:
        data {[stda]} -- [stda站点数据]

    Keyword Arguments:
        iscopy_otherdim {bool} -- [是否拷贝7-N列其它坐标信息] (default: {True})
        iscopy_value {bool} -- [是否拷贝N+1列起的数据列] (default: {True})

    Returns:
        [stda] -- [拷贝后的数据]
    '''
    idx1 = 6
    idx2 = data.attrs['data_start_columns']
    newdata = data.copy(deep=True)

    if iscopy_otherdim == False and iscopy_value == True:
        # 其它坐标信息不拷贝，数据值拷贝
        newdata = newdata.drop(columns=data.columns[idx1: idx2], axis=1)

    if iscopy_otherdim == True and iscopy_value == False:
        # 其它坐标信息拷贝，数据值不拷贝
        newdata = newdata.drop(columns=data.columns[idx2:], axis=1)

    if iscopy_otherdim == False and iscopy_value == False:
        # 其它坐标信息不拷贝，数据值不拷贝
        newdata = newdata.drop(columns=data.columns[idx1:], axis=1)

    return newdata


@pd.api.extensions.register_dataframe_accessor('stda')
class __STDADataFrameAccessor(object):
    def __init__(self, df):
        self._df = df

    @property
    def fcst_time(self):
        '''
        [获取预报时间（time列+dtime列），返回值类型为pd.series]
        '''
        return pd.to_datetime(self._df['time']) + pd.to_timedelta(self._df['dtime'], unit='h')

    @property
    def data(self):
        '''
        [获取数据（自data_start_columns起所有列），返回值类型为pd.dataframe]
        '''
        return self._df.iloc[:, self._df.attrs['data_start_columns']:]

    @property
    def member_name(self):
        '''
        [获取数据列名（自data_start_columns起所有列），返回值类型为list]
        '''
        return self._df.columns[self._df.attrs['data_start_columns']:]

    def to_grid(self):

        # return data, level, time, dtime, id, lon, lat
        pass

    def plot(self):
        # plot this array's data on a map, e.g., using Cartopy
        pass


if __name__ == '__main__':
    pass
