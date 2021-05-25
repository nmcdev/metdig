# -*- coding: utf-8 -*

import metdig.io.cassandra as cassandra_io
import metdig.io.era5 as era5_io
import metdig.io.cmadaas as cmadaas_io
import metdig.io.thredds as thredds_io
import metdig.io.MDIException as MDIException

from metdig.io.lib import config


def config_init(CMADaaS_DNS=None, CMADaaS_PORT=None, CMADaaS_USER_ID=None, CMADaaS_PASSWORD=None, CMADaaS_serviceNodeId=None,
                   MICAPS_GDS_IP=None, MICAPS_GDS_PORT=None,
                   THREDDS_IP=None, THREDDS_PORT=None,
                   CACHE_DIR=None,
                   ):
    '''
    io数据接口参数初始化方法，不存在则创建，配置仅赋值传参的参数，未传参的配置保持不变
    '''
    config.init_nmcdev_cfg(
        CMADaaS_DNS=CMADaaS_DNS, CMADaaS_PORT=CMADaaS_PORT, CMADaaS_USER_ID=CMADaaS_USER_ID, CMADaaS_PASSWORD=CMADaaS_PASSWORD,
        CMADaaS_serviceNodeId=CMADaaS_serviceNodeId, MICAPS_GDS_IP=MICAPS_GDS_IP, MICAPS_GDS_PORT=MICAPS_GDS_PORT, CACHE_DIR=CACHE_DIR)
    config.init_metdig_cfg(THREDDS_IP=THREDDS_IP, THREDDS_PORT=THREDDS_PORT, CACHE_DIR=CACHE_DIR)
    pass


def get_model_grid(data_source,  throwexp=True, **kwargs):
    '''

    [读取单层单时次模式网格数据]

    Arguments:
        data_source {[str]} -- [可选择填写如下数据源: cassandra, cmadaas, era5, thredds)]
        **kwargs {[type]} -- [调用读取函数的kwargs]
        throwexp {bool} -- [是否抛出异常，（注意谨慎设置为False，不会抛出任何异常，无法定位为何出错）] (default: {True})

    Returns:
        [stda] -- [description]
    '''
    try:
        if data_source == 'cassandra':
            return cassandra_io.get_model_grid(**kwargs)
        elif data_source == 'cds':
            # era5 不存在fhour和data_name参数
            kwargs.pop('fhour')
            kwargs.pop('data_name')
            return era5_io.get_model_grid(**kwargs)
        elif data_source == 'cmadaas':
            return cmadaas_io.get_model_grid(**kwargs)
        elif data_source == 'thredds':
            return thredds_io.get_model_grid(**kwargs)
        else:
            raise Exception('data_source={} error!'.format(data_source))
    except Exception as e:
        if throwexp == True:
            raise e
        else:
            print(str(e))
            return None
    return None


def get_model_grids(data_source, throwexp=True, **kwargs):
    '''

    [读取单层多时次模式网格数据]

    Arguments:
        data_source {[str]} -- [可选择填写如下数据源: cassandra, cmadaas, era5, thredds)]
        **kwargs {[type]} -- [调用读取函数的kwargs]
        throwexp {bool} -- [是否抛出异常，（注意谨慎设置为False，不会抛出任何异常，无法定位为何出错）] (default: {True})

    Returns:
        [stda] -- [description]
    '''
    try:
        if data_source == 'cassandra':
            return cassandra_io.get_model_grids(**kwargs)
        elif data_source == 'cds':
            # era5 不存在fhour和data_name参数，era5的init_times等效于其它的init_time+fhour
            if 'init_time' in kwargs:
                kwargs['init_times'] = kwargs['init_time']
            kwargs.pop('fhours')
            kwargs.pop('data_name')
            return era5_io.get_model_grids(**kwargs)
        elif data_source == 'cmadaas':
            return cmadaas_io.get_model_grids(**kwargs)
        elif data_source == 'thredds':
            return thredds_io.get_model_grids(**kwargs)
        else:
            raise Exception('data_source={} error!'.format(data_source))
    except Exception as e:
        if throwexp == True:
            raise e
        else:
            print(str(e))
            return None
    return None


def get_model_3D_grid(data_source, throwexp=True, **kwargs):
    '''

    [读取多层单时次模式网格数据]

    Arguments:
        data_source {[str]} -- [可选择填写如下数据源: cassandra, cmadaas, era5, thredds)]
        **kwargs {[type]} -- [调用读取函数的kwargs]
        throwexp {bool} -- [是否抛出异常，（注意谨慎设置为False，不会抛出任何异常，无法定位为何出错）] (default: {True})

    Returns:
        [stda] -- [description]
    '''
    try:
        if data_source == 'cassandra':
            return cassandra_io.get_model_3D_grid(**kwargs)
        elif data_source == 'cds':
            # era5 不存在fhour和data_name参数
            kwargs.pop('fhour')
            kwargs.pop('data_name')
            return era5_io.get_model_3D_grid(**kwargs)
        elif data_source == 'cmadaas':
            return cmadaas_io.get_model_3D_grid(**kwargs)
        elif data_source == 'thredds':
            return thredds_io.get_model_3D_grid(**kwargs)
        else:
            raise Exception('data_source={} error!'.format(data_source))
    except Exception as e:
        if throwexp == True:
            raise e
        else:
            print(str(e))
            return None
    return None


def get_model_3D_grids(data_source, throwexp=True, **kwargs):
    '''

    [读取多层多时次模式网格数据]

    Arguments:
        data_source {[str]} -- [可选择填写如下数据源: cassandra, cmadaas, era5, thredds)]
        **kwargs {[type]} -- [调用读取函数的kwargs]
        throwexp {bool} -- [是否抛出异常，（注意谨慎设置为False，不会抛出任何异常，无法定位为何出错）] (default: {True})

    Returns:
        [stda] -- [description]
    '''
    try:
        if data_source == 'cassandra':
            return cassandra_io.get_model_3D_grids(**kwargs)
        elif data_source == 'cds':
            # era5 不存在fhour和data_name参数，era5的init_times等效于其它的init_time+fhour
            if 'init_time' in kwargs:
                kwargs['init_times'] = kwargs['init_time']
            kwargs.pop('fhours')
            kwargs.pop('data_name')
            return era5_io.get_model_3D_grids(**kwargs)
        elif data_source == 'cmadaas':
            return cmadaas_io.get_model_3D_grids(**kwargs)
        elif data_source == 'thredds':
            if 'init_time' in kwargs:
                kwargs['init_times'] = kwargs['init_time']
            return thredds_io.get_model_3D_grids(**kwargs)
        else:
            raise Exception('data_source={} error!'.format(data_source))
    except Exception as e:
        if throwexp == True:
            raise e
        else:
            print(str(e))
            return None
    return None


def get_model_points(data_source, throwexp=True, **kwargs):
    '''

    [获取单层/多层，单时效/多时效观测站点数据]

    Arguments:
        data_source {[str]} -- [可选择填写如下数据源: cassandra, cmadaas, era5, thredds)]
        **kwargs {[type]} -- [调用读取函数的kwargs]
        throwexp {bool} -- [是否抛出异常，（注意谨慎设置为False，不会抛出任何异常，无法定位为何出错）] (default: {True})

    Returns:
        [stda] -- [description]
    '''
    try:
        if data_source == 'cassandra':
            return cassandra_io.get_model_points(**kwargs)
        elif data_source == 'cmadaas':
            return cmadaas_io.get_model_points(**kwargs)
        elif data_source == 'cds':
            # era5 不存在fhour和data_name参数
            kwargs.pop('fhours')
            kwargs.pop('data_name')
            return era5_io.get_model_points(**kwargs)
        elif data_source == 'thredds':
            kwargs.pop('fhours')
            return thredds_io.get_model_points(**kwargs)
        else:
            raise Exception('data_source={} error!'.format(data_source))
    except Exception as e:
        if throwexp == True:
            raise e
        else:
            print(str(e))
            return None
    return None


def get_obs_stations(data_source, throwexp=True, **kwargs):
    '''

    [获取单时次站点数据]

    Arguments:
        data_source {[str]} -- [可选择填写如下数据源: cassandra, cmadaas)]
        **kwargs {[type]} -- [调用读取函数的kwargs]
        throwexp {bool} -- [是否抛出异常，（注意谨慎设置为False，不会抛出任何异常，无法定位为何出错）] (default: {True})

    Returns:
        [stda] -- [description]
    '''
    try:
        if data_source == 'cassandra':
            return cassandra_io.get_obs_stations(**kwargs)
        elif data_source == 'cmadaas':
            kwargs.pop('level')
            kwargs.pop('is_save_other_info')
            return cmadaas_io.get_obs_stations(**kwargs)
        else:
            raise Exception('data_source={} error!'.format(data_source))
    except Exception as e:
        if throwexp == True:
            raise e
        else:
            print(str(e))
            return None
    return None


def get_obs_stations_multitime(data_source, throwexp=True, **kwargs):
    '''

    [获取多时次站点数据]

    Arguments:
        data_source {[str]} -- [可选择填写如下数据源: cassandra, cmadaas)]
        **kwargs {[type]} -- [调用读取函数的kwargs]
        throwexp {bool} -- [是否抛出异常，（注意谨慎设置为False，不会抛出任何异常，无法定位为何出错）] (default: {True})

    Returns:
        [stda] -- [description]
    '''
    try:
        if data_source == 'cassandra':
            return cassandra_io.get_obs_stations_multitime(**kwargs)
        elif data_source == 'cmadaas':
            kwargs.pop('level')
            kwargs.pop('is_save_other_info')
            return cmadaas_io.get_obs_stations_multitime(**kwargs)
        else:
            raise Exception('data_source={} error!'.format(data_source))
    except Exception as e:
        if throwexp == True:
            raise e
        else:
            print(str(e))
            return None
    return None
