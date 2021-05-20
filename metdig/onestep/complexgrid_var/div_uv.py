import numpy as np
import xarray as xr

from metdig.io import get_model_3D_grid,get_model_3D_grids,get_model_grid

import metdig.utl.utl_stda_grid as utl_stda_grid

from metdig.cal import thermal
from metdig.cal import dynamic

def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    div = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='div', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return div,u,v

def _by_uv(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if u is None or v is None:
        return None, None, None

    # calcu
    div = dynamic.divergence(u, v)
    return div, u, v

def read_div_uv(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    div,u,v = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if div is not None and u is not None and v is not None:
        return div, u, v

    print('cal _by_uv')
    div, u, v = _by_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if div is not None and u is not None and v is not None:
        return div, u, v

    raise Exception('Can not get any data!')

def _by_self_4d(data_source=None, init_time=None, fhours=None, data_name=None, levels=500, extent=(50, 150, 0, 65)):
    div = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='div', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='u', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='v', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return div,u,v

def _by_uv_4d(data_source=None, init_time=None, fhours=None, data_name=None, levels=500, extent=(50, 150, 0, 65)):
    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='u', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, var_name='v', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if u is None or v is None:
        return None, None, None

    div = dynamic.divergence(u, v)
    return div, u, v


def read_div_uv_4d(data_source=None, init_time=None, fhours=None, data_name=None, levels=500, extent=(50, 150, 0, 65)):

    div,u,v = _by_self_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if div is not None and u is not None and v is not None:
        return div, u, v

    print('cal _by_uv')
    div, u, v = _by_uv_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if div is not None and u is not None and v is not None:
        return div, u, v

    raise Exception('Can not get any data!')