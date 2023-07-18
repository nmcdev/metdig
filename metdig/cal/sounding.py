# -*- coding: utf-8 -*-

import numpy as np
import math

import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units

from metdig.cal.lib import utility as utl
import metdig.utl as mdgstda
from metdig.cal.lib.utility import unifydim_stda

__all__ = [
    'lfc',
    'lcl',
    'parcel_profile',
]


# def lcl(pres, tmp, td, max_iters=50, eps=1e-5):
#     pres_p = utl.stda_to_quantity(pres)  # hpa
#     tmp_p = utl.stda_to_quantity(tmp)  # degC
#     td_p = utl.stda_to_quantity(td)  # degC

#     lcl_pres, lcl_tmp = mpcalc.lcl(pres_p, tmp_p, td_p, max_iters=max_iters, eps=eps)

#     lcl_pres = utl.quantity_to_stda_byreference('pres', lcl_pres, pres)
#     lcl_tmp = utl.quantity_to_stda_byreference('tmp', lcl_tmp, pres)

#     return lcl_pres, lcl_tmp

def lfc(pres,tmp,td,psfc=None,t2m=None,td2m=None,parcel_temperature_profile=None,dewpoint_start=None, which='top'):
    #如果psfc=None,t2m=None,td2m=None，则默认从pres的最低层抬升
    #如果psfc、t2m、td2m都不为None 则默认从模式地面开始抬升
    lfc_pres=xr.zeros_like(pres.isel(level=[0])).copy()
    lfc_pres.level.values[0]=0
    lfc_pres.attrs['var_cn_name']='自由对流气压'
    lfc_tmp=xr.zeros_like(tmp.isel(level=[0])).copy()
    lfc_tmp.level.values[0]=0
    lfc_tmp.attrs['var_cn_name']='自由对流温度'

    if((psfc is not None) and (t2m is not None) and (td2m is not None)):
        psfc['level']=('level',[9999])
        t2m['level']=('level',[9999])
        td2m['level']=('level',[9999])

    for imember in pres.member.values:
        for idtime in pres.dtime.values:
            for itime in pres.time.values:
                for ilon in pres.lon.values:
                    for ilat in pres.lat.values:
                        pres1d=pres.sel(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat])
                        tmp1d=tmp.sel(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat])
                        td1d=td.sel(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat])
                        try:
                            if((psfc is not None) and (t2m is not None) and (td2m is not None)):
                                psfc1d=psfc.sel(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat]).copy()
                                t2m1d=t2m.sel(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat]).copy()
                                td2m1d=td2m.sel(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat]).copy()

                                pres1d=pres1d.where(pres1d<psfc1d.values,drop=True)
                                tmp1d=tmp1d.where(pres1d<psfc1d.values,drop=True)
                                td1d=td1d.where(pres1d<psfc1d.values,drop=True)

                                pres1d_p=xr.concat([pres1d,psfc1d],dim='level').sortby('level',ascending=False).stda.quantity.squeeze()
                                tmp1d_p=xr.concat([tmp1d,t2m1d],dim='level').sortby('level',ascending=False).stda.quantity.squeeze()
                                td1d_p=xr.concat([td1d,td2m1d],dim='level').sortby('level',ascending=False).stda.quantity.squeeze()
                                lfc_pres1d_p,lfc_tmp1d_p=mpcalc.lfc(pres1d_p,tmp1d_p,td1d_p)
                            else:
                                pres1d_p=pres1d.stda.quantity.squeeze()
                                tmp1d_p=tmp1d.stda.quantity.squeeze()
                                td1d_p=td1d.stda.quantity.squeeze()
                                lfc_pres1d_p,lfc_tmp1d_p=mpcalc.lfc(pres1d_p,tmp1d_p,td1d_p)
                            lfc_pres.loc[dict(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat])]=[lfc_pres1d_p.magnitude]
                            lfc_tmp.loc[dict(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat])]=[lfc_tmp1d_p.magnitude]
                        except:
                            lfc_pres.loc[dict(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat])]=[np.nan]
                            lfc_tmp.loc[dict(member=[imember],dtime=[idtime],time=[itime],lon=[ilon],lat=[ilat])]=[np.nan]
    return lfc_pres,lfc_tmp
if __name__=='__main__':
    import metdig
    from datetime import datetime
    levels=[1000,950,925,850,800,700,500,200]
    tmp=metdig.io.get_model_3D_grid(data_source='cmadaas',init_time=datetime(2022,5,10,20),fhour=24,data_name='ecmwf',var_name='tmp',levels=levels,extent=[107,119,16,26])
    rh=metdig.io.get_model_3D_grid(data_source='cmadaas',init_time=datetime(2022,5,10,20),fhour=24,data_name='ecmwf',var_name='rh',levels=levels,extent=[107,119,16,26])
    psfc=metdig.io.get_model_grid(data_source='cmadaas',init_time=datetime(2022,5,10,20),fhour=24,data_name='ecmwf',var_name='psfc',extent=[107,119,16,26])
    t2m=metdig.io.get_model_grid(data_source='cmadaas',init_time=datetime(2022,5,10,20),fhour=24,data_name='ecmwf',var_name='t2m',extent=[107,119,16,26])
    td2m=metdig.io.get_model_grid(data_source='cmadaas',init_time=datetime(2022,5,10,20),fhour=24,data_name='ecmwf',var_name='td2m',extent=[107,119,16,26])
    td=metdig.cal.dewpoint_from_relative_humidity(tmp,rh)
    pres = metdig.utl.gridstda_full_like_by_levels(tmp, tmp.level.values.tolist())
    lfc_pres,lfc_tmp=lfc(pres=pres,tmp=tmp,td=td,psfc=psfc,t2m=t2m,td2m=td2m)
    print(lfc_pres)

def lcl(pres, tmp, td, max_iters=50, eps=1e-5):
    pres_p = utl.stda_to_quantity(pres)  # hpa
    tmp_p = utl.stda_to_quantity(tmp)  # degC
    td_p = utl.stda_to_quantity(td)  # degC

    lcl_pres, lcl_tmp = mpcalc.lcl(pres_p, tmp_p, td_p, max_iters=max_iters, eps=eps)

    lcl_pres = utl.quantity_to_stda_byreference('pres', lcl_pres, pres)
    lcl_tmp = utl.quantity_to_stda_byreference('tmp', lcl_tmp, pres)

    return lcl_pres, lcl_tmp


def parcel_profile(pres, tmp, td):
    pres_p = utl.stda_to_quantity(pres)  # hpa
    tmp_p = utl.stda_to_quantity(tmp)  # degC
    td_p = utl.stda_to_quantity(td)  # degC

    profile = mpcalc.parcel_profile(pres_p, tmp_p, td_p)

    profile = utl.quantity_to_stda_byreference('tmp', profile, pres)

    return profile
