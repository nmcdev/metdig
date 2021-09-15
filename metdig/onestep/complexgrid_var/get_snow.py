# -*- coding: utf-8 -*


import numpy as np
import xarray as xr
from datetime import datetime,timedelta
from metdig.io import get_model_grid

import metdig.utl as mdgstda

import logging
_log = logging.getLogger(__name__)


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, var_name=None, extent=(50, 150, 0, 65)):
    snow = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name=var_name, extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return snow


def _by_snow(data_source=None, init_time=None, fhour=None,data_name=None, atime=None, extent=(50, 150, 0, 65)):
    snow1 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='snow', extent=extent, x_percent=0, y_percent=0, throwexp=False)
    
    if snow1 is None:
        return None

    snow = snow1.copy(deep=True)
    
    if((fhour - atime) != 0):
        snow2 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour - atime, data_name=data_name,
                            var_name='snow', extent=extent, x_percent=0, y_percent=0, throwexp=False)

        if snow1 is None or snow2 is None:
            return None
        snow.values = snow1.values - snow2.values
  
    attrs=snow1.attrs
    snow.attrs=attrs
    snow.attrs['valid_time']=atime
    snow.attrs['var_cn_name']=str(atime)+'小时降水'
    snow.attrs['var_name']='snow'+'%02d'%atime
    return snow

def _by_snow01(data_source=None, init_time=None, fhour=None, data_name=None, atime=None, extent=(50, 150, 0, 65)):

    snow01=[]
    for iatime in range(0,atime):
        if(data_name=='era5' or data_name == 'cldas'):  #此处为临时设置，未来需要考虑下架构改进
            temp = get_model_grid(data_source=data_source, init_time=init_time-timedelta(hours=iatime), fhour=0, data_name=data_name,
                            var_name='snow01', extent=extent, x_percent=0, y_percent=0, throwexp=False)
        else:
            temp = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour-iatime, data_name=data_name,
                            var_name='snow01', extent=extent, x_percent=0, y_percent=0, throwexp=False)
        if temp is None:
            return None

        snow01.append(temp)
    attrs=temp.attrs
    if(data_name=='era5' or data_name == 'cldas'):  #此处为临时设置，未来需要考虑下架构改进
        snow=xr.concat(snow01,dim='time').sum('time').expand_dims({'time':[init_time]})
    else:
        snow=xr.concat(snow01,dim='dtime').sum('dtime').expand_dims({'dtime':[atime]})
    snow.attrs=attrs
    snow.attrs['valid_time']=atime
    snow.attrs['var_cn_name']=str(atime)+'小时降水'
    snow.attrs['var_name']='snow'+'%02d'%atime
    return snow

def read_snow(data_source=None, init_time=None, fhour=None, extent=(50, 150, 0, 65),data_name=None, atime=6):
    snow=_by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='snow'+'%02d'%atime, extent=extent)
    if snow is not None:
        return snow

    _log.info('cal snow'+'%02d'%atime+' _by_snow')
    snow = _by_snow(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, atime=atime, extent=extent)
    if snow is not None:
        return snow

    _log.info('cal snow'+'%02d'%atime+' _by_snow01')
    snow = _by_snow01(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, atime=atime, extent=extent)
    if snow is not None:
        return snow

    raise Exception('Can not get any data!')

def read_points_snow(points=None,fhours=None,**kwargs):

    snow=[]
    for ifhour in fhours:
        try:
            data=read_snow(fhour=ifhour,**kwargs)
            snow.append(data)
        except:
            continue
    if(snow !=[]):
        snow=xr.concat(snow, dim='dtime')
        return mdgstda.gridstda_to_stastda(snow, points)
    return None
    