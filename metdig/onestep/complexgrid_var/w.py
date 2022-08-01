# -*- coding: utf-8 -*


import numpy as np
import xarray as xr

from metdig.io import get_model_3D_grids, get_model_grid
from metdig.onestep.complexgrid_var.spfh import read_spfh, read_spfh_4d

import metdig.utl.utl_stda_grid as utl_stda_grid

import metdig.cal as mdgcal

import logging
_log = logging.getLogger(__name__)


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, level=None, extent=(50, 150, 0, 65)):
    theta = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='w', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return theta


def _by_vvel_tmp_spfh(data_source=None, init_time=None, fhour=None, data_name=None, level=None, extent=(50, 150, 0, 65)):
    spfh = read_spfh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=extent)

    tmp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='tmp', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    vvel = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                        var_name='vvel', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if tmp is None or vvel is None or spfh is None:
        return None

    w = mdgcal.vertical_velocity(vvel, tmp, spfh)

    return w

def read_w(data_source=None, init_time=None, fhour=None, data_name=None, level=None, extent=(50, 150, 0, 65)):
    data = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    _log.info('cal w _by_vvel_tmp_spfh')
    data = _by_vvel_tmp_spfh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    raise Exception('Can not get any data!')


def read_w3d(levels, **read_theta_kwargs):
    data = []
    for ilevel in levels:
        data.append(read_w(level=ilevel, **read_theta_kwargs))
    data = xr.concat(data, dim='level')
    return data

def _by_self_4D(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    w = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                              var_name='w', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return w

def _by_vvel_tmp_spfh_4d(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    spfh = read_spfh_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)

    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='tmp', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    vvel = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                        var_name='vvel', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)


    if tmp is None or vvel is None or spfh is None:
        return None

    w = mdgcal.vertical_velocity(vvel, tmp, spfh)

    return w

def read_w_4d(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=None):

    w = _by_self_4D(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if w is not None:
        return w

    _log.info('cal w _by_vvel_tmp_spfh')
    w = _by_vvel_tmp_spfh_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if w is not None:
        return w

    raise Exception('Can not get any data!')

if __name__=='__main__':
    import pandas as pd
    points={'lon': [90], 'lat': [30]}
    init_times=pd.date_range('2022-07-03-20','2022-07-04-08',freq='1H')
    fhours=[0]
    levels=[200, 225, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 775, 800, 825, 850, 875, 900, 925, 950, 975, 1000][::-1]
    data_source='cds'
    data_name='era5'
    w = read_w_4d(data_source=data_source, init_time=init_times, fhours=fhours, data_name=data_name, levels=levels)
