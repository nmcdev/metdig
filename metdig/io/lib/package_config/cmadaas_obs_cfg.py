# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np

from metdig.io.lib.package_config.base import check_units, SingletonMetaClass


class cmadaas_obs_cfg(metaclass=SingletonMetaClass):
    def __init__(self):
        self.obs_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cmadaas_obs_cfg.csv'
        self.obs_cfg = pd.read_csv(self.obs_cfg_csv, encoding='gbk', comment='#')
        self.obs_cfg = self.obs_cfg.fillna('')
        self.obs_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式

    def get_obs_cfg(self, data_name=None, var_name=None):
        this_cfg = self.obs_cfg[(self.obs_cfg['data_name'] == data_name) &
                                (self.obs_cfg['var_name'] == var_name)].copy(deep=True).reset_index(drop=True)

        if len(this_cfg) == 0:
            raise Exception('can not get data_name={} var_name={} in {}!'.format(data_name, var_name, self.obs_cfg_csv))

        return this_cfg.to_dict('index')[0]

    def obs_cmadaas_data_code(self, data_name=None, var_name=None):
        return self.get_obs_cfg(data_name=data_name, var_name=var_name)['cmadaas_data_code']

    def obs_cmadaas_units(self, data_name=None, var_name=None):
        return self.get_obs_cfg(data_name=data_name, var_name=var_name)['var_units']

    def obs_cmadaas_var_name(self, data_name=None, var_name=None):
        return self.get_obs_cfg(data_name=data_name, var_name=var_name)['cmadaas_var_name']

if __name__ == '__main__':
    x = cmadaas_obs_cfg().obs_cmadaas_data_code(data_name='sfc_chn_hor', var_name='rain24')
    print(x)
    
    x = cmadaas_obs_cfg().obs_cmadaas_units(data_name='sfc_chn_hor', var_name='rain24')
    print(x)

    x = cmadaas_obs_cfg().obs_cmadaas_var_name(data_name='sfc_chn_hor', var_name='rain24')
    print(x)