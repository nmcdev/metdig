import numpy as np

from metdig.io import get_model_grid
from metdig.io import get_model_3D_grid,get_model_3D_grids

import metdig.utl.utl_stda_grid as utl_stda_grid

from metdig.cal import thermal
from metdig.cal import dynamic
from metdig.cal import other

import logging
_log = logging.getLogger(__name__)


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, level=None, extent=(50, 150, 0, 65)):
    wsp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='wsp', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='u', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='v', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return wsp, u, v


def _by_uv(data_source=None, init_time=None, fhour=None, data_name=None, level=None, extent=(50, 150, 0, 65)):
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='u', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='v', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if u is None or v is None:
        return None, None, None

    # calcu
    wsp = other.wind_speed(u, v)
    return wsp, u, v


def read_wsp(data_source=None, init_time=None, fhour=None, data_name=None, level=None, extent=(50, 150, 0, 65)):
    wsp, u, v = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if wsp is not None and u is not None and v is not None:
        return wsp, u, v

    _log.info('cal wsp _by_uv')
    wsp, u, v = _by_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if wsp is not None and u is not None and v is not None:
        return wsp, u, v

    raise Exception('Can not get any data!')

def _by_self_4D(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    wsp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                              var_name='wsp', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return wsp

def _by_u_v_4d(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='u', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                        var_name='v', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if u is None or v is None:
        return None

    wsp = other.wind_speed(u,v)

    return wsp

def read_w_4d(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=None):

    w = _by_self_4D(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if w is not None:
        return w

    _log.info('cal w _by_vvel_tmp_spfh')
    w = _by_u_v_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if w is not None:
        return w

    raise Exception('Can not get any data!')
