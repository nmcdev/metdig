# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np

from metdig.io.lib.package_config.base import check_units, SingletonMetaClass
from metdig.io.lib.package_config.cmadaas_datacode_cfg import cmadaas_datacode_cfg


class cmadaas_model_cfg(metaclass=SingletonMetaClass):
    def __init__(self):
        self.model_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cmadaas_model_cfg.csv'
        self.model_cfg = pd.read_csv(self.model_cfg_csv, encoding='gbk', comment='#')
        self.model_cfg = self.model_cfg.fillna('')
        self.model_cfg.apply(lambda row: check_units(row['var_units']), axis=1)  # 检查是否满足units格式
        self.model_cfg['cmadaas_data_code'] = self.model_cfg.apply(lambda row: row['cmadaas_data_code'].strip('/').split('/'), axis=1)

    def get_model_cfg(self, data_name=None, var_name=None, level_type=None, data_code=None):
        this_cfg = self.model_cfg[(self.model_cfg['data_name'] == data_name) &
                                  (self.model_cfg['var_name'] == var_name) &
                                  (self.model_cfg['level_type'] == level_type)].copy(deep=True).reset_index(drop=True)

        if len(this_cfg) == 0:
            raise Exception('can not get data_name={} level_type={} var_name={}  in {}!'.format(data_name, level_type, var_name, self.model_cfg_csv))

        if len(this_cfg) > 1:
            raise Exception('error: greater than 1 recode! data_name={} level_type={} var_name={} in {}!'.format(
                data_name, level_type, var_name, self.model_cfg_csv))

        cmadaas_data_code = this_cfg['cmadaas_data_code'].values[0]

        if data_code.strip().lower() != 'any':
            if data_code not in cmadaas_data_code:
                raise Exception('error: {} not in cmadaas_data_code! data_name={} level_type={} var_name={} in {}!'.format(
                    data_code, data_name, level_type, var_name, self.model_cfg_csv))

        return this_cfg.to_dict('index')[0]

    def model_cmadaas_data_code(self, data_name=None, var_name=None, level_type=None, fhour=0):
        cmadaas_data_code = cmadaas_datacode_cfg().get_datacode_cfg(data_name=data_name, fhour=fhour)
        if cmadaas_data_code.strip().lower() != 'any':
            return cmadaas_data_code
        return self.get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=cmadaas_data_code)['cmadaas_data_code'][0]

    def model_cmadaas_var_name(self, data_name=None, var_name=None, level_type=None, data_code=None):
        return self.get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=data_code)['cmadaas_var_name']

    def model_cmadaas_level_type(self, data_name=None, var_name=None, level_type=None, data_code=None):
        temp = self.get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=data_code)['cmadaas_level_type']
        if(temp == 999):  # 表内不好储存字符型符号
            return '-'
        else:
            return temp

    def model_cmadaas_units(self, data_name=None, var_name=None, level_type=None, data_code=None):
        return self.get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=data_code)['var_units']

    def model_cmadaas_level(self, data_name=None, var_name=None, level_type=None, data_code=None, level=None):
        models_level = self.get_model_cfg(data_name=data_name, var_name=var_name, level_type=level_type, data_code=data_code)['cmadaas_level']

        if models_level == 'any':
            return level
        else:
            return int(models_level)

if __name__ == '__main__':

    data_code = cmadaas_model_cfg().model_cmadaas_data_code(data_name='ecmwf', var_name='tmp', level_type='high', fhour=0)
    print(data_code)

    cmadaas_var_name = cmadaas_model_cfg().model_cmadaas_var_name(data_name='ecmwf', var_name='tmp', level_type='high', data_code=data_code)
    print(cmadaas_var_name)

    level = cmadaas_model_cfg().model_cmadaas_level(data_name='ecmwf', var_name='tmp', level_type='high', data_code=data_code, level=2)
    print(level)
