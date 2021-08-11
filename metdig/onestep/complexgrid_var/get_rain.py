# -*- coding: utf-8 -*


import numpy as np
import xarray as xr

from metdig.io import get_model_grid

import metdig.utl as mdgstda

import logging
_log = logging.getLogger(__name__)


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, var_name=None, extent=(50, 150, 0, 65)):
    rain = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name=var_name, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return rain


def _by_rain(data_source=None, init_time=None, fhour=None,data_name=None, atime=None, extent=(50, 150, 0, 65)):
    rain1 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='rain', extent=extent, x_percent=0, y_percent=0, throwexp=False)
    
    if rain1 is None:
        return None

    rain = rain1.copy(deep=True)
    
    if((fhour - atime) != 0):
        rain2 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour - atime, data_name=data_name,
                            var_name='rain', extent=extent, x_percent=0, y_percent=0, throwexp=False)

        if rain1 is None or rain2 is None:
            return None
        rain.values = rain1.values - rain2.values
  
    attrs=rain1.attrs
    rain.attrs=attrs
    rain.attrs['valid_time']=atime
    rain.attrs['var_cn_name']=str(atime)+'小时降水'
    rain.attrs['var_name']='rain'+'%02d'%atime
    return rain

def _by_rain01(data_source=None, init_time=None, fhour=None, data_name=None, atime=None, extent=(50, 150, 0, 65)):

    rain01=[]
    for iatime in range(0,atime):
        temp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='rain01', extent=extent, x_percent=0, y_percent=0, throwexp=False)
        if temp is None:
            return None

        rain01.append(temp)
    attrs=temp.attrs
    rain=xr.concat(rain01,dim='dtime').sum('dtime').expand_dims({'dtime':[atime]})
    rain.attrs=attrs
    rain.attrs['valid_time']=atime
    rain.attrs['var_cn_name']=str(atime)+'小时降水'
    rain.attrs['var_name']='rain'+'%02d'%atime
    return rain

def read_rain(data_source=None, init_time=None, fhour=None, extent=(50, 150, 0, 65),data_name=None, atime=6):
    rain=_by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='rain'+'%02d'%atime, extent=extent)
    if rain is not None:
        return rain

    _log.info('cal rain'+'%02d'%atime+' _by_rain')
    rain = _by_rain(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, atime=atime, extent=extent)
    if rain is not None:
        return rain

    _log.info('cal rain'+'%02d'%atime+' _by_rain01')
    rain = _by_rain01(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, atime=atime, extent=extent)
    if rain is not None:
        return rain

    raise Exception('Can not get any data!')

def read_points_rain(points=None,fhours=None,**kwargs):

    rain=[]
    for ifhour in fhours:
        try:
            data=read_rain(fhour=ifhour,**kwargs)
            rain.append(data)
        except:
            continue
    if(rain !=[]):
        rain=xr.concat(rain, dim='dtime')
        return mdgstda.gridstda_to_stastda(rain, points)
    return None
    