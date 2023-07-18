# -*- coding: utf-8 -*-

import xarray as xr
import pandas as pd
import numpy as np

import functools
from inspect import Parameter, signature

from metpy.units import units 

import metdig.utl as mdgstda

import logging
_log = logging.getLogger(__name__)

def stda_to_quantity(data):
    '''

    []

    Arguments:
        data {[stda]} -- [stda data]

    Returns:
        [quantity] -- [description]
    '''
    return data.stda.quantity


def stda_to_numpy(data):
    '''

    []

    Arguments:
        data {[stda]} -- [stda data]

    Returns:
        [ndarray] -- [description]
    '''
    return data.stda.values


def quantity_to_stda_byreference(var_name, data, reference_variables,
                      **attrs_kwargs):
    '''

    [根据reference_variables(stda格式)，将data(Quantity)转换成功stda格式，其中坐标信息均来自于reference_variables。
    注意，此处data需要外部转换好单位再进入此函数，此函数不涉及单位转换，
    改进，为保留reference_variables中非可选的坐标信息，比如lon_cross,lat_cross]

    Arguments:
        data {[quantity]} -- [需要转换的数据]
        reference_variables {[stda]} -- [参考stda数据，经纬度等维度信息均参考此变量]

    Raises:
        Exception -- [description]
    '''
    if isinstance(reference_variables, xr.DataArray):
        stda_data=reference_variables.copy(deep=True)
        stda_data.name = var_name
        stda_attrs = mdgstda.get_stda_attrs(var_name=var_name, **attrs_kwargs)
        data, data_units = mdgstda.numpy_units_to_stda(data.magnitude, str(data.units), stda_attrs['var_units'])
        stda_data.values=data
        stda_data.attrs=stda_attrs

        # stda_data = mdgstda.numpy_to_gridstda(
        #     np.array(data),
        #     reference_variables['member'].values, reference_variables['level'].values, reference_variables['time'].values,
        #     reference_variables['dtime'].values, reference_variables['lat'].values, reference_variables['lon'].values,
        #     var_name=var_name, np_input_units=str(data.units),
        # )
        return stda_data

    elif isinstance(reference_variables, pd.DataFrame):
        stda_data = mdgstda.stastda_copy(reference_variables, iscopy_otherdim=True, iscopy_value=False)
        stda_data.attrs = mdgstda.get_stda_attrs(var_name=var_name)
        stda_data.attrs['data_start_columns'] = reference_variables.attrs['data_start_columns']
        member = reference_variables.stda.member #针对集合预报的情况的修改
        if (len(member)==1):
            stda_data[member[0]] = data.magnitude #np.array(data)[:]
        else:
            for idxm,im in enumerate(member):
                stda_data[im] = np.array(data)[...,idxm].squeeze()
        return stda_data

    else:
        raise Exception('stda_to_Quantity Failed! type(reference_variables) must be pd.DataFrame or xr.DataArray!')


def check_stda(check_lst):
    """检查是否是相同类型的stda

    Parameters
    ----------
    check_lst : list
        被检查的要素名称列表
    """
    def decorator(func):
        sig = signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            for arg_name in check_lst:
                try:
                    tag = bound_args.arguments[arg_name].stda.is_stda()
                except Exception as e:
                    tag = False
                if tag == False:
                    raise Exception(f'{func.__name__} Argument {arg_name} is not stda!')
            return func(*args, **kwargs)
        return wrapper
    return decorator


def unifydim_stda(unify_lst, exclude=frozenset()):
    """将多个stda的维度统一取交集

    Parameters
    ----------
    check_lst : list
        被检查的要素名称列表

    exclude : bool
        不参与求维度交集的维度
    """
    def decorator(func):
        sig = signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _unify_lst = unify_lst

            if len(_unify_lst) == 0:
                return func(*args, **kwargs)

            bound_args = sig.bind(*args, **kwargs)
            
            # 第一个参数的类型只能是DataArray或DataFrame
            type_like = None

            # 去掉不用检查的参数
            for i in range(len(_unify_lst)-1, -1, -1):
                if _unify_lst[i] not in bound_args.arguments.keys():
                    _unify_lst.pop(i)
                else:
                    try:
                        if type_like is None:
                            type_like = bound_args.arguments[_unify_lst[i]].stda.type # 获取第一个有效参数的类型
                        else:
                            if type_like != bound_args.arguments[_unify_lst[i]].stda.type: # 第二个开始和第一个比较，类型不同去掉
                                _unify_lst.pop(i)
                    except Exception as e:
                        _unify_lst.pop(i)
            
            if len(_unify_lst) <= 1:
                return func(*args, **kwargs)

            # 检查维度是否一致（如果和第一个不一样，则所有要素取交集）
            if type_like == 'DataArray':
                for arg_name in _unify_lst[1:]:
                    if bound_args.arguments[_unify_lst[0]].stda.equal_dim(bound_args.arguments[arg_name]) == False:
                        _log.warning(f"{func.__name__} Argument {_unify_lst} dims may not be equal! The program will automatically use xarray.align(*objects, join='inner') to get intersections!")
                        # 取交集
                        lst_stda = [bound_args.arguments[arg_name] for arg_name in _unify_lst]
                        lst_name = [arg_name for arg_name in _unify_lst]
                        lst_stda = xr.align(*lst_stda, join='inner', exclude=exclude) 
                        for i in range(len(lst_stda)):
                            bound_args.arguments[lst_name[i]] = lst_stda[i]
                        # print(bound_args)
                        break
            elif type_like == 'DataFrame':
                # 待更新
                pass
            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper
    return decorator
