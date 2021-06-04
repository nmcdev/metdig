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


__model_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cmadaas_model_cfg.csv'
__model_cfg = pd.read_csv(__model_cfg_csv, encoding='gbk', comment='#')
__model_cfg = __model_cfg.fillna('')
__model_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式
__model_cfg['cmadaas_data_code'] = __model_cfg.apply(lambda row: row['cmadaas_data_code'].strip('/').split('/'), axis=1)

__obs_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cmadaas_obs_cfg.csv'
__obs_cfg = pd.read_csv(__obs_cfg_csv, encoding='gbk', comment='#')
__obs_cfg = __obs_cfg.fillna('')
__obs_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式

__datacode_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cmadaas_datacode_cfg.csv'
__datacode_cfg = pd.read_csv(__datacode_cfg_csv, encoding='gbk', comment='#')
__datacode_cfg = __datacode_cfg.fillna('')

def get_datacode_cfg(data_name=None, fhour=0):

    if fhour == 0:
        fhour_flag = 0
    else:
        fhour_flag = 1
    this_cfg = __datacode_cfg[(__datacode_cfg['data_name'] == data_name) &
                              (__datacode_cfg['fhour_flag'] == fhour_flag)].copy(deep=True).reset_index(drop=True)

    if len(this_cfg) == 0:
        raise Exception('can not get data_name={} fhour_flag={} in {}!'.format(data_name, fhour_flag, __datacode_cfg_csv))

    if len(this_cfg) > 1:
        raise Exception('error: greater than 1 recode! data_name={} fhour_flag={} in {}!'.format(data_name, fhour_flag, __datacode_cfg_csv))

    return this_cfg['data_code'].values[0]


def get_model_cfg(data_name=None, var_name=None, level_type=None, data_code=None):
    this_cfg = __model_cfg[(__model_cfg['data_name'] == data_name) &
                           (__model_cfg['var_name'] == var_name) &
                           (__model_cfg['level_type'] == level_type)].copy(deep=True).reset_index(drop=True)

    if len(this_cfg) == 0:
        raise Exception('can not get data_name={} level_type={} var_name={}  in {}!'.format(data_name, level_type, var_name, __model_cfg_csv))

    if len(this_cfg) > 1:
        raise Exception('error: greater than 1 recode! data_name={} level_type={} var_name={} in {}!'.format(data_name, level_type, var_name, __model_cfg_csv))

    cmadaas_data_code = this_cfg['cmadaas_data_code'].values[0]

    if data_code.strip().lower() != 'any':
        if data_code not in cmadaas_data_code:
            raise Exception('error: {} not in cmadaas_data_code! data_name={} level_type={} var_name={} in {}!'.format(data_code, data_name, level_type, var_name, __model_cfg_csv))
    
    return this_cfg.to_dict('index')[0]

def model_cmadaas_data_code(data_name=None, var_name=None, level_type=None, fhour=0):
    cmadaas_data_code = get_datacode_cfg(data_name=data_name, fhour=fhour)
    if cmadaas_data_code.strip().lower() != 'any':
        return cmadaas_data_code
    return get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=cmadaas_data_code)['cmadaas_data_code'][0]

def model_cmadaas_var_name(data_name=None, var_name=None, level_type=None, data_code=None):
    return get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=data_code)['cmadaas_var_name']


def model_cmadaas_level_type(data_name=None, var_name=None, level_type=None, data_code=None):
    return get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=data_code)['cmadaas_level_type']


def model_cmadaas_units(data_name=None, var_name=None, level_type=None, data_code=None):
    return get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=data_code)['var_units']


def model_cmadaas_level(data_name=None, var_name=None, level_type=None, data_code=None, level=None):
    models_level = get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=data_code)['cmadaas_level']

    if models_level == 'any':
        return level
    else:
        return int(models_level)

def get_obs_cfg(data_name=None, var_name=None):
    this_cfg = __obs_cfg[(__obs_cfg['data_name'] == data_name) &
                         (__obs_cfg['var_name'] == var_name)].copy(deep=True).reset_index(drop=True)

    if len(this_cfg) == 0:
        raise Exception('can not get data_name={} var_name={} in {}!'.format(data_name, var_name, __obs_cfg_csv))

    return this_cfg.to_dict('index')[0]

def obs_cmadaas_data_code(data_name=None, var_name=None):
    return get_obs_cfg(data_name=data_name, var_name=var_name)['cmadaas_data_code']

def obs_cmadaas_units(data_name=None, var_name=None):
    return get_obs_cfg(data_name=data_name, var_name=var_name)['var_units']

def obs_cmadaas_var_name(data_name=None, var_name=None):
    return get_obs_cfg(data_name=data_name, var_name=var_name)['cmadaas_var_name']

'''
def obs_var_name(data_name=None):
    return get_obs_cfg(data_name=data_name)['var_name']
'''

if __name__ == '__main__':
    data_code = model_cmadaas_data_code(data_name='ecmwf', var_name='tmp', level_type='high', fhour=0)
    print(data_code)

    cmadaas_var_name = model_cmadaas_var_name(data_name='ecmwf', var_name='tmp', level_type='high', data_code=data_code)
    print(cmadaas_var_name)

    # level = model_cmadaas_level(data_name='grapes_gfs', var_name='tmp', level_type='high', data_code=data_code, level=2)
    # print(level)

    # x = obs_cmadaas_var_name(data_name='national', var_name='rain24')
    # print(x)
