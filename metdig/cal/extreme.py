'''
天气极端性
'''
import numpy as np
import math
from datetime import datetime, timedelta
from copy import deepcopy

import xarray as xr

from metdig.cal.lib.utility import unifydim_stda, check_stda


__all__ = [
    'anomaly',
    'standard_anomaly',
    'ens_af_prob',
    'ens_af_maxmin',
]

@check_stda(['stda', 'clm_mean'])
def anomaly(stda, clm_mean, cal_member_mean=False):
    """距平，任意stda数据，沿member维度作平均后对各个level、time、dtime求距平
        stda - clm_mean

    Args:
        stda (stda): 任意stda数据(member=n, level=l, time=t, dtime=d, lat=y, lon=x)
        clm_mean (stda): 再分析平均值背景场(member=1, level=l, time=t, dtime=1, lat=y, lon=x)
        cal_member_mean (bool, optional): 是否先对stda数据进行member维度的平均. Defaults to False.

    Returns:
        stda: _description_ (member=1orn, level=l, time=t, dtime=d, lat=y, lon=x)
    """
    if clm_mean['member'].size != 1 or clm_mean['dtime'].size != 1:
        raise Exception('clm_mean must be a single-member, single-dtime stda')
    if clm_mean.stda.equal_lonlat(stda) == False:
        mean_regrid = clm_mean.interp({'lon':('lon',stda.lon.values),'lat':('lat',stda.lat.values)})
    else:
        mean_regrid = clm_mean

    # 沿member维度作平均
    if cal_member_mean == True and stda.member.size > 1:
        var = stda.mean(dim='member')
        var = var.expand_dims({'memeber': [0]})
    else:
        var = stda

    result = []

    bg_fcst_time = list(mean_regrid.stda.time)
    bg_level = list(mean_regrid.stda.level)
    
    for level in var.stda.level:
        if level not in bg_level:
            continue
        for time in var.stda.time:
            for dtime in var.stda.dtime:
                fcst_time = time + timedelta(hours=dtime)
                if fcst_time not in bg_fcst_time:
                    continue
                _member = var.sel(level=[level], time=[time], dtime=[dtime]) 
                _mean_regrid = mean_regrid.sel(level=[level], time=[fcst_time], dtime=[0]) 
                # 距平
                anom = _member.copy()
                anom.values = _member.values - _mean_regrid.values
                result.append(anom)
    if len(result) > 0:
        result = xr.combine_by_coords(result)[stda.name]
        result.attrs =  deepcopy(stda.attrs)
        result.attrs['var_name'] = '' 
        result.attrs['var_cn_name'] = ''
        result.attrs['var_units'] = ''
        return result
    return None

    
@check_stda(['stda', 'clm_mean', 'clm_sd'])
def standard_anomaly(stda, clm_mean, clm_sd, cal_member_mean=False):
    """标准化异常度，任意stda数据，沿member维度作平均后对各个level、time、dtime求标准化异常度
        (stda - clm_mean) / clm_sd

    Args:
        stda (stda): 任意stda数据(member=n, level=l, time=t, dtime=d, lat=y, lon=x)
        clm_mean (stda): 再分析平均值背景场(member=1, level=l, time=t, dtime=1, lat=y, lon=x)
        clm_sd (stda): 再分析平均值背景场(member=1, level=l, time=t, dtime=1, lat=y, lon=x)
        cal_member_mean (bool, optional): 是否先对stda数据进行member维度的平均. Defaults to False.

    Returns:
        stda: _description_ (member=1, level=l, time=t, dtime=d, lat=y, lon=x)
    """
    if clm_mean['member'].size != 1 or clm_mean['dtime'].size != 1:
        raise Exception('clm_mean must be a single-member, single-dtime stda')
    if clm_sd['member'].size != 1 or clm_sd['dtime'].size != 1:
        raise Exception('clm_sd must be a single-member, single-dtime stda')

    if clm_mean.stda.equal_lonlat(stda) == False:
        mean_regrid = clm_mean.interp({'lon':('lon',stda.lon.values),'lat':('lat',stda.lat.values)})
    else:
        mean_regrid = clm_mean
    if clm_sd.stda.equal_lonlat(stda) == False:
        sd_regrid = clm_sd.interp({'lon':('lon',stda.lon.values),'lat':('lat',stda.lat.values)})
    else:
        sd_regrid = clm_sd

    # 沿member维度作平均
    if cal_member_mean == True and stda.member.size > 1:
        var = stda.mean(dim='member')
        var = var.expand_dims({'memeber': [0]})
    else:
        var = stda

    result = []

    bg_fcst_time = list(mean_regrid.stda.time)
    bg_level = list(mean_regrid.stda.level)
    
    for level in var.stda.level:
        if level not in bg_level:
            continue
        for time in var.stda.time:
            for dtime in var.stda.dtime:
                fcst_time = time + timedelta(hours=dtime)
                if fcst_time not in bg_fcst_time:
                    continue
                _member = var.sel(level=[level], time=[time], dtime=[dtime]) 
                _mean_regrid = mean_regrid.sel(level=[level], time=[fcst_time], dtime=[0])
                _sd_regrid = sd_regrid.sel(level=[level], time=[fcst_time], dtime=[0]) 
                # 标准化距平
                stdanom = _member.copy()
                stdanom.values = (_member.values - _mean_regrid.values) / _sd_regrid.values 
                result.append(stdanom)
    if len(result) > 0:
        result = xr.combine_by_coords(result)[stda.name]
        result.attrs =  deepcopy(stda.attrs)
        result.attrs['var_name'] = '' 
        result.attrs['var_cn_name'] = ''
        result.attrs['var_units'] = ''
        return result
    return None


@check_stda(['stda', 'clm_mean', 'clm_sd'])
def ens_af_prob(stda, clm_mean, clm_sd, sigma=[-3, -2, -1, 1, 2, 3]):
    """标准化异常概率，集合预报stda数据，各个level、time、dtime求标准化异常概率，返回值中的member维度为各个sigma对应的异常概率

    Args:
        stda (stda): 任意stda数据(member=n, level=l, time=t, dtime=d, lat=y, lon=x)
        clm_mean (stda): 再分析平均值背景场(member=1, level=l, time=t, dtime=1, lat=y, lon=x)
        clm_sd (stda): 再分析平均值背景场(member=1, level=l, time=t, dtime=1, lat=y, lon=x)
        sigma (list, optional): 异常度阈值. Defaults to [-3, -2, -1, 1, 2, 3].

    Returns:
        stda: _description_(member=len(sigma), level=l, time=t, dtime=d, lat=y, lon=x)
    """
    af_member = standard_anomaly(stda, clm_mean, clm_sd, cal_member_mean=False) # (51, ?, ?, ?, ?, ?)
    if af_member is None:
        return None
    result = []
    for sig in sigma:
        if sig > 0:
            af_prob = (af_member >= sig).mean(dim='member').expand_dims({'member': [sig]})
        else:
            af_prob = (af_member <= sig).mean(dim='member').expand_dims({'member': [sig]})
        result.append(af_prob)
    result = xr.combine_by_coords(result)[stda.name]  # (6, ?, ?, ?, ?, ?)
    result *= 100  # 转换为百分比
    result.attrs =  deepcopy(stda.attrs)
    result.attrs['var_name'] = '' 
    result.attrs['var_cn_name'] = ''
    result.attrs['var_units'] = 'percent'
    return result


@check_stda(['stda', 'clm_mean', 'clm_sd'])
def ens_af_maxmin(stda, clm_mean, clm_sd):
    """标准化异常最大最小值，集合预报stda数据，各个level、time、dtime求标准化异常最大最小值，返回值中的member维度为最大最小

    Args:
        stda (stda): 任意stda数据(member=n, level=l, time=t, dtime=d, lat=y, lon=x)
        clm_mean (stda): 再分析平均值背景场(member=1, level=l, time=t, dtime=1, lat=y, lon=x)
        clm_sd (stda): 再分析平均值背景场(member=1, level=l, time=t, dtime=1, lat=y, lon=x)

    Returns:
        stda: _description_(member=2, level=l, time=t, dtime=d, lat=y, lon=x)
    """
    af_member = standard_anomaly(stda, clm_mean, clm_sd, cal_member_mean=False) # (51, ?, ?, ?, ?, ?)
    if af_member is None:
        return None
    af_max = af_member.max(dim='member').expand_dims({'member': ['max']})
    af_min = af_member.min(dim='member').expand_dims({'member': ['min']})
    result = xr.combine_by_coords([af_max, af_min])[stda.name]  # (6, ?, ?, ?, ?, ?)
    result.attrs =  deepcopy(stda.attrs)
    result.attrs['var_name'] = '' 
    result.attrs['var_cn_name'] = ''
    result.attrs['var_units'] = ''
    return result
