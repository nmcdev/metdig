# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np

from metdig.io.lib.package_config.base import check_units, SingletonMetaClass


class cassandra_model_cfg(metaclass=SingletonMetaClass):
    def __init__(self):
        self.model_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cassandra_model_cfg.csv'
        # self.model_cfg = pd.read_csv(self.model_cfg_csv, encoding='gbk', comment='#')
        self.model_cfg = pd.read_csv(self.model_cfg_csv, comment='#')

        self.model_cfg = self.model_cfg.fillna('')
        self.model_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式

    def get_model_cfg(self, level_type=None, data_name=None, var_name=None):
        this_cfg = self.model_cfg[(self.model_cfg['data_name'] == data_name) &
                                  (self.model_cfg['var_name'] == var_name) &
                                  (self.model_cfg['level_type'] == level_type)].copy(deep=True).reset_index(drop=True)

        # 此处建议修改为warning
        if len(this_cfg) == 0:
            raise Exception('can not get data_name={} level_type={} var_name={} in {}!'.format(data_name, level_type, var_name, self.model_cfg_csv))

        return this_cfg.to_dict('index')[0]

    def model_cassandra_dir(self, level_type=None, data_name=None, var_name=None, level=None):
        path = self.get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['cassandra_path']

        if level is None:
            return path

        if level_type == 'high':
            return path + str(level) + '/'
        elif level_type == 'surface':
            return path

        return ''

    def model_cassandra_units(self, level_type=None, data_name=None, var_name=None):
        return self.get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['var_units']

    def model_cassandra_level(self, level_type=None, data_name=None, var_name=None, level=None):
        models_level = self.get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['cassandra_level']

        if models_level == 'any':
            return level
        else:
            return int(models_level)
            
    def model_cassandra_prod_type(self, level_type=None, data_name=None, var_name=None):
        return self.get_model_cfg(level_type=level_type, data_name=data_name, var_name=var_name)['cassandra_prod_type']


if __name__ == '__main__':

    x = cassandra_model_cfg().model_cassandra_dir(data_name='ecmwf', var_name='tmp', level_type='high', level=100)
    print(x)
    x = cassandra_model_cfg().model_cassandra_units(data_name='ecmwf', var_name='tmp', level_type='high')
    print(x)

    x = cassandra_model_cfg().model_cassandra_level(data_name='ecmwf', var_name='tmp', level_type='high', level=100)
    print(x)
    x = cassandra_model_cfg().model_cassandra_level(data_name='ecmwf', var_name='tmp', level_type='high', level=None)
    print(x)

    x = cassandra_model_cfg().model_cassandra_prod_type(data_name='ecmwf', var_name='tmp', level_type='high')
    print(x)