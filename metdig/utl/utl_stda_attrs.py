# -*- coding: utf-8 -*-

from metpy.units import units

import os
import pandas as pd
import numpy as np

__all__ = [
    'get_stda_attrs'
]


def __check_units(var_units):
    try:
        if np.array(units(var_units)) != 1:
            raise Exception('error: units={} 单位不能带倍数, '.format(var_units))
    except Exception as e:
        raise e


__stda_attrs = None


def get_stda_attrs(var_name='', **attrs_kwargv):
    '''

    [
        get stda attributes
        Example: attrs = get_stda_attrs(var_name='hgt')
        Example: attrs = get_stda_attrs(var_name='hgt', data_source='cassandra', level_type='high', data_name='ecmwf')
    ]


    Arguments:
        **attrs_kwargv {[type]} -- [其它相关属性，如：data_source='cassandra', level_type='high', data_name='ecmwf']

    Keyword Arguments:
        var_name {str} -- [要素名] (default: {''})


    Returns:
        [dictionary] -- [属性列表]
    '''
    global __stda_attrs
    if __stda_attrs is None:
        __stda_attrs_csv = os.path.dirname(os.path.realpath(__file__)) + '/stda_attrs_cfg.csv'
        __stda_attrs = pd.read_csv(__stda_attrs_csv, encoding='gbk', comment='#')
        __stda_attrs = __stda_attrs.fillna({'var_cn_name': '', 'var_units': '', 'valid_time': 0})
        __stda_attrs.apply(lambda row: __check_units(row['var_units']), axis=1)  # 检查是否满足units格式

    this_attrs = __stda_attrs[__stda_attrs['var_name'] == var_name].copy(deep=True)

    if len(this_attrs) == 0:
        attrs = {
            'data_source': 'undefined stda',
            'level_type': 'undefined stda',
            # 'data_name': 'undefined stda', # stda属性中去除data_name， data_name作为member维(网格数据)、data_start_columns起的列名(站点数据)
            'var_name': 'undefined stda',
            'var_cn_name': 'undefined stda',
            'var_units': 'undefined stda',
            'valid_time': 'undefined stda',
        }
    else:
        attrs = {
            'data_source': '',
            'level_type': '',
            # 'data_name': '', # stda属性中去除data_name， data_name作为member维(网格数据)、data_start_columns起的列名(站点数据)
            'var_name': this_attrs['var_name'].values[0],
            'var_cn_name': this_attrs['var_cn_name'].values[0],
            'var_units': this_attrs['var_units'].values[0],
            'valid_time': this_attrs['valid_time'].values[0],
        }

    attrs.update(attrs_kwargv)

    return attrs


def test():
    # print(stda_attrs)
    for idx, row in __stda_attrs.iterrows():
        print('{:10s}{:}'.format(row['var_name'], row['var_units']))


if __name__ == '__main__':
    # attrs = get_stda_attrs(var_name='u')
    # print(attrs['var_units'])
    test()
