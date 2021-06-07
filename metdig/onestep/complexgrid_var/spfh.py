# -*- coding: utf-8 -*


import numpy as np

from metdig.io import get_model_grid, get_model_3D_grids, get_model_3D_grid

import metdig.utl.utl_stda_grid as utl_stda_grid

import metdig.cal as mdgcal

import logging
_log = logging.getLogger(__name__)


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    spfh = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='spfh', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return spfh


def _by_tmp_rh(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    tmp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='tmp', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    rh = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                        var_name='rh', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if tmp is None or rh is None:
        return None

    # calcu
    pres = utl_stda_grid.gridstda_full_like(tmp, level, var_name='pres')
    td = mdgcal.dewpoint_from_relative_humidity(tmp, rh)
    spfh = mdgcal.specific_humidity_from_dewpoint(pres, td)  # modify by wenzhijun pres和td参数对调，适应于metpy1.0

    return spfh


def read_spfh(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    data = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    _log.info('cal spfh _by_tmp_rh')
    data = _by_tmp_rh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    raise Exception('Can not get any data!')


def _by_self_3D(data_source=None, init_time=None, fhour=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    spfh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                             var_name='spfh', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return spfh


def _by_tmp_rh_3D(data_source=None, init_time=None, fhour=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    rh = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if tmp is None or rh is None:
        return None

    # calcu
    pres = utl_stda_grid.gridstda_full_like_by_levels(tmp, levels)
    td = mdgcal.dewpoint_from_relative_humidity(tmp, rh)
    spfh = mdgcal.specific_humidity_from_dewpoint(pres, td)  # modify by wenzhijun pres和td参数对调，适应于metpy1.0

    return spfh


def read_spfh_3D(data_source=None, init_time=None, fhour=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    data = _by_self_3D(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=extent)
    if data is not None:
        return data

    _log.info('cal spfh _by_tmp_rh')
    data = _by_tmp_rh_3D(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, levels=levels, extent=extent)
    if data is not None:
        return data

    raise Exception('Can not get any data!')


def _by_self_4D(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    spfh = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                              var_name='spfh', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return spfh


def _by_tmp_rh_4D(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                             var_name='tmp', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    rh = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                            var_name='rh', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if tmp is None or rh is None:
        return None

    # calcu
    pres = utl_stda_grid.gridstda_full_like_by_levels(tmp, levels)
    td = mdgcal.dewpoint_from_relative_humidity(tmp, rh)
    spfh = mdgcal.specific_humidity_from_dewpoint(pres, td)  # modify by wenzhijun pres和td参数对调，适应于metpy1.0

    return spfh


def read_spfh_4D(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    data = _by_self_4D(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if data is not None:
        return data

    _log.info('cal spfh _by_tmp_rh')
    data = _by_tmp_rh_4D(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if data is not None:
        return data

    raise Exception('Can not get any data!')
