# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np

from metdig.io.lib.package_config.base import check_units, SingletonMetaClass


class cassandra_obs_cfg(metaclass=SingletonMetaClass):
    def __init__(self):
        self.obs_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cassandra_obs_cfg.csv'
        self.obs_cfg = pd.read_csv(self.obs_cfg_csv, encoding='gbk', comment='#')
        self.obs_cfg = self.obs_cfg.fillna('')
        self.obs_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式

    def obs_cassandra_dir(self, data_name=None, var_name=None):
        _obs_cfg = self.obs_cfg[(self.obs_cfg['data_name'] == data_name) &
                                (self.obs_cfg['var_name'] == var_name)].copy(deep=True)

        if len(_obs_cfg) == 0:
            raise Exception('can not get data_name = {} var_name={} in {}!'.format(data_name, var_name, self.obs_cfg_csv))

        return _obs_cfg['cassandra_path'].values[0]

    def obs_cassandra_units(self, data_name=None, var_name=None):
        _obs_cfg = self.obs_cfg[(self.obs_cfg['data_name'] == data_name) &
                                (self.obs_cfg['var_name'] == var_name)].copy(deep=True)
        if len(_obs_cfg) == 0:
            return ''
        return _obs_cfg['var_units'].values[0]


if __name__ == '__main__':

    x = cassandra_obs_cfg().obs_cassandra_dir(data_name='sfc_chn_hor', var_name='rain24')
    print(x)

    x = cassandra_obs_cfg().obs_cassandra_units(data_name='sfc_chn_hor', var_name='rain24')
    print(x)
