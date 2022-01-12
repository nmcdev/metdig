# -*- coding: utf-8 -*-

import xarray as xr
import numpy as np
import pandas as pd
from copy import deepcopy

from metpy.units import units
import metdig.utl as mdgstda

__all__ = [
    'numpy_to_stastda',
    'gridstda_to_stastda',
    'stastda_copy',
    'stastda_to_gridstda',
]


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
    for i, m in enumerate(members):
        df[m] = _temp_data[:, i]

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


def gridstda_to_stastda(grid_stda_data, points={},method='linear'):
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
    points_xr = grid_stda_data.interp(lon=('points', points['lon']), lat=('points', points['lat']),method=method)
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


def stastda_to_gridstda(df, xdim='lon', ydim='lat'):
    '''
    根据给定的xdim ydim 将站点stda转换为二维格点stda，缺失点填充nan，
    （后续可以再优化成多维的）
    注意事项：
    方法不涉及插值，只是简单放到二维网格
    1. 要求输入的站点stda除xdim ydim两维外，其余维度去重后长度为1
    2. 站点stda的id不可作为xdim ydim参数，因为格点stda中没有这一维度
    3. 站点stda的id会以属性的方式写到格点stda中
    4. data_start_columns不会写到格点stda属性中
    '''
    member = df.stda.member.values[0]
    griddims = {}
    for col in ['level', 'time', 'dtime', 'id', 'lon', 'lat']:
        dimvalue = np.unique(df[col].values)
        if col != xdim and col != ydim:
            if dimvalue.size > 1:
                raise Exception('除输入参数的xdim ydim，其余维度去重后长度必须为1')
        griddims[col] = np.sort(dimvalue)

    _grid2d_y, _grid2d_x = np.meshgrid(griddims[ydim], griddims[xdim])
    _grid2d_df = pd.DataFrame()
    _grid2d_df[xdim] = _grid2d_x.flatten()
    _grid2d_df[ydim] = _grid2d_y.flatten()
    # 按照_grid2d_df合并，(对输入的df去重，保证merge正常)
    _grid2d_df = pd.merge(_grid2d_df, df.drop_duplicates(subset=[xdim, ydim], keep='first'), how='left', on=[xdim, ydim])
    _grid2d_data = _grid2d_df[member].values.reshape(_grid2d_x.shape)

    # 处理成stda
    coords = [(xdim, griddims[xdim]),
              (ydim, griddims[ydim]), ]
    _grid2d_xr = xr.DataArray(_grid2d_data, coords=coords)
    for dim in ('level', 'time', 'dtime', 'lat', 'lon'):
        if dim != xdim and dim != ydim:
            _grid2d_xr = _grid2d_xr.expand_dims({dim: griddims[col]})
    _grid2d_xr = _grid2d_xr.expand_dims({'member': [member]})
    _grid2d_xr = _grid2d_xr.transpose('member', 'level', 'time', 'dtime', 'lat', 'lon')
    _grid2d_xr.attrs = {'id': griddims['id']}
    try:
        _grid2d_xr.attrs.update(df.attrs)
        _grid2d_xr.attrs.pop('data_start_columns')
    except:
        pass
    return _grid2d_xr


@pd.api.extensions.register_dataframe_accessor('stda')
class __STDADataFrameAccessor(object):
    """
    stda 格式说明: 列定义为(level, time, dtime, id, lon, lat, member1, member2...)
    """

    def __init__(self, df):
        self._df = df

    @property
    def level(self):
        """[get level]

        Returns:
            [pd.series]: [level]
        """
        return pd.Series(self._df['level'].values)

    @property
    def fcst_time(self):
        """[get fcst_time*dtime)]

        Returns:
            [pd.series]: [fcst_time]
        """
        fcst_time = pd.to_datetime(self._df['time']) + pd.to_timedelta(self._df['dtime'], unit='h')
        return pd.Series(fcst_time)

    @property
    def time(self):
        """[get time]

        Returns:
            [pd.series]: [time]
        """
        time = pd.to_datetime(self._df['time'].values)
        return pd.Series(time)

    @property
    def dtime(self):
        """[get dtime]

        Returns:
            [pd.series]: [dtime]
        """
        return pd.Series(self._df['dtime'].values)

    @property
    def id(self):
        """[get id]

        Returns:
            [pd.series]: [id]
        """
        return pd.Series(self._df['id'].values)

    @property
    def lat(self):
        """[get lat]

        Returns:
            [pd.series]: [lat]
        """
        return pd.Series(self._df['lat'].values)

    @property
    def lon(self):
        """[get lon]

        Returns:
            [pd.series]: [lon]
        """
        return pd.Series(self._df['lon'].values)

    @property
    def member(self):
        """[get member]

        Returns:
            [pd.series]: [member]
        """
        try:
            data_start_columns=self._df.attrs['data_start_columns']
        except:
            data_start_columns=6
        member = self._df.columns[data_start_columns:]
        # member = self._df.columns[self._df.attrs['data_start_columns']:]
        return pd.Series(member)

    @property
    def values(self):
        """[get values]

        Returns:
            [numpy]: [values]
        """
        return self._df.loc[:, self.member].values.squeeze()  # 此处加squeeze保证只有一列的时候返回的是个一维数组，只有一行一列的返回的是一个数值

    @property
    def quantity(self):
        """[get quantity values]

        Returns:
            [quantity numpy]: [quantity values]
        """
        return self.values * units(self._df.attrs['var_units'])

    @values.setter
    def values(self, values):
        """[set values（注意，该方法为直接赋值不会改变属性信息，如果需要改变属性属性，请调用set_values方法）
        example: sample.stda.values = 1 ]

        Args:
            values ([int or float or numpy]]): [values]
        """
        self._df.loc[:, self.member] = values

    def set_values(self, values, var_name=None, **attrs_kwargv):
        """[set values，如果给定var_name。则自动赋值stda属性]

        Args:
            values ([int or float or numpy]): [values]
            var_name ([str], optional): [stda要素名]. Defaults to None.
            **attrs_kwargs {[type]} -- [其它相关属性，如：data_source='cassandra', level_type='high']
        """
        self._df.loc[:, self.member] = values
        if var_name is not None:
            attrs = mdgstda.get_stda_attrs(var_name=var_name, **attrs_kwargv)
            attrs['data_start_columns'] = self._df.attrs['data_start_columns']
            self._df.attrs = attrs

    def get_dim_value(self, dim_name):
        """[获取维度数据，如果dim_name=='fcst_time'情况下，特殊处理，返回time*dtime]

        Args:
            dim_name ([str]): [维度名]

        Returns:
            [numpy]: [维度值]
        """
        if dim_name == 'fcst_time':
            return self.fcst_time.values
        if dim_name == 'time':
            return self.time.values
        return self._df[dim_name].values

    def get_value(self, ydim='lat', xdim='lon'):
        """[根据维度名获取stda数据，
        注： 
        1、网格stda仅支持二维，非二维stda调用该函数会报错
        2、站点stda为pd.DataFrame，无意义，故忽略xdim ydim两个参数]

        Returns:
            [numpy]: [values]
        """
        return self.values

    def description(self):
        '''
        获取描述信息，格式如下:
        起报时间: Y年m月d日H时
        预报时间: Y年m月d日H时
        预报时效: 小时
        '''
        init_time = self.time[0]
        fhour = self.dtime[0]
        fcst_time = self.fcst_time[0]

        if fhour != 0:
            description = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时'.format(
                init_time, fcst_time, fhour)
        else:
            description = '分析时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n实况/分析'.format(init_time)
        return description

    def description_point(self, describe=''):
        '''
        获取描述信息，格式如下:
        起报时间: Y年m月d日H时
        [data_name]N小时预报describe
        预报点: lon, lat

        起报时间: Y年m月d日H时
        [data_name]实况info
        分析点: lon, lat
        '''
        init_time = self.time[0]
        fhour = self.dtime[0]
        point_lon = self.lon[0]
        point_lat = self.lat[0]
        data_name = self.member[0].upper()

        if point_lon > 0:
            point_lon = str(point_lon) + 'E'
        else:
            point_lon = str(point_lon) + 'W'

        if point_lat > 0:
            point_lat = str(point_lat) + 'N'
        else:
            point_lat = str(point_lat) + 'S'

        title = ''
        if(fhour != 0):
            description = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]{2}小时预报{5}\n预报点: {3}, {4}'.format(
                init_time, data_name, fhour, point_lon, point_lat, describe)
        else:
            description = '分析时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n[{1}]实况/分析{4}\n分析点: {2}, {3}'.format(
                init_time, data_name, point_lon, point_lat, describe)
        return description

    def where(self, conditon, other=np.nan):
        '''
        根据conditon条件过滤数据自data_start_columns列开始的数据，类似于pandas.DataFrame.where
        示例: 过滤小于100且大于200的值，mydf.stda.where((mydf.stda.values > 100) & (mydf.stda.values > 200), np.nan)
        '''
        self._df.loc[:, self.member] = np.where(conditon, self.values, other)
    
    def min(self, dim=None, skipna=True, return_number=True):
        """[Return min data，站点stda多个成员的时候会返回各个成员的min]

        Args:
            dim ([str], optional): [该参数无意义，因为站点stda为pd.DataFrame，故忽略]. Defaults to None.
            skipna ([str], optional): [skip missing values (as marked by NaN)]. Defaults to True.
            return_number ([bool], optional): [是否返回数值，默认仅返回numpy数值，若想返回DataFrame请设置为False]. Defaults to True.
        """
        colname = self.member
        if len(colname) == 1 and return_number == False:
            # 只有当只有一个成员的时候，才可以返回所在行的DataFrame
            idx = self._df[colname].idxmin(skipna=skipna)
            return self._df.iloc[idx]
        return self._df[colname].min(skipna=skipna).values.squeeze() 

    def max(self, dim=None, skipna=True, return_number=True):
        """[Return max data，站点stda多个成员的时候会返回各个成员的max]

        Args:
            dim ([str], optional): [该参数无意义，因为站点stda为pd.DataFrame，故忽略]. Defaults to None.
            skipna ([str], optional): [skip missing values (as marked by NaN)]. Defaults to True.
            return_number ([bool], optional): [是否返回数值，默认仅返回numpy数值，若想返回DataFrame请设置为False]. Defaults to True.
        """
        colname = self.member
        if len(colname) == 1 and return_number == False:
            # 只有当只有一个成员的时候，才可以返回所在行的DataFrame
            idx = self._df[colname].idxmax(skipna=skipna)
            return self._df.iloc[idx]
        return self._df[colname].max(skipna=skipna).values.squeeze() 
    
    def mean(self, dim=None, skipna=True, return_number=True):
        """[Return mean data，站点stda多个成员的时候会返回各个成员的mean]

        Args:
            dim ([str], optional): [该参数无意义，因为站点stda为pd.DataFrame，故忽略]. Defaults to None.
            skipna ([str], optional): [skip missing values (as marked by NaN)]. Defaults to True.
            return_number ([bool], optional): [该参数无意义，因为站点stda为pd.DataFrame，故忽略]. Defaults to True.
        """
        colname = self.member
        return self._df[colname].mean(skipna=skipna).values.squeeze() 


if __name__ == '__main__':
    pass
