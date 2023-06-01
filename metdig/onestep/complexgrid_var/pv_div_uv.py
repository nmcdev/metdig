# -*- coding: utf-8 -*


import numpy as np
import xarray as xr

from metdig.io import get_model_grid
from metdig.io import get_model_3D_grid
from metdig.io import get_model_3D_grids

import metdig.utl.utl_stda_grid as utl_stda_grid

import metdig.cal as mdgcal

import logging
_log = logging.getLogger(__name__)


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, level=250, extent=(50, 150, 0, 65)):

    if(isinstance(level, list) is False):
        level = list([level])

    pv = []
    div = []
    u = []
    v = []
    for ilevel in level:
        _ = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='pv', level=ilevel, extent=extent, x_percent=0, y_percent=0, throwexp=False)
        if _ is not None:
            pv.append(_)
    if len(pv) == 0:
        return None, None, None, None

    for ilevel in level:
        _ = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='div', level=ilevel, extent=extent, x_percent=0, y_percent=0, throwexp=False)
        if _ is not None:
            div.append(_)
        _ = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='u', level=ilevel, extent=extent, x_percent=0, y_percent=0, throwexp=False)
        if _ is not None:
            u.append(_)
        _ = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                           var_name='v', level=ilevel, extent=extent, x_percent=0, y_percent=0, throwexp=False)
        if _ is not None:
            v.append(_)
    if len(div) == 0 or len(u) == 0 or len(v) == 0:
        return None, None, None, None

    pv = xr.concat(pv, dim='level')
    div = xr.concat(div, dim='level')
    u = xr.concat(u, dim='level')
    v = xr.concat(v, dim='level')
    return pv, div, u, v

def _by_self_4d(data_source=None, init_time=None, fhours=None, data_name=None, 
                levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 100], extent=(50, 150, 0, 65)):
    pv = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='pv', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    div = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='div', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='u', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='v', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return pv, div, u, v



def _by_uv_tmp(data_source=None, init_time=None, fhour=None, data_name=None,
               lvl_ana=250, levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 100],
               extent=(50, 150, 0, 65)):
    u = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='u', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='v', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    tmp = get_model_3D_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='tmp', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if u is None or v is None or tmp is None:
        return None, None, None, None

    # calculate
    pres = utl_stda_grid.gridstda_full_like_by_levels(u, u['level'].values)
    thta = mdgcal.potential_temperature(pres, tmp)
    pv = mdgcal.potential_vorticity_baroclinic(thta, pres, u, v)
    div = mdgcal.divergence(u, v)

    # get lvl_ana
    pv = pv.where(pv['level'] == lvl_ana, drop=True)
    div = div.where(div['level'] == lvl_ana, drop=True)
    u = u.where(u['level'] == lvl_ana, drop=True)
    v = v.where(v['level'] == lvl_ana, drop=True)
    return pv, div, u, v

def _by_uv_tmp_4d(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):
    u = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='u', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    v = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='v', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    tmp = get_model_3D_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name,
                         var_name='tmp', levels=levels, extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if u is None or v is None or tmp is None:
        return None, None, None, None

    # calculate
    pres = utl_stda_grid.gridstda_full_like_by_levels(u, u['level'].values)
    thta = mdgcal.potential_temperature(pres, tmp)
    pv = mdgcal.potential_vorticity_baroclinic(thta, pres, u, v)
    div = mdgcal.divergence(u, v)

    return pv, div, u, v



def read_pv_div_uv(data_source=None, init_time=None, fhour=None, data_name=None,
                   lvl_ana=250, levels=[1000, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 100],
                   extent=(50, 150, 0, 65)):
    pv, div, u, v = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=lvl_ana, extent=extent)
    if pv is not None and div is not None and u is not None and v is not None:
        return pv, div, u, v

    _log.info('cal pv div _by_uv_tmp')
    pv, div, u, v = _by_uv_tmp(data_source=data_source, init_time=init_time, fhour=fhour,
                               data_name=data_name, lvl_ana=lvl_ana, levels=levels, extent=extent)
    if pv is not None and div is not None and u is not None and v is not None:
        return pv, div, u, v

    raise Exception('Can not get any data!')


def read_pv_div_uv_4d(data_source=None, init_time=None, fhours=None, data_name=None, levels=None, extent=(50, 150, 0, 65)):

    pv, div, u, v = _by_self_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if pv is not None and div is not None and u is not None and v is not None:
        return pv, div, u, v
    _log.info('cal vvel _by_uv_tmp_4d')
    pv, div, u, v = _by_uv_tmp_4d(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, levels=levels, extent=extent)
    if pv is not None and div is not None and u is not None and v is not None:
        return pv, div, u, v
    
    raise Exception('Can not get any data!')