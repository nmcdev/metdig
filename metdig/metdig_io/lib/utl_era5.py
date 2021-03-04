# _*_ coding: utf-8 _*_

import os
import pandas as pd
from metpy.units import units

def __check_units(var_units):
    try:
        units(var_units)
    except Exception as e:
        raise e

__model_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/era5_cfg.csv'
__model_cfg = pd.read_csv(__model_cfg_csv, encoding='gbk', comment='#')
__model_cfg = __model_cfg.fillna('')
__model_cfg.apply(lambda row: __check_units(row['var_units']), axis=1)  # 检查是否满足units格式

def get_model_cfg(var_name=None, level_type=None):
    this_cfg = __model_cfg[(__model_cfg['var_name'] == var_name) &
                         (__model_cfg['level_type'] == level_type)].copy(deep=True).reset_index(drop=True)

    if len(this_cfg) == 0:
        raise Exception('can not get level_type = {} var_name = {} in {}!'.format(level_type, var_name, __model_cfg_csv))

    return this_cfg.to_dict('index')[0]


def era5_variable(var_name=None, level_type=None):
    '''
    stda数据集名称和era5数据集名称对应关系表
    '''
    return get_model_cfg(var_name=var_name, level_type=level_type)['era5_var_name']

def era5_units(var_name=None, level_type=None):
    return get_model_cfg(var_name=var_name, level_type=level_type)['var_units']

def era5_level(var_name=None, level_type=None, level=None):
    models_level = get_model_cfg(var_name=var_name, level_type=level_type)['era5_level']

    if models_level == 'any':
        return level
    else:
        return int(models_level)


if __name__ == '__main__':
    # x = era5_variable(level_type='surface', var_name='u10m',)
    # print(x)
    # x = era5_units(level_type='surface', var_name='u10m',)
    # print(x)

    x = era5_level(level_type='high', var_name='u', level=None)
    print(x)

    x = era5_level(level_type='high', var_name='u', level=100)
    print(x)

    x = era5_level(level_type='high', var_name='u', level=2)
    print(x)

    x = era5_level(level_type='surface', var_name='u10m', level=None)
    print(x)

    x = era5_level(level_type='surface', var_name='u10m', level=10)
    print(x)

    x = era5_level(level_type='surface', var_name='u10m', level=2)
    print(x)
