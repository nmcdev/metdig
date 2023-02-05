# -*- coding: utf-8 -*


import numpy as np
import xarray as xr

from metdig.io import get_model_grid,get_model_grids
import metdig.utl.utl_stda_grid as utl_stda_grid

import metdig.cal as mdgcal
import metdig.utl as mdgstda

import logging
_log = logging.getLogger(__name__)


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, extent=(50, 150, 0, 65)):
    rh2m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='rh2m', extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return rh2m


def _by_t2m_td2m(data_source=None, init_time=None, fhour=None, data_name=None, extent=(50, 150, 0, 65)):

    t2m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='t2m', extent=extent, x_percent=0, y_percent=0, throwexp=False)
    td2m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                        var_name='td2m',extent=extent, x_percent=0, y_percent=0, throwexp=False)
    
    if t2m is None or td2m is None:
        return None

    rh2m = mdgcal.relative_humidity_from_dewpoint(t2m,td2m)

    return rh2m

def read_rh2m(data_source=None, init_time=None, fhour=None, data_name=None, extent=(50, 150, 0, 65)):
    data = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=extent)
    if data is not None:
        return data

    _log.info('cal rh2m _by_t2m_td2m')
    data = _by_t2m_td2m(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=extent)
    if data is not None:
        return data

    return None

def _by_self_3D(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    rh2m = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                             var_name='rh2m', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return rh2m
    
def _by_t2m_td2m_3d(data_source=None, init_time=None, fhours=None, data_name=None, extent=(50, 150, 0, 65)):

    t2m = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='t2m', extent=extent, x_percent=0, y_percent=0, throwexp=False)
    td2m = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                        var_name='td2m', extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if t2m is None or td2m is None:
        return None
    rh2m = mdgcal.relative_humidity_from_dewpoint(t2m,td2m)
    return rh2m

def read_rh2m3d(data_source=None, init_time=None, fhours=None, data_name=None, extent=(50, 150, 0, 65)):

    data = _by_self_3D(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,extent=extent)
    if data is not None:
        return data
    _log.info('cal rh2m _by_t2m_td2m_3d')
    data = _by_t2m_td2m_3d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,extent=extent)
    if data is not None:
        return data
    raise Exception('Can not get any data!')

def read_points_rh2m(points=None,fhours=None,**kwargs):

    rh2m=[]
    for ifhour in fhours:
        try:
            data=read_rh2m(fhour=ifhour,**kwargs)
            rh2m.append(data)
        except:
            continue
    if(rh2m !=[]):
        rh2m=xr.concat(rh2m, dim='dtime')
        return mdgstda.gridstda_to_stastda(rh2m, points)
    return None
