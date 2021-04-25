# -*- coding: utf-8 -*


import numpy as np
import xarray as xr

from metdig.io import get_model_grid

import metdig.utl.utl_stda_grid as utl_stda_grid

import metdig.cal as mdgcal


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    theta = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='theta', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return theta


def _by_tmp_rh(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    tmp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='tmp', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    rh = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='rh', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
        
    if tmp is None or rh is None:
        return None

    # calcu
    pres = utl_stda_grid.gridstda_full_like(tmp, level, var_name='pres')
    td = mdgcal.dewpoint_from_relative_humidity(tmp, rh)
    theta = mdgcal.equivalent_potential_temperature(pres, tmp, td)

    return theta


def read_theta(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    data = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    print('cal _by_tmp_rh')
    data = _by_tmp_rh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    raise Exception('Can not get any data!')

def read_theta3d(levels,**read_theta_kwargs):
    data=[]
    for ilevel in levels:
        data.append(read_theta(level=ilevel,**read_theta_kwargs))
    data=xr.concat(data,dim='level')
    return data