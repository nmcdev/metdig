
import numpy as np
import math

import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units

from metdig.cal.lib import utility as utl
import metdig.utl as mdgstda
from metdig.cal.lib.utility import unifydim_stda, check_stda

__all__ = [
    # 'gradient',
    'geospatial_gradient',
    'integrate',
]



def gradient(stda, axes1, axes2, delta1, delta2):

    loop_axes = ['member', 'level', 'time', 'dtime', 'lat', 'lon']
    if axes1 in loop_axes:
        loop_axes.remove(axes1)
    else:
        raise Exception(f'{axes1} not in stda.dims')
    if axes2 in loop_axes:
        loop_axes.remove(axes2)
    else:
        raise Exception(f'{axes2} not in stda.dims')
    
    if stda[axes1].size < 3:
        raise Exception(f'{axes1} dimension size must be greater than 3')
    if stda[axes2].size < 3:
        raise Exception(f'{axes2} dimension size must be greater than 3')

    for d in loop_axes:
        if stda[d].size != 1:
            raise Exception(f'{d} dimension size must be equal to 1')
        
    stda = stda.squeeze()
    print(stda)

    # lon_coord = ('lon', stda['lon'].values, {
    #             'long_name': 'longitude', 'units': 'degrees_east',
    #             '_CoordinateAxisType': 'Lon', "axis": "X"})
    # lat_coord = ('lat', stda['lat'].values, {
    #     'long_name': 'latitude', 'units': 'degrees_north',
    #     '_CoordinateAxisType': 'Lat', 'axis': "Y"})
    # lon_2d, lat_2d = np.meshgrid(stda.lon, stda.lat)
    # x = lon_2d
    # y = lat_2d

    # if axes is None:
    #     axes=[0, 1] # 未指定就都

    # print(stda)
    # grad_y = stda.copy(deep=True)
    # grad_y.values[:] = np.nan
    # grad_x = stda.copy(deep=True)
    # grad_x.values[:] = np.nan

    # for ilevel in stda.level.values:
    #     for imember in stda.member.values:
    #         for idtime in stda.dtime.values:
    #             for itime in stda.time.values:
    #                 _d=stda.sel(level=[ilevel],member=[imember],dtime=[idtime],time=[itime]).squeeze()
    #                 print(f'----{ilevel} {imember} {idtime} {itime}---')
    #                 # grad = mpcalc.gradient(_d.values, axes=[0], coordinates=(y, x)) # axes: 0->y, 1->x （对y轴的差分结果）
    #                 # grad = mpcalc.gradient(_d.values, axes=[1], coordinates=(y, x)) # axes: 0->y, 1->x （对x轴的差分结果）
    #                 grad = mpcalc.gradient(_d.values, coordinates=(y, x)) # axes=None时返回的元组（对y轴的差分结果，对x轴的差分结果）
    #                 # grad = mpcalc.gradient(_d.values, deltas=(1, 1)) # deltas表示数据间隔距离，可以 分辨率值/矩阵[维度-1]
                    
    #                 grad_y.loc[{'level': ilevel,'member':imember,'dtime':idtime,'time':itime}] = np.array(grad[0])
    #                 # print(grad_y.loc[{'level': ilevel,'member':imember,'dtime':idtime,'time':itime}])
    #                 grad_x.loc[{'level': ilevel,'member':imember,'dtime':idtime,'time':itime}] = np.array(grad[1])
    #                 # print(grad_x.loc[{'level': ilevel,'member':imember,'dtime':idtime,'time':itime}])
                    
                    
    # print(grad_y)
    # print(grad_x)
    pass


def geospatial_gradient(stda, dx=None, dy=None):
    """地理空间差分（地理空间梯度），使用xarray的geospatial_gradient方法

    Args:
        stda (stda): 任意stda数据
        dx (np.array, optional): 指定`stda中网格经度方向点之间间距的数组或标量序列(必须带units为长度单位)`，默认按经纬度坐标计算球面间距。 Defaults to None.
        dy (np.array, optional): 指定`stda中网格纬度方向点之间间距的数组或标量序列(必须带units为长度单位)`，默认按经纬度坐标计算球面间距。. Defaults to None.

    Returns:
        tuple: (df/dx, df/dy) (对纬度轴的差分结果，对经度轴的差分结果)
    """

    if (dx is None) or (dy is None):
        _dx, _dy = mpcalc.lat_lon_grid_deltas(stda['lon'].values, stda['lat'].values)
        if dx is None:
            dx = _dx
        if dy is None:
            dy = _dy

    dfdx = stda.copy(deep=True)
    dfdx.values[:] = np.nan
    dfdx.attrs['var_name'] = 'df/dx'
    dfdx.attrs['var_cn_name'] = ''
    dfdy = stda.copy(deep=True)
    dfdy.values[:] = np.nan
    dfdy.attrs['var_name'] = 'df/dy'
    dfdy.attrs['var_cn_name'] = ''

    for ilevel in stda.level.values:
        for imember in stda.member.values:
            for idtime in stda.dtime.values:
                for itime in stda.time.values:
                    _d = stda.sel(level=ilevel,member=imember,dtime=idtime,time=itime)

                    _dvalues = utl.stda_to_quantity(_d) 

                    # print(f'----{ilevel} {imember} {idtime} {itime}---')
                    # ('df/dx', 'df/dy') metpy返回的单位固定为
                    _dfdx, _dfdy = mpcalc.geospatial_gradient(_dvalues, dx=dx, dy=dy) # axes=None时返回的元组（对y轴的差分结果，对x轴的差分结果）
                    

                    dfdx.loc[{'level': ilevel,'member':imember,'dtime':idtime,'time':itime}] = _dfdx.magnitude
                    # print(dfdx.loc[{'level': ilevel,'member':imember,'dtime':idtime,'time':itime}])
                    dfdy.loc[{'level': ilevel,'member':imember,'dtime':idtime,'time':itime}] = _dfdy.magnitude
                    # print(dfdy.loc[{'level': ilevel,'member':imember,'dtime':idtime,'time':itime}])

                    dfdx.attrs['var_units'] = str(_dfdx.units)
                    dfdy.attrs['var_units'] = str(_dfdy.units)
                        
    return (dfdx, dfdy)



def integrate(stda, axes):
    """积分 给定维度上的积分计算，使用xarray的integrate方法，基于梯形法则
    Integrate along the given coordinate using the trapezoidal rule.

    Args:
        stda (stda): 任意stda数据
        axes (str): stda 维度名称 e.g. 'member', 'level', 'time', 'dtime', 'lat', 'lon'
    """
    ret = stda.integrate(axes)
    ret = ret.expand_dims({axes: [0]})
    ret = ret.transpose(*stda.dims)
    return ret