# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np

from metdig.io.lib.package_config.base import check_units, SingletonMetaClass


class cassandra_sate_cfg(metaclass=SingletonMetaClass):
    def __init__(self):
        self.sate_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cassandra_sate_cfg.csv'
        self.sate_cfg = pd.read_csv(self.sate_cfg_csv, encoding='gbk', comment='#')
        self.sate_cfg = self.sate_cfg.fillna('')
        self.sate_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式
        self.sate_cfg['channel'] = self.sate_cfg.apply(lambda row: row['channel'].strip('/').split('/'), axis=1)

    def get_sate_cfg(self, data_name=None, var_name=None, channel=None):
        this_cfg = self.sate_cfg[(self.sate_cfg['data_name'] == data_name) &
                                 (self.sate_cfg['var_name'] == var_name)].copy(deep=True).reset_index(drop=True)

        # channel 是list
        index = -1
        for idx, row in this_cfg.iterrows():
            if 'any' in row['channel'] or str(channel) in row['channel']:
                index = idx
                break

        if index < 0:
            raise Exception('can not get data_name={} var_name={} channel={} in {}!'.format(data_name, var_name, channel, self.sate_cfg_csv))

        return this_cfg.to_dict('index')[index]

    def sate_cassandra_dir(self, data_name=None, var_name=None, channel=None):
        return self.get_sate_cfg(data_name=data_name, var_name=var_name, channel=channel)['cassandra_path']

    def sate_cassandra_units(self, data_name=None, var_name=None, channel=None):
        return self.get_sate_cfg(data_name=data_name, var_name=var_name, channel=channel)['var_units']

if __name__ == '__main__':

    x = cassandra_sate_cfg().sate_cassandra_dir(data_name='fy4al1', var_name='ref', channel=1)
    print(x)

    x = cassandra_sate_cfg().sate_cassandra_dir(data_name='fy4al1', var_name='ref', channel=1)
    print(x)