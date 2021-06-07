# -*- coding: utf-8 -*-

import datetime

import xarray as xr
import numpy as np
import pandas as pd
from metpy.units import units

import metdig.utl as mdgstda

__all__ = [
    'numpy_to_gridstda',
    'gridstda_full_like',
    'gridstda_full_like_by_levels',
]

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
    """
    stda 格式说明: 维度定义为(member, level, time, dtime, lat, lon)
    """

    def __init__(self, xr):
        self._xr = xr

    @property
    def level(self):
        '''
        获取level, 返回值为pd.series
        '''
        return pd.Series(self._xr['level'].values)

    @property
    def fcst_time(self):
        '''
        [获取预报时间（time*dtime)，返回值类型为pd.series]
        '''
        fcst_time = []
        for time in self._xr['time'].values:
            for dtime in self._xr['dtime'].values:
                _ = pd.to_datetime(time).replace(tzinfo=None).to_pydatetime() + datetime.timedelta(hours=int(dtime))
                fcst_time.append(_)
        return pd.Series(fcst_time)

    @property
    def time(self):
        '''
        获取time，返回值类型为pd.series
        '''
        time = pd.to_datetime(self._xr['time'].values)
        return pd.Series(time)

    @property
    def dtime(self):
        '''
        获取dtime，返回值类型为pd.series
        '''
        return pd.Series(self._xr['dtime'].values)

    @property
    def lat(self):
        '''
        获取lat，返回值类型为pd.series
        '''
        return pd.Series(self._xr['lat'].values)

    @property
    def lon(self):
        '''
        获取lon，返回值类型为pd.series
        '''
        return pd.Series(self._xr['lon'].values)

    @property
    def member(self):
        '''
        获取member，返回值类型为pd.series
        '''
        return pd.Series(self._xr['member'].values)

    def description(self):
        '''
        获取描述信息，格式如下:
        起报时间: Y年m月d日H时
        预报时间: Y年m月d日H时
        预报时效: 小时
        www.nmc.cn
        '''
        init_time = self.time[0]
        fhour = self.dtime[0]
        fcst_time = self.fcst_time[0]

        if fhour != 0:
            description = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(
                init_time, fcst_time, fhour)
        else:
            description = '分析时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n实况/分析\nwww.nmc.cn'.format(init_time)
        return description
    
    def description_point(self, describe=''):
        '''
        获取描述信息，格式如下
        起报时间: Y年m月d日H时
        [data_name]N小时预报describe
        预报点: lon, lat
        www.nmc.cn

        起报时间: Y年m月d日H时
        [data_name]实况info
        分析点: lon, lat
        www.nmc.cn
        '''
        init_time = self.time[0]
        fhour = self.dtime[0]
        point_lon = self.lon[0]
        point_lat = self.lat[0]
        data_name = self.member[0].upper()

        if(fhour != 0):
            description = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]{2}小时预报{5}\n预报点: {3}, {4}\nwww.nmc.cn'.format(
                init_time, data_name, fhour, point_lon, point_lat, describe)
        else:
            description = '分析时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]实况/分析{4}\n分析点: {2}, {3}\nwww.nmc.cn'.format(
                init_time, data_name, point_lon, point_lat, describe)
        return description    


    def get_dim_value(self, dim_name):
        '''
        获取维度信息，如果dim_name=='fcst_time'情况下，特殊处理，范围time*dtime
        返回值为numpy
        '''
        if dim_name == 'fcst_time':
            return self.fcst_time.values
        if dim_name == 'time':
            return self.time.values
        return self._xr[dim_name].values

    def get_value(self, ydim='lat', xdim='lon', xunits=False):
        '''
        获取二维数据，假如stda不是二维的数据，则报错
        返回值为numpy
        '''
        if xdim == 'fcst_time':
            if self._xr['time'].values.size == 1:  # 因为是二维，假如time维长度为1，则有维度的肯定在dtime维
                xdim = 'dtime'
            else:
                xdim = 'time'
        if ydim == 'fcst_time':
            if self._xr['time'].values.size == 1:
                ydim = 'dtime'
            else:
                ydim = 'time'
        data = self._xr.squeeze().transpose(ydim, xdim).values
        if xunits == True:
            data = data * units(self._xr.attrs['var_units'])
        return data


if __name__ == '__main__':
    pass
