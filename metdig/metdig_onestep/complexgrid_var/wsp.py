import numpy as np

from metdig.metdig_io import get_model_grid
from metdig.metdig_io import get_model_3D_grid

import metdig.metdig_utl.utl_stda_grid as utl_stda_grid

from metdig.metdig_cal import thermal
from metdig.metdig_cal import dynamic
from metdig.metdig_cal import other

def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    wsp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='wsp', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return wsp,u,v

def _by_uv(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=level, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if u is None or v is None:
        return None, None, None

    # calcu
    wsp = other.wind_speed(u, v)
    return wsp, u, v

def read_wsp(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    wsp,u,v = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if wsp is not None and u is not None and v is not None:
        return wsp, u, v

    print('cal _by_uv')
    wsp, u, v = _by_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if wsp is not None and u is not None and v is not None:
        return wsp, u, v

    raise Exception('Can not get any data!')
