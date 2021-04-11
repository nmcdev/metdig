# -*- coding: utf-8 -*


import numpy as np

from metdig.metdig_io import get_model_grid
from metdig.metdig_io import get_model_3D_grid

import metdig.metdig_utl.utl_stda_grid as utl_stda_grid

import metdig.metdig_cal as mdgcal


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    wvfl = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='wvfl', level=level, extent=extent, x_percent=0.2, y_percent=0.1, throwexp=False)
    return wvfl


def _by_sphf_uv(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    spfh = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='spfh', level=level, extent=extent, x_percent=0.2, y_percent=0.1, throwexp=False)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='u', level=level, extent=extent, x_percent=0.2, y_percent=0.1, throwexp=False)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='v', level=level, extent=extent, x_percent=0.2, y_percent=0.1, throwexp=False)

    if spfh is None or u is None or v is None:
        return None

    # calcu
    wsp = mdgcal.wind_speed(u, v)
    wvfl = mdgcal.cal_ivt_singlelevel(spfh, wsp)

    return wvfl


def _by_tmp_rh_uv(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    tmp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                         var_name='tmp', level=level, extent=extent, x_percent=0.2, y_percent=0.1, throwexp=False)
    rh = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                        var_name='rh', level=level, extent=extent, x_percent=0.2, y_percent=0.1, throwexp=False)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='u', level=level, extent=extent, x_percent=0.2, y_percent=0.1, throwexp=False)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                       var_name='v', level=level, extent=extent, x_percent=0.2, y_percent=0.1, throwexp=False)

    if tmp is None or rh is None or u is None or v is None:
        return None

    # calcu
    pres = utl_stda_grid.gridstda_full_like(tmp, level, var_name='pres')
    td = mdgcal.dewpoint_from_relative_humidity(tmp, rh)
    spfh = mdgcal.specific_humidity_from_dewpoint(pres, td) # modify by wenzhijun pres和td参数对调，适应于metpy1.0
    wsp = mdgcal.wind_speed(u, v)
    wvfl = mdgcal.cal_ivt_singlelevel(spfh, wsp)

    return wvfl


def read_wvfl(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    data = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    # print(data)
    if data is not None:
        return data

    print('cal _by_sphf_uv')
    data = _by_sphf_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    print('cal _by_tmp_rh_uv')
    data = _by_tmp_rh_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=level, extent=extent)
    if data is not None:
        return data

    raise Exception('Can not get any data!')
