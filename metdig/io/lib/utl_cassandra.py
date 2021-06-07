# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np

from metpy.units import units


def check_units(var_units):
    try:
        units(var_units)
    except Exception as e:
        raise e

__model_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cassandra_model_cfg.csv'
__model_cfg = pd.read_csv(__model_cfg_csv, encoding='gbk', comment='#')
__model_cfg = __model_cfg.fillna('')
__model_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式

__obs_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cassandra_obs_cfg.csv'
__obs_cfg = pd.read_csv(__obs_cfg_csv, encoding='gbk', comment='#')
__obs_cfg = __obs_cfg.fillna('')
__obs_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式

_sate_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cassandra_sate_cfg.csv'
_sate_cfg = pd.read_csv(_sate_cfg_csv, encoding='gbk', comment='#')
_sate_cfg = _sate_cfg.fillna('')
_sate_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式
_sate_cfg['channel'] = _sate_cfg.apply(lambda row: row['channel'].strip('/').split('/'), axis=1)

__radar_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cassandra_radar_cfg.csv'
__radar_cfg = pd.read_csv(__radar_cfg_csv, encoding='gbk', comment='#')
__radar_cfg = __radar_cfg.fillna('')
__radar_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式

def get_model_cfg(level_type=None, data_name=None, var_name=None):
    this_cfg = __model_cfg[(__model_cfg['data_name'] == data_name) &
                           (__model_cfg['var_name'] == var_name) &
                           (__model_cfg['level_type'] == level_type)].copy(deep=True).reset_index(drop=True)

    # 此处建议修改为warning
    if len(this_cfg) == 0:
        raise Exception('can not get data_name={} level_type={} var_name={} in {}!'.format(data_name, level_type, var_name, __model_cfg_csv))

    return this_cfg.to_dict('index')[0]

def get_sate_cfg(data_name=None, var_name=None, channel=None):
    this_cfg = _sate_cfg[(_sate_cfg['data_name'] == data_name) &
                          (_sate_cfg['var_name'] == var_name)].copy(deep=True).reset_index(drop=True)

    # channel 是list
    index = -1
    for idx, row in this_cfg.iterrows():
        if 'any' in row['channel'] or str(channel) in row['channel']:
            index = idx
            break

    if index < 0:
        raise Exception('can not get data_name={} var_name={} channel={} in {}!'.format(data_name, var_name, channel, _sate_cfg_csv))

    return this_cfg.to_dict('index')[index]

def get_radar_cfg(data_name=None, var_name=None):
    this_cfg = __radar_cfg[(__radar_cfg['data_name'] == data_name) &
                           (__radar_cfg['var_name'] == var_name)].copy(deep=True).reset_index(drop=True)

    if len(this_cfg) == 0:
        raise Exception('can not get data_name={} var_name={} in {}!'.format(data_name, var_name, __radar_cfg_csv))

    return this_cfg.to_dict('index')[0]

def model_cassandra_dir(level_type=None, data_name=None, var_name=None, level=None):
    path = get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['cassandra_path']

    if level is None:
        return path

    if level_type == 'high':
        return path + str(level) + '/'
    elif level_type == 'surface':
        return path

    return ''


def model_cassandra_units(level_type=None, data_name=None, var_name=None):
    return get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['var_units']


def model_cassandra_level(level_type=None, data_name=None, var_name=None, level=None):
    models_level = get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['cassandra_level']

    if models_level == 'any':
        return level
    else:
        return int(models_level)

def sate_cassandra_dir(data_name=None, var_name=None, channel=None):
    return get_sate_cfg(data_name=data_name, var_name=var_name, channel=channel)['cassandra_path']


def sate_cassandra_units(data_name=None, var_name=None, channel=None):
    return get_sate_cfg(data_name=data_name, var_name=var_name, channel=channel)['var_units']

def radar_cassandra_dir(data_name=None, var_name=None):
    return get_radar_cfg(data_name=data_name, var_name=var_name)['cassandra_path']

def radar_cassandra_units(data_name=None, var_name=None):
    return get_radar_cfg(data_name=data_name, var_name=var_name)['var_units']


def obs_cassandra_dir(data_name=None, var_name=None):
    _obs_cfg = __obs_cfg[(__obs_cfg['data_name'] == data_name) &
                         (__obs_cfg['var_name'] == var_name)].copy(deep=True)

    if len(_obs_cfg) == 0:
        raise Exception('can not get data_name = {} var_name={} in {}!'.format(data_name, var_name, __obs_cfg_csv))
    
    return _obs_cfg['cassandra_path'].values[0]


def obs_cassandra_units(data_name=None, var_name=None):
    _obs_cfg = __obs_cfg[(__obs_cfg['data_name'] == data_name) &
                         (__obs_cfg['var_name'] == var_name)].copy(deep=True)
    if len(_obs_cfg) == 0:
        return ''
    return _obs_cfg['var_units'].values[0]

'''
def obs_var_name(level_type=None, data_name=None):
    _obs_cfg = __obs_cfg[(__obs_cfg['data_name'] == data_name) &
                         (__obs_cfg['level_type'] == level_type)].copy(deep=True)
    if len(_obs_cfg) == 0:
        return ''
    return _obs_cfg['var_name'].values[0]
'''

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
        'Gust_angle': 'wdir',
        'Gust_speed': 'wsp',
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


if __name__ == '__main__':
    print(model_cassandra_level(level_type='high', data_name='ecmwf', var_name='u', level=1))
    print(model_cassandra_level(level_type='high', data_name='ecmwf', var_name='u', level=10))
    print(model_cassandra_level(level_type='high', data_name='ecmwf', var_name='u', level=100))
    print(model_cassandra_level(level_type='high', data_name='ecmwf', var_name='u', level=None))

    print(model_cassandra_level(level_type='surface', data_name='ecmwf', var_name='t2m', level=1))
    print(model_cassandra_level(level_type='surface', data_name='ecmwf', var_name='t2m', level=10))
    print(model_cassandra_level(level_type='surface', data_name='ecmwf', var_name='t2m', level=100))
    print(model_cassandra_level(level_type='surface', data_name='ecmwf', var_name='t2m', level=None))