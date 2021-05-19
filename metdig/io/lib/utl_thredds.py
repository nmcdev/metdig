# _*_ coding: utf-8 _*_

import os
import pandas as pd
from metpy.units import units

def __check_units(var_units):
    try:
        units(var_units)
    except Exception as e:
        raise e

__model_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/thredds_model_cfg.csv'
__model_cfg = pd.read_csv(__model_cfg_csv, encoding='gbk', comment='#')
__model_cfg = __model_cfg.fillna('')
__model_cfg.apply(lambda row: __check_units(row['var_units']), axis=1)  # 检查是否满足units格式

def get_model_cfg(level_type=None, data_name=None, var_name=None):
    this_cfg = __model_cfg[(__model_cfg['data_name'] == data_name) &
                           (__model_cfg['var_name'] == var_name) &
                           (__model_cfg['level_type'] == level_type)].copy(deep=True).reset_index(drop=True)

    if len(this_cfg) == 0:
        raise Exception('can not get data_name={} level_type={} var_name={} in {}!'.format(data_name, level_type, var_name, __model_cfg_csv))

    return this_cfg.to_dict('index')[0]


def model_thredds_path(level_type=None, data_name=None, var_name=None, level=None):
    path = get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['thredds_path']

    if level is None:
        return path

    if level_type == 'high':
        return path + str(level) + '/'
    elif level_type == 'surface':
        return path

    return ''


def model_thredds_units(level_type=None, data_name=None, var_name=None):
    return get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['var_units']

def model_thredds_variable(level_type=None, data_name=None, var_name=None):
    return get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['thredds_var_name']

def model_thredds_level(level_type=None, data_name=None, var_name=None, level=None):
    models_level = get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['thredds_level']

    if models_level == 'any':
        return level
    else:
        return int(models_level)


if __name__ == '__main__':
    # x = thredds_variable(level_type='surface', var_name='u10m',)
    # print(x)
    # x = thredds_units(level_type='surface', var_name='u10m',)
    # print(x)

    x = thredds_level(level_type='high', var_name='u', level=None)
    print(x)

    x = thredds_level(level_type='high', var_name='u', level=100)
    print(x)

    x = thredds_level(level_type='high', var_name='u', level=2)
    print(x)

