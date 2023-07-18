# -*- coding: utf-8 -*-

'''

'''


import numpy as np
import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units as mpunits
import metpy.interpolate as mpinterp
from metpy.plots.mapping import CFProjection

from metdig.cal.lib import utility as utl
import metdig.utl as mdgstda
from metdig.cal.lib.utility import unifydim_stda, check_stda


__all__ = [
    'cross_section',
    'cross_section_components'
]


@check_stda(['data'])
def cross_section(data, start, end, steps=101, interp_type='linear'):
    '''

    [Obtain an interpolated cross-sectional slice through gridded data.]

    Arguments:
        data {[stda]} -- [符合stda数据格式的等经纬度数据]
        start {[array_like]} -- [A latitude-longitude pair designating the start point of the cross section 
            (units are degrees north and degrees east).]
        end {[array_like]} -- [A latitude-longitude pair designating the end point of the cross section 
            (units are degrees north and degrees east).]

    Keyword Arguments:
        steps {number} -- [The number of points along the geodesic 
            between the start and the end point (including the end points) 
            to use in the cross section. Defaults to 100.] (default: {100})
        interp_type {str} -- [The interpolation method, either ‘linear’ or ‘nearest’
            (see xarray.DataArray.interp() for details). Defaults to ‘linear’.] (default: {'linear'})
    '''

    # data.coords['crs'] = CFProjection({'grid_mapping_name': 'latitude_longitude'})
    data = data.metpy.assign_crs(grid_mapping_name='latitude_longitude')  # metpy 1.0

    if len(start) < 2 or len(start) % 2:
        raise Exception('Start point must be a pair of lat/lon coordinates')

    npts = len(start) // 2 # 线段数
    steps *= npts # 如果线段多，则插值点数自动变多

    distance = []
    for i in range(npts): # 循环每一段线
        _stp = start[i * 2:i * 2 + 2] # 开始点[lat, lon]
        _edp = end[i * 2:i * 2 + 2] # 结束点[lat, lon]
        distance.append((_stp[0] - _edp[0])**2 + (_stp[1] - _edp[1])**2) # 计算每一段线的距离
    distance = np.array(distance)
    distance = distance / distance.sum() # 距离归一化到0-1
    # print(distance)

    cross_data_lst = []
    for i in range(npts): # 循环每一段线
        _stp = start[i * 2:i * 2 + 2] # 开始点[lat, lon]
        _edp = end[i * 2:i * 2 + 2] # 结束点[lat, lon]

        _step = int(distance[i] * steps) # 每一段线的插值点数按总线段的比例分配
        # print(_stp, _edp, _step)
        if _step < 3: # 插值点数最少为3
            _step = 3
        cross_data = mpinterp.cross_section(data, _stp, _edp, steps=_step, interp_type=interp_type)
        
        if i >= 1:
            _last_edp = end[(i-1) * 2:(i-1) * 2 + 2] # 上一段的结束点
            if _last_edp[0] == _stp[0] and _last_edp[1] == _stp[1]: # 如果上一段线的结束点和这一段线的开始点重合
                cross_data = cross_data.isel(index=slice(1, None)) # 去掉重复的第一个点
                # print('去掉重复的第一个点')
            
            _last_index_ed = cross_data_lst[-1]['index'].values[-1] # 上一段线的最后一个index
            cross_data['index'] = np.arange(_last_index_ed + 1, _last_index_ed + cross_data['index'].size + 1)  # index设置为连续递增数列

        cross_data.name = 'data'
        # print(cross_data.dims, cross_data.shape, type(cross_data))
        # print(cross_data.coords)
        # print()
        cross_data_lst.append(cross_data)

    cross_data_lst = xr.combine_by_coords(cross_data_lst)['data'] # [member, level, time, dtime, index]
    cross_stda = mdgstda.numpy_to_gridstda(cross_data_lst.values[:, :, :, :, np.newaxis, :], # 增加一维lat，然后将index转换成lon
                                            cross_data_lst['member'].values,
                                            cross_data_lst['level'].values,
                                            cross_data_lst['time'].values,
                                            cross_data_lst['dtime'].values,
                                            [9999],
                                            cross_data_lst['lon'].values)
    cross_stda.coords['crs'] = CFProjection({'grid_mapping_name': 'latitude_longitude'})
    cross_stda = cross_stda.assign_coords({"lon_cross": ("lon", cross_data_lst['lon'].values)})
    cross_stda = cross_stda.assign_coords({"lat_cross": ("lon", cross_data_lst['lat'].values)})
    cross_stda = cross_stda.assign_coords({"index": ("lon", cross_data_lst['index'].values)})
    cross_stda.attrs = data.attrs
    # print(cross_stda.dims, cross_stda.shape)
    # print(cross_stda)
    # exit()
    return cross_stda


@check_stda(['cross_x', 'cross_y'])
@unifydim_stda(['cross_x', 'cross_y'])
def cross_section_components(cross_x, cross_y):
    '''

    [Obtain the tangential and normal components of a cross-section of a vector field]

    Arguments:
        cross_x {[stda]} -- [The input DataArray of the x-component (in terms of data projection) of the vector field]
        cross_y {[stda]} -- [The input DataArray of the y-component (in terms of data projection) of the vector field]

    Keyword Arguments:
        index {str} -- [description] (default: {'index'})
    '''

    # 需要给attrs赋值units属性
    data_x = cross_x.copy(deep=True)
    data_y = cross_y.copy(deep=True)
    # data_x.attrs['units'] = utl.stdaunits_to_metpyunits(data_x.attrs['var_units'])
    # data_y.attrs['units'] = utl.stdaunits_to_metpyunits(data_y.attrs['var_units'])
    data_x.attrs['units'] = data_x.attrs['var_units']
    data_y.attrs['units'] = data_y.attrs['var_units']

    # 增加常量维度index
    data_x = data_x.assign_coords({"index": ("lon", np.arange(0, data_x['lon'].values.size))})
    data_y = data_y.assign_coords({"index": ("lon", np.arange(0, data_y['lon'].values.size))})

    # stda中lon lat为真实维度，index为常量维度
    # metpy.cross_section_components参数需要的真实维度必须是index，lon lat为常量维度
    data_x = data_x.swap_dims({'lon': 'index'})
    data_x = data_x.rename({'lon': 'unknow_lon', 'lat': 'unknow_lat'})
    data_x = data_x.rename({'lon_cross': 'lon', 'lat_cross': 'lat'})

    data_y = data_y.swap_dims({'lon': 'index'})
    data_y = data_y.rename({'lon': 'unknow_lon', 'lat': 'unknow_lat'})
    data_y = data_y.rename({'lon_cross': 'lon', 'lat_cross': 'lat'})

    data_x = data_x.metpy.assign_crs(grid_mapping_name='latitude_longitude')  # metpy 1.0
    data_y = data_y.metpy.assign_crs(grid_mapping_name='latitude_longitude')  # metpy 1.0
    cross_t, cross_n = mpcalc.cross_section_components(data_x, data_y, index='index')

    # 计算结束后转换为stda维度
    cross_t = cross_t.rename({'lon': 'lon_cross', 'lat': 'lat_cross'})
    cross_t = cross_t.rename({'unknow_lon': 'lon', 'unknow_lat': 'lat'})
    cross_t = cross_t.swap_dims({'index': 'lon'})
    cross_t.attrs = cross_x.attrs
    cross_t.attrs['var_name'] = 't_components'
    cross_t.attrs['var_cn_name'] = '切向分量'

    cross_n = cross_n.rename({'lon': 'lon_cross', 'lat': 'lat_cross'})
    cross_n = cross_n.rename({'unknow_lon': 'lon', 'unknow_lat': 'lat'})
    cross_n = cross_n.swap_dims({'index': 'lon'})
    cross_n.attrs = cross_y.attrs
    cross_n.attrs['var_name'] = 'n_components'
    cross_n.attrs['var_cn_name'] = '法向分量'

    return cross_t, cross_n
