# -*- coding: utf-8 -*


import numpy as np
import xarray as xr

from metdig.io import get_model_grid
from metdig.onestep.complexgrid_var.spfh import read_spfh

import metdig.utl.utl_stda_grid as utl_stda_grid

import metdig.cal as mdgcal

import logging
_log = logging.getLogger(__name__)


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    vvel = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='vvel', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return vvel


def _by_w_tmp_spfh(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    spfh = read_spfh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=extent)

    tmp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='tmp', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    w = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                        var_name='w', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if tmp is None or w is None or spfh is None:
        return None

    w = mdgcal.vertical_velocity_pressure(w, tmp, spfh)

    return w

def read_vvel(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    data = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    _log.info('cal vvel _by_w_tmp_spfh')
    data = _by_w_tmp_spfh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    return None
    # raise Exception('Can not get any data!')


def read_vvel3d(levels, **read_vvel_kwargs):
    data = []
    for ilevel in levels:
        temp=read_vvel(level=ilevel, **read_vvel_kwargs)
        if (temp is not None):
            data.append(temp)
    data = xr.concat(data, dim='level')
    return data

def read_vvel3ds(fhours, **read_vvel3d_kwargs):
    data = []
    for ifhour in fhours:
        temp=read_vvel3d(fhour=ifhour, **read_vvel3d_kwargs)
        if (temp is not None):
            data.append(temp)
    data = xr.concat(data, dim='dtime')
    return data