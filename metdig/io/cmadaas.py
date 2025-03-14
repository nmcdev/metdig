# -*- coding: utf-8 -*-

import sys

import datetime
import xarray as xr
import numpy as np
import pandas as pd

import nmc_met_io.retrieve_cmadaas as nmc_cmadaas_io
import metdig.io.nmc_cmadass_helper as nmc_cmadass_helper

from metdig.io.lib import cmadaas_model_cfg, cmadaas_obs_cfg
from metdig.io.lib import utility as utl


import metdig.utl as mdgstda

import logging
_log = logging.getLogger(__name__)


def get_model_grid(init_time=None, fhour=None, data_name=None, var_name=None, level=None,
                   extent=None, x_percent=0, y_percent=0,cache_clear=True,dim_round=4,**kwargs):
    '''

    [读取单层单时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhour {[int32]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [数据要素名]
        level {[int32]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})
        dim_round {number} 坐标保留几位小数
    Returns:
        [stda] -- [stda格式数据]
    '''
    try:
        if level:
            level_type = 'high'
        else:
            level_type = 'surface'
        cmadaas_data_code = cmadaas_model_cfg().model_cmadaas_data_code(data_name=data_name, var_name=var_name, level_type=level_type, fhour=fhour)
        cmadaas_var_name = cmadaas_model_cfg().model_cmadaas_var_name(
            data_name=data_name, var_name=var_name, level_type=level_type, data_code=cmadaas_data_code)
        cmadaas_level_type = cmadaas_model_cfg().model_cmadaas_level_type(
            data_name=data_name, var_name=var_name, level_type=level_type, data_code=cmadaas_data_code)
        cmadaas_level = cmadaas_model_cfg().model_cmadaas_level(level_type=level_type, var_name=var_name,
                                                        data_name=data_name, data_code=cmadaas_data_code, level=level)
        cmadaas_units = cmadaas_model_cfg().model_cmadaas_units(level_type=level_type, var_name=var_name, data_name=data_name, data_code=cmadaas_data_code)
        cmadaas_prod_type = cmadaas_model_cfg().model_cmadaas_prod_type(
            data_name=data_name, var_name=var_name, level_type=level_type, data_code=cmadaas_data_code)
        _log.debug('cmadaas_data_code={}, cmadaas_level_type={}, cmadaas_level={}, cmadaas_var_name={}, fhour={}'.format(cmadaas_data_code, cmadaas_level_type, cmadaas_level, cmadaas_var_name, fhour))
    except Exception as e:
        raise Exception(str(e))

    timestr = '{:%Y%m%d%H}'.format(init_time-datetime.timedelta(hours=8))  # 数据都是世界时，需要转换为北京时
    if(extent is not None):
        limit=utl.extent2limit(extent,x_percent=x_percent,y_percent=y_percent)
    else:
        limit=None

    # 特殊处理
    if ((cmadaas_data_code == 'NAFP_CRA_FTM_6HOR') & (extent==None)):
        kwargs['eleValueRanges'] = 'PROD_PARA3:0P25'

    if cmadaas_prod_type == 'analysis':
        #针对大数据云平台中的实况格点数据，入cldas
        data = nmc_cmadaas_io.cmadaas_analysis_by_time(data_code=cmadaas_data_code,
                                             time=timestr+'0000', level_type=cmadaas_level_type,#limit=limit, #暂时去除limit参数，因为nmc_met_io的缓存数据不能判断空间范围，导致重复读取数据
                                             fcst_level=cmadaas_level, fcst_ele=cmadaas_var_name,cache_clear=cache_clear,**kwargs) # ['time', 'level', 'lat', 'lon'] 注意（nmc_micaps_io返回的维度不统一）
    elif cmadaas_prod_type == 'model':
        data = nmc_cmadass_helper.cmadaas_model_grid(data_code=cmadaas_data_code,
                                                init_time=timestr, valid_time=fhour, level_type=cmadaas_level_type,limit=limit, #暂时去除limit参数，因为nmc_met_io的缓存数据不能判断空间范围，导致重复读取数据
                                                fcst_level=cmadaas_level, fcst_ele=cmadaas_var_name,cache_clear=cache_clear,**kwargs) # ['time', 'level', 'lat', 'lon'] 注意（nmc_micaps_io返回的维度不统一）
    elif cmadaas_prod_type.startswith('ens'):
        #针对大数据云平台中的集合成员数据
        ms = cmadaas_prod_type.split('_')[-1].split('-')[0]
        me = cmadaas_prod_type.split('_')[-1].split('-')[1]
        data = []
        for i in range(int(ms), int(me) + 1, 1):
            tmp = nmc_cmadass_helper.cmadaas_ens_model_grid(data_code=cmadaas_data_code,
                                                init_time=timestr, valid_time=fhour, level_type=cmadaas_level_type,#limit=limit, #暂时去除limit参数，因为nmc_met_io的缓存数据不能判断空间范围，导致重复读取数据
                                                fcst_level=cmadaas_level, fcst_ele=cmadaas_var_name, fcst_member=i,cache_clear=cache_clear,**kwargs) # ['time', 'level', 'lat', 'lon'] 注意（nmc_micaps_io返回的维度不统一）
            
            if tmp is not None:
                data.append(tmp)
        data = xr.concat(data, dim='number')
    else:
        raise Exception('cmadaas_prod_type error!')

    # 建议这里修改为warning
    if data is None:
        raise Exception('Can not get data from cmadaas! cmadaas_data_code={}, cmadaas_level_type={}, cmadaas_level={}, cmadaas_var_name={}, init_time={}, fhour={}'.format(
            cmadaas_data_code, cmadaas_level_type, cmadaas_level, cmadaas_var_name, timestr, fhour))
    
    #读取集合预报
    if('number' in list(data.coords.keys())):
        member = data.coords['number'].values
        member = list(map(lambda x: data_name + '-' + str(x), member))
    else:
        member = [data_name]

    data['lon']=data.lon.round(dim_round)
    data['lat']=data.lat.round(dim_round)
    # 数据裁剪
    data = utl.area_cut(data, extent, x_percent, y_percent)

    # 经纬度从小到大排序好
    data = data.sortby('lat')
    data = data.sortby('lon')
    # time_BJT= [itime.values+np.timedelta64(8,'h') for itime in data.time]
    # data.coords['time']=time_BJT

    # 待测试。。。
    stda_data = mdgstda.xrda_to_gridstda(data[list(data.keys())[0]],
                                         member_dim='number', level_dim='level', time_dim='time', lat_dim='lat', lon_dim='lon',
                                         member=member, level=[cmadaas_level], time=[init_time], dtime=[fhour],
                                         var_name=var_name, np_input_units=cmadaas_units,
                                         data_source='cmadaas', level_type=level_type)
    return stda_data

    '''
    stda_data = None
    if level:
        levels = [level]
    else:
        levels = [cmadaas_level]
    
    # 转成stda
    # stda_data=mdgstda.xrda_to_gridstda(data[list(data.keys())[0]],member=data_name,var_name=var_name)
    # return stda_data
    # if 'data' in data.keys():
    try:
        np_data = np.squeeze(data[list(data.keys())[0]].values)
        np_data = np_data[np.newaxis, np.newaxis, np.newaxis, np.newaxis, ...]
        stda_data = mdgstda.numpy_to_gridstda(
            np_data, [data_name],
            levels, [init_time],
            [fhour],
            data.coords['lat'].values, data.coords['lon'].values, var_name=var_name, np_input_units=cmadaas_units, data_source='cmadaas',
            level_type=level_type)

        return stda_data
    except:
        raise Exception('data is not in nmc_met_io return data_set')
    '''


def get_model_grids(init_time=None, fhours=None, data_name=None, var_name=None, level=None,
                    extent=None, x_percent=0, y_percent=0,**kwargs):
    '''

    [读取单层多时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhours {[list or number]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [要素名]
        level {[int32]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    fhours = utl.parm_tolist(fhours)
    init_time = utl.parm_tolist(init_time)

    stda_data = []

    for iinit in init_time:
        for fhour in fhours:
            try:
                data = get_model_grid(iinit, fhour, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent,**kwargs)
                if data is not None and data.size > 0:
                    stda_data.append(data)
            except Exception as e:
                _log.info(str(e))

    if stda_data:
        if(len(init_time)>1):
            return xr.concat(stda_data, dim='time')
        else:
            return xr.concat(stda_data, dim='dtime')

    return None

def get_model_3D_grid(init_time=None, fhour=None, data_name=None, var_name=None, levels=None,
                      extent=None, x_percent=0, y_percent=0):
    '''

    [读取多层单时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhour {[int32]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [要素名]
        levels {[list or number]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    levels = utl.parm_tolist(levels)

    stda_data = []
    for level in levels:
        try:
            data = get_model_grid(init_time, fhour, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and data.size > 0:
                stda_data.append(data)
        except Exception as e:
            _log.info(str(e))
    if stda_data:
        return xr.concat(stda_data, dim='level')
    else:
        return None


def get_model_3D_grids(init_time=None, fhours=None, data_name=None, var_name=None, levels=None,
                       extent=None, x_percent=0, y_percent=0):
    '''

    [读取多层多时次模式网格数据]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhours {[list or number]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [要素名]
        levels {[list or number]} -- [层次，不传代表地面层] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    fhours = utl.parm_tolist(fhours)
    levels = utl.parm_tolist(levels)
    init_time = utl.parm_tolist(init_time)

    stda_data = []

    for iinit in init_time:
        for fhour in fhours:
            temp_data = []
            for level in levels:
                try:
                    data = get_model_grid(iinit, fhour, data_name, var_name, level, extent=extent, x_percent=x_percent, y_percent=y_percent)
                    if data is not None and data.size > 0:
                        temp_data.append(data)
                except Exception as e:
                    _log.info(str(e))
            if temp_data:
                temp_data = xr.concat(temp_data, dim='level')
                stda_data.append(temp_data)
    if stda_data:
        if(len(init_time)>1):
            return xr.concat(stda_data, dim='time')
        else:
            return xr.concat(stda_data, dim='dtime')
    return None

# if __name__=='__main__':
#     import pandas as pd
#     init_times=pd.date_range('2022-07-01-02','2022-07-07-20',freq='6h').to_pydatetime()
#     test=get_model_3D_grids(data_name='cma_ra',init_time=init_times,fhours=0,var_name='u',levels=[500,850])
#     print(test)

def get_model_points(init_time=None, fhours=None, data_name=None, var_name=None, levels=None, points={}):
    '''

    [读取单层/多层，单时效/多时效 模式网格数据，插值到站点上]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间]
        fhours {[list]} -- [预报时效]
        data_name {[str]} -- [模式名]
        var_name {[str]} -- [要素名]
        levels {[list]} -- [层次，不传代表地面层] (default: {None})
        points {[dict]} -- [站点信息，字典中必须包含经纬度{'lon':[], 'lat':[]}]

    Returns:
        [stda] -- [stda格式数据]
    '''
    fhours = utl.parm_tolist(fhours)
    levels = utl.parm_tolist(levels)

    # get grids data
    stda_data = get_model_3D_grids(init_time, fhours, data_name, var_name, levels)

    if stda_data is not None and stda_data.size > 0:
        return mdgstda.gridstda_to_stastda(stda_data, points)
    return None


def get_obs_stations(obs_time=None, data_name=None, var_name=None, id_selected=None,
                     extent=None, x_percent=0, y_percent=0):
    '''

    [获取单层单时次观测站点数据]

    Keyword Arguments:
        obs_time {[datetime]} -- [观测时间]
        data_name {[str]} -- [观测类型]
        var_name {[str]} -- [要素名]
        id_selected {[list or item]} -- [站号，站号列表或单站] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    # 从配置中获取相关信息
    try:
        cmadaas_data_code = cmadaas_obs_cfg().obs_cmadaas_data_code(data_name=data_name, var_name=var_name)
        cmadass_units = cmadaas_obs_cfg().obs_cmadaas_units(data_name=data_name, var_name=var_name)  # cmadass数据单位
        cmadaas_var_name = cmadaas_obs_cfg().obs_cmadaas_var_name(data_name=data_name, var_name=var_name)
        stda_attrs = mdgstda.get_stda_attrs(data_source='cmadaas', data_name=data_name, var_name=var_name)  # stda属性获取
        _log.debug('cmadaas_data_code={}, cmadaas_var_name={} '.format(cmadaas_data_code, cmadaas_var_name))
    except Exception as e:
        raise Exception(str(e))

    # 读取数据
    timestr = '{:%Y%m%d%H%M%S}'.format(obs_time - datetime.timedelta(hours=8))  # cmadaas数据都是世界时，需要转换为北京时
    data = nmc_cmadaas_io.cmadaas_obs_by_time(timestr, data_code=cmadaas_data_code,
                                              elements="Station_Id_C,Station_Id_d,lat,lon,Datetime," + cmadaas_var_name)
    data['Datetime']=obs_time # cmadaas数据都是世界时，需要转换为北京时

    if data is None:
        raise Exception('Can not get data from cmadaas! cmadaas_data_code={}, cmadaas_var_name={}, obs_time={}'.format(
            cmadaas_data_code, cmadaas_var_name, timestr))

    data = data.set_index('Station_Id_C')  # 设置ID列为索引列
    # print(data.index.dtype)
    # print(data)

    # 经纬度范围裁剪
    data = utl.area_cut(data, extent, x_percent, y_percent)

    # 站点选择
    data = utl.sta_select_id(data, id_selected)

    # 层次初始化，这边先假定全是地面层次，初始化为0
    levels = np.full((len(data)), 0)

    # 转成stda
    if isinstance(data_name, list) is True:
        data_name = str(data_name)
    return mdgstda.numpy_to_stastda(
        data[cmadaas_var_name].values, [data_name], levels, data['Datetime'].values, 0, data.iloc[:,0].values,  data['lat'].values, data['lon'].values,
        np_input_units=cmadass_units, var_name=var_name, other_input={},
        data_source='cmadaas', data_name=data_name
    )
if __name__=='__main__':
    import datetime
    obs_time=datetime.datetime(2022,11,5,8)
    # map_extent=[113.5,119.5,38,42]
    rain=get_obs_stations(obs_time=obs_time,data_name='sfc_chn_hor',var_name='tmp')
    print(rain)

def get_obs_stations_multitime(obs_times=None, data_name=None, var_name=None, id_selected=None,
                               extent=None, x_percent=0, y_percent=0, ):
    '''

    [获取单层多时次观测站点数据]

    Keyword Arguments:
        obs_times {[list]} -- [观测时间列表]
        data_name {[str]} -- [观测类型]
        var_name {[str]} -- [要素名]
        id_selected {[list or item]} -- [站号，站号列表或单站] (default: {None})
        extent {[tuple]} -- [裁剪区域，如(50, 150, 0, 65)] (default: {None})
        x_percent {number} -- [根据裁剪区域经度方向扩充百分比] (default: {0})
        y_percent {number} -- [根据裁剪区域纬度方向扩充百分比] (default: {0})

    Returns:
        [stda] -- [stda格式数据]
    '''
    obs_times = utl.parm_tolist(obs_times)

    datas = []
    attrs = {}
    for obs_time in obs_times:
        try:
            data = get_obs_stations(obs_time, data_name, var_name=var_name,
                                    id_selected=id_selected, extent=extent, x_percent=x_percent, y_percent=y_percent)
            if data is not None and len(data) > 0:
                attrs = data.attrs
                datas.append(data)
        except Exception as e:
            _log.info(str(e))

    if datas:
        df = pd.concat(datas, ignore_index=True)
        df.attrs = attrs
        return df

    return None

