# -*- coding: utf-8 -*-

import datetime

import xarray as xr
import numpy as np
import pandas as pd
from metpy.units import units

import metdig.metdig_utl as mdgstda


def numpy_to_gridstda(np_input, members, levels, times, dtimes, lats, lons, 
                      np_input_units='', var_name='', 
                      **attrs_kwargv):
    '''
    
    [numpy数组转stda网格标准格式]
    
    Arguments:
        np_input {[ndarray]} -- [numpy数据,维度必须为('member', 'level', 'time', 'dtime', 'lat', 'lon')]
        members {[list or ndarray]} -- [成员列表]
        levels {[list or ndarray]} -- [层次列表]
        times {[list] or ndarray} -- [起报时间列表]
        dtimes {[list or ndarray]} -- [预报失效列表]
        lats {[list or ndarray]} -- [纬度列表]
        lons {[list or ndarray]} -- [经度列表]
        **attrs_kwargv {[type]} -- [其它相关属性，如：data_source='cassandra', level_type='high']
    
    Keyword Arguments:
        np_input_units {[str]} -- [np_input数据对应的单位，自动转换为能查询到的stda单位]
        var_name {str} -- [要素名] (default: {''})
    
    Returns:
        [STDA] -- [STDA网格数据]
    '''

    # get attrs
    stda_attrs = mdgstda.get_stda_attrs(var_name=var_name, **attrs_kwargv)

    # 单位转换
    data, data_units = mdgstda.numpy_units_to_stda(np_input, np_input_units, stda_attrs['var_units'])

    stda_attrs['var_units'] = data_units

    members = np.array(members)
    levels = np.array(levels)
    times = np.array(times)
    dtimes = np.array(dtimes)
    lats = np.array(lats)
    lons = np.array(lons)

    '''
    弃用Dataset
    # create STDA xarray.Dataset
    stda_data = xr.Dataset()
    stda_data['data'] = (['member', 'level', 'time', 'dtime', 'lat', 'lon'], data, stda_attrs)

    stda_data.coords['member'] = ('member', members)
    stda_data.coords['level'] = ('level', levels)
    stda_data.coords['time'] = ('time', times)
    stda_data.coords['dtime'] = ('dtime', dtimes)
    stda_data.coords['lat'] = ('lat', lats)
    stda_data.coords['lon'] = ('lon', lons)
    '''

    # create STDA xarray.DataArray
    coords = [('member', members),
              ('level', levels),
              ('time', times),
              ('dtime', dtimes),
              ('lat', lats),
              ('lon', lons), ]
    stda_data = xr.DataArray(data, coords=coords)
    stda_data.attrs = stda_attrs

    return stda_data


def gridstda_full_like(a, fill_value, dtype=None, var_name='', **attrs_kwargv):
    '''

    [返回一个和参数a具有相同维度信息的STDA数据，并且均按fill_value填充该stda]

    Arguments:
        a {[stda]} -- [description]
        fill_value {[scalar]} -- [Value to fill the new object with before returning it]
        **attrs_kwargv {[type]} -- [其它相关属性，如：data_source='cassandra', level_type='high', data_name='ecmwf']

    Keyword Arguments:
        dtype {[dtype, optional]} -- [dtype of the new array. If omitted, it defaults to other.dtype] (default: {None})
        var_name {str} -- [要素名] (default: {''})

    Returns:
        [stda] -- [stda网格数据]
    '''
    stda_data = xr.full_like(a, fill_value, dtype=dtype)
    stda_data.attrs = mdgstda.get_stda_attrs(var_name=var_name, **attrs_kwargv)
    return stda_data


def gridstda_full_like_by_levels(a, levels, dtype=None, var_name='pres', **attrs_kwargv):
    '''

    [返回一个和参数a具有相同维度信息的stda数据，并且按参数levels逐层赋值]

    Arguments:
        a {[type]} -- [description]
        levels {[type]} -- [description]
        **attrs_kwargv {[type]} -- [其它相关属性，如：data_source='cassandra', level_type='high', data_name='ecmwf']

    Keyword Arguments:
        dtype {[dtype, optional]} -- [dtype of the new array. If omitted, it defaults to other.dtype] (default: {None})
        var_name {str} -- [要素名] (default: {'pres'})

    Returns:
        [stda] -- [stda网格数据]
    '''

    # 后续可以改为stda_broadcast_levels， xr.broadcast(a, levels.squeeze())
    stda_data = gridstda_full_like(a, 0, var_name=var_name, **attrs_kwargv)
    for i, lev in enumerate(levels):
        stda_data.values[:, i, :, :, :, :] = lev
    return stda_data


@xr.register_dataarray_accessor('stda')
class __STDADataArrayAccessor(object):
    def __init__(self, xr):
        self._xr = xr

    @property
    def fcst_time(self):
        '''
        [获取预报时间（time*dtime)，返回值类型为list]
        '''
        times = []
        for time in self._xr['time'].values:
            for dtime in self._xr['dtime'].values:
                _ = pd.to_datetime(time).replace(tzinfo=None).to_pydatetime() + datetime.timedelta(hours=int(dtime))
                times.append(_)
        return times


if __name__ == '__main__':
    pass
