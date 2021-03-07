# -*- coding: utf-8 -*-

'''

'''


import numpy as np

import metpy.calc as mpcalc
from metpy.units import units as mpunits
import metpy.interpolate as mpinterp
from metpy.plots.mapping import CFProjection

from .lib import utility  as utl
import metdig.metdig_utl as mdgstda


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
    data=data.metpy.assign_crs(grid_mapping_name='latitude_longitude') #metpy 1.0

    cross_data = mpinterp.cross_section(data, start, end, steps=steps, interp_type=interp_type)  

    # to_stda
    np_cross = cross_data.values # [member, level, time, dtime, index]
    np_cross = np_cross[:, :, :, :, np.newaxis, :] # 增加一维lat，然后将index转换成lon
    cross_stda = mdgstda.numpy_to_gridstda(np_cross,
                                                 cross_data['member'].values,
                                                 cross_data['level'].values,
                                                 cross_data['time'].values,
                                                 cross_data['dtime'].values,
                                                 [9999],
                                                 cross_data['lon'].values)
    cross_stda.attrs = cross_data.attrs

    cross_stda.coords['crs'] = CFProjection({'grid_mapping_name': 'latitude_longitude'})
    cross_stda = cross_stda.assign_coords({"lon_cross": ("lon", cross_data['lon'].values)})
    cross_stda = cross_stda.assign_coords({"lat_cross": ("lon", cross_data['lat'].values)})

    return cross_stda


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

    cross_u_t, cross_v_n = mpcalc.cross_section_components(data_x, data_y, index='index')

    # 计算结束后转换为stda维度
    cross_u_t = cross_u_t.rename({'lon': 'lon_cross', 'lat': 'lat_cross'})
    cross_u_t = cross_u_t.rename({'unknow_lon': 'lon', 'unknow_lat': 'lat'})
    cross_u_t = cross_u_t.swap_dims({'index': 'lon'})
    cross_u_t.attrs = cross_x.attrs

    cross_v_n = cross_v_n.rename({'lon': 'lon_cross', 'lat': 'lat_cross'})
    cross_v_n = cross_v_n.rename({'unknow_lon': 'lon', 'unknow_lat': 'lat'})
    cross_v_n = cross_v_n.swap_dims({'index': 'lon'})
    cross_v_n.attrs = cross_y.attrs

    return cross_u_t, cross_v_n
