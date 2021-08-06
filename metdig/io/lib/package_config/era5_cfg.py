# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np

from metdig.io.lib.package_config.base import check_units, SingletonMetaClass


class era5_cfg(metaclass=SingletonMetaClass):
    def __init__(self):
        self.model_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/era5_cfg.csv'
        self.model_cfg = pd.read_csv(self.model_cfg_csv, encoding='gbk', comment='#')
        self.model_cfg = self.model_cfg.fillna('')
        self.model_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式

    def get_model_cfg(self, var_name=None, level_type=None):
        this_cfg = self.model_cfg[(self.model_cfg['var_name'] == var_name) &
                                  (self.model_cfg['level_type'] == level_type)].copy(deep=True).reset_index(drop=True)

        if len(this_cfg) == 0:
            raise Exception('can not get level_type = {} var_name = {} in {}!'.format(level_type, var_name, self.model_cfg_csv))

        return this_cfg.to_dict('index')[0]

    def era5_variable(self, var_name=None, level_type=None):
        '''
        stda数据集名称和era5数据集名称对应关系表
        '''
        return self.get_model_cfg(var_name=var_name, level_type=level_type)['era5_var_name']

    def era5_units(self, var_name=None, level_type=None):
        return self.get_model_cfg(var_name=var_name, level_type=level_type)['var_units']

    def era5_level(self, var_name=None, level_type=None, level=None):
        models_level = self.get_model_cfg(var_name=var_name, level_type=level_type)['era5_level']

        if models_level == 'any':
            return level
        else:
            return int(models_level)


if __name__ == '__main__':
    x = era5_cfg().era5_variable(level_type='surface', var_name='u10m',)
    print(x)
    x = era5_cfg().era5_units(level_type='surface', var_name='u10m',)
    print(x)

    x = era5_cfg().era5_level(level_type='high', var_name='u', level=None)
    print(x)

    x = era5_cfg().era5_level(level_type='high', var_name='u', level=100)
    print(x)

    x = era5_cfg().era5_level(level_type='high', var_name='u', level=2)
    print(x)

    x = era5_cfg().era5_level(level_type='surface', var_name='u10m', level=None)
    print(x)

    x = era5_cfg().era5_level(level_type='surface', var_name='u10m', level=10)
    print(x)

    x = era5_cfg().era5_level(level_type='surface', var_name='u10m', level=2)
    print(x)
