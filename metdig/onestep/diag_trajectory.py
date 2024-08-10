# -*- coding: utf-8 -*-

import pandas as pd

from metdig.io import get_model_3D_grids

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.onestep.complexgrid_var.vvel import read_vvel3ds
from metdig.onestep.complexgrid_var.theta import read_theta4d

from metdig.products import diag_trajectory as draw_trajectory

import metdig.cal as mdgcal
import metdig.utl.utl_stda_grid as utl_stda_grid

__all__ = [
    'trajectory',
]



@date_init('init_time', method=date_init.special_series_set)
def trajectory(data_source='cassandra', data_name='ecmwf', 
               init_time=None, 
               fhours=range(0, 73, 3), 
               levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 200], # 取数据的层次
               var_diag='vvel', # 诊断物理量，如spfh、rh等
               points={'lon': [95, 95.1], 'lat': [30, 30.1], 'level':[925,900], 'id':[1,2]}, # 追踪点
               t_s=None, # 追踪起始时间 如果为空则代表全数据时段
               t_e=None, # 追踪终止时间 如果为空则代表全数据时段
               dt=1800, # 追踪时间步长 单位为s
               area='全国', # 取数据的区域，绘图时会自动把区域缩小到质点追踪的范围
               is_mask_terrain=True,
               is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    extent = get_map_area(area)

    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='u', levels=levels,extent=extent)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='v', levels=levels,extent=extent)
    vvel = read_vvel3ds(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels,extent=extent)
    if var_diag is None or var_diag == '':
        var_diag = 'vvel'
    if var_diag == 'vvel':
        diag = vvel.copy()
    elif var_diag == 'theta':
        diag = read_theta4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    else:
        diag = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name=var_diag, levels=levels,extent=extent)
    
    trajectories = mdgcal.trajectory_on_pressure_level(u, v, vvel, var_diag=diag, 
                                                       s_point=points,
                                                       t_s=t_s,
                                                       t_e=t_e,
                                                       dt=dt)
    # trajectories = pd.read_csv('d:/trajectories.csv') # 测试
        
    if is_return_data:
        dataret = {'u': u, 'v': v, 'vvel': vvel, var_diag: diag, 'trajectories': trajectories}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_trajectory.draw_trajectory(u, v, trajectories, var_diag=var_diag, dt=dt, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret