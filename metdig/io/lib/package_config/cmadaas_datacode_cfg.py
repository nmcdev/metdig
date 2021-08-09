# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np

from metdig.io.lib.package_config.base import check_units, SingletonMetaClass


class cmadaas_datacode_cfg(metaclass=SingletonMetaClass):
    def __init__(self):
        self.datacode_cfg_csv = os.path.dirname(os.path.realpath(__file__)) + '/cmadaas_datacode_cfg.csv'
        self.datacode_cfg = pd.read_csv(self.datacode_cfg_csv, encoding='gbk', comment='#')
        self.datacode_cfg = self.datacode_cfg.fillna('')
        
    def get_datacode_cfg(self, data_name=None, fhour=0):

        if fhour == 0:
            fhour_flag = 0
        else:
            fhour_flag = 1
        this_cfg = self.datacode_cfg[(self.datacode_cfg['data_name'] == data_name) &
                                (self.datacode_cfg['fhour_flag'] == fhour_flag)].copy(deep=True).reset_index(drop=True)

        if len(this_cfg) == 0:
            raise Exception('can not get data_name={} fhour_flag={} in {}!'.format(data_name, fhour_flag, self.datacode_cfg_csv))

        if len(this_cfg) > 1:
            raise Exception('error: greater than 1 recode! data_name={} fhour_flag={} in {}!'.format(data_name, fhour_flag, self.datacode_cfg_csv))

        return this_cfg['data_code'].values[0]

    