# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np

from metdig.io.lib.package_config.base import check_units, SingletonMetaClass


class cassandra_radar_cfg(metaclass=SingletonMetaClass):
    def __init__(self):
        self.radar_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cassandra_radar_cfg.csv'
        self.radar_cfg = pd.read_csv(self.radar_cfg_csv, encoding='gbk', comment='#')
        self.radar_cfg = self.radar_cfg.fillna('')
        self.radar_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式

    def get_radar_cfg(self, data_name=None, var_name=None):
        this_cfg = self.radar_cfg[(self.radar_cfg['data_name'] == data_name) &
                                  (self.radar_cfg['var_name'] == var_name)].copy(deep=True).reset_index(drop=True)

        if len(this_cfg) == 0:
            raise Exception('can not get data_name={} var_name={} in {}!'.format(data_name, var_name, self.radar_cfg_csv))

        return this_cfg.to_dict('index')[0]

    def radar_cassandra_dir(self, data_name=None, var_name=None):
        return self.get_radar_cfg(data_name=data_name, var_name=var_name)['cassandra_path']

    def radar_cassandra_units(self, data_name=None, var_name=None):
        return self.get_radar_cfg(data_name=data_name, var_name=var_name)['var_units']

if __name__ == '__main__':

    x = cassandra_radar_cfg().radar_cassandra_dir(data_name='achn', var_name='cref')
    print(x)

    x = cassandra_radar_cfg().radar_cassandra_dir(data_name='achn', var_name='cref')
    print(x)