# -*- coding: utf-8 -*-


from datetime import datetime, timedelta

import os
import time
import xarray as xr
import numpy as np
import pandas as pd

import inspect

import logging
_log = logging.getLogger(__name__)


def extent2limit(extent, x_percent=0, y_percent=0):
    '''
    依照extent获取limit
    '''

    delt_x = (extent[1] - extent[0]) * x_percent
    delt_y = (extent[3] - extent[2]) * y_percent
    limit=[extent[2] - delt_y,extent[0] - delt_x, extent[3] + delt_y, extent[1] + delt_x]
    return limit

def parm_tolist(parm):
    try:
        return list(parm)
    except:
        return [parm]


def model_filename(initTime, fhour, UTC=False):
    """
        Construct model file name.

    Arguments:
        initTime {string or datetime object} -- model initial time,
            like 18042008' or datetime(2018, 4, 20, 8).
        fhour {int or str} -- model forecast hours.
    """
    if isinstance(fhour,str):
        fhour_str='.'+fhour
    else:
        fhour_str=".{:03d}".format(fhour)
    if(UTC is False):
        if isinstance(initTime, datetime):
            return initTime.strftime('%y%m%d%H') + fhour_str
        else:
            return initTime.strip() + fhour_str
    else:
        if isinstance(initTime, datetime):
            return (initTime - timedelta(hours=8)).strftime('%y%m%d%H') + fhour_str
        else:
            time_rel = (datetime.strptime('20' + initTime, '%Y%m%d%H') - timedelta(hours=8)).strftime('%y%m%d%H')
            return time_rel.strip() + fhour_str


def obs_filename(obsTime, UTC=False):
    if(UTC is False):
        if isinstance(obsTime, datetime):
            return obsTime.strftime('%Y%m%d%H%M%S') + ".000"
        else:
            return obsTime.strip() + ".000"
    else:
        if isinstance(obsTime, datetime):
            return (obsTime - timedelta(hours=8)).strftime('%Y%m%d%H%M%S') + ".000"
        else:
            time_rel = (datetime.strptime(obsTime, '%Y%m%d%H%M%S') - timedelta(hours=8)).strftime('%Y%m%d%H%M%S')
            return time_rel.strip() + ".000"


def reset_id_back(sta):
    '''
    输入的sta的站号中可能有些站号包含a-z,A-Z的字母，对此将这些字母转换为对应的ASCII数字，再将整个字符串格式的站号转换为数值形式
    返回sta站号为整型
                                                                '''
    # print(sta)
    values = sta['id'].values
    if type(values[0]) != str:
        values = values.astype(str)
        int_id = np.zeros(len(values)).astype(str)
        for i in range(len(values)):
            strs = values[i]
            if len(strs) > 5:
                int_id[i] = chr(int(strs[0:2])) + strs[2:]
        sta['id'] = int_id
    if isinstance(values[0], float):
        int_id = values.astype(np.int32)
        sta["id"] = int_id


def area_cut(data, extent, x_percent=0, y_percent=0):
    '''
    区域裁剪 
    '''
    if extent is None:
        return data

    delt_x = (extent[1] - extent[0]) * x_percent
    delt_y = (extent[3] - extent[2]) * y_percent
    cut_extent = (extent[0] - delt_x, extent[1] + delt_x, extent[2] - delt_y, extent[3] + delt_y)

    if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
        return data.where((data['lon'] >= cut_extent[0]) &
                          (data['lon'] <= cut_extent[1]) &
                          (data['lat'] >= cut_extent[2]) &
                          (data['lat'] <= cut_extent[3]), drop=True)

    elif isinstance(data, pd.DataFrame):
        return data[(data['lon'] > cut_extent[0]) &
                    (data['lon'] < cut_extent[1]) &
                    (data['lat'] > cut_extent[2]) &
                    (data['lat'] < cut_extent[3])]


def sta_select_id(df, id_selected):
    '''
    从df.index中筛选id_selected
    '''
    if len(df) == 0:
        return df
    if id_selected is None:
        return df

    if not isinstance(id_selected, list) and not isinstance(id_selected, np.ndarray):
        id_selected = [id_selected]

    id_selected = np.array(id_selected).astype(df.index.dtype)

    try:
        data = df.loc[id_selected]
    except Exception as e:
        _log.debug('id_selected failed: id={} is not in data!'.format(id_selected))
        return None
        data = df.drop(index=df.index)
    return data


def cfgpath_format_todatestr(cfgpath, **kwargs):
    """[xxx_cfg.csv配置文件中的路径格式化成只有日期的字符串，函数返回值可以用strftime格式化成datetime]

    Args:
        cfgpath ([str]): [配置文件中的路径]
        time ([datetime]): [日期]

    Returns:
        [str]: [可以直接使用的有效路径字符串]
    """
    return cfgpath.format(Y='%Y',
                          y='%y',
                          m='%m',
                          d='%d',
                          H='%H',
                          M='%M',
                          S='%S',
                          **kwargs,
                          )


def obs_rename_colname(data):
    # nmc_met_io.retrieve_micaps_server.get_station_data的返回值的要素名，和STDA的要素名的对应关系
    name_dict = {
        'Wind_angle': 'wdir',
        'Wind_speed': 'wsp',
        'Wind_angle_1m_avg': 'wdir',
        'Wind_speed_1m_avg': 'wsp',
        'Wind_angle_2m_avg': 'wdir',
        'Wind_speed_2m_avg': 'wsp',
        'Wind_angle_10m_avg': 'wdir',
        'Wind_speed_10m_avg': 'wsp',
        'Wind_angle_max': 'wdir',
        'Wind_speed_max': 'wsp',
        'Wind_angle_instant': 'wdir',
        'Wind_speed_instant': 'wsp',
        'Gust_angle': 'gustdir10m',
        'Gust_speed': 'gust10m',
        'Gust_angle_6h': 'wdir',
        'Gust_speed_6h': 'wsp',
        'Gust_angle_12h': 'wdir',
        'Gust_speed_12h': 'wsp',
        'Wind_power': '',
        'Sea_level_pressure': '',
        'Pressure_3h_trend': '',
        'Pressure_24h_trend': '',
        'Station_pressure': '',
        'Pressure_max': 'pres',
        'Pressure_min': 'pres',
        'Pressure': 'pres',
        'Pressure_day_avg': 'pres',
        'SLP_day_avg': '',
        'Hihgt': '',
        'Geopotential_hihgt': 'hgt',
        'Temp': 'tmp',
        'Temp_max': 'tmx',
        'Temp_min': 'tmn',
        'Temp_24h_trend': 'tmp',
        'Temp_24h_max': 'tmx24_2m',
        'Temp_24h_min': 'tmn24_2m',
        'Temp_dav_avg': 'tmp',
        'Dewpoint': 'td',
        'Dewpoint_depression': '',
        'Relative_humidity': 'rh',
        'Relative_humidity_min': 'rh',
        'Relative_humidity_day_avg': 'rh',
        'Water_vapor_pressure': '',
        'Water_vapor_pressure_day_avg': '',
        'Rain': 'rain',
        'Rain_1h': 'rain01',
        'Rain_3h': 'rain03',
        'Rain_6h': 'rain06',
        'Rain_12h': 'rain12',
        'Rain_day': 'rain24',
        'Rain_20-08': 'rain24',
        'Rain_08-20': 'rain24',
        'Rain_20-20': 'rain24',
        'Rain_08-08': 'rain24',
        'Evaporation': '',
        'Evaporation_large': '',
        'Precipitable_water': '',
        'Vis_1min': '',
        'Vis_10min': '',
        'Vis_min': '',
        'Vis_manual': '',
        'Total_cloud_cover': '',
        'Low_cloud_cover': '',
        'Cloud_base_hihgt': '',
        'Low_cloud': '',
        'Middle_cloud': '',
        'High_cloud': '',
        'TCC_day_avg': '',
        'LCC_day_avg': '',
        'Cloud_cover': '',
        'Cloud_type': '',
        'Weather_current': '',
        'Weather_past_1': '',
        'Weather_past_2': '',
        'Surface_temp': '',
        'Surface_temp_max': '',
        'Surface_temp_min': '',
        'Geopotential_hight': 'hgt',
        'Dewpoint_depression': 't_td',
    }

    return data.rename(columns=name_dict)
