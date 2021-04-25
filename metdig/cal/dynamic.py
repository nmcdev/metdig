# -*- coding: utf-8 -*-

'''

'''


import numpy as np

import metpy.calc as mpcalc
from metpy.units import units

from .lib import utility as utl
import metdig.utl.utl_stda_grid as utl_stda_grid

def vertical_velocity(vvel,tmp,mir=0):
    '''

    [Calculate w from omega assuming hydrostatic conditions.]

    Arguments:
        vvel {[stda]} -- [omega.]
        temperature {[stda]} -- [x component of the wind.]
        mir {[stda]} -- [y component of the wind. ]
    '''
    omega = utl.stda_to_quantity(vvel)
    temperature = utl.stda_to_quantity(tmp)
    pressure=utl_stda_grid.gridstda_full_like_by_levels(tmp, tmp.level.values.tolist())
    pressure=utl.stda_to_quantity(pressure)
    w=mpcalc.vertical_velocity(omega,pressure,temperature,mir)
    w = utl.quantity_to_stda_byreference('w', w, vvel)
    return w

def var_advect(var,u, v):
    '''

    [Calculate the absolute vorticity of the horizontal wind.]

    Arguments:
        var {[stda]} -- [any variable.]
        u {[stda]} -- [x component of the wind.]
        v {[stda]} -- [y component of the wind. ]
    '''

    dx, dy = mpcalc.lat_lon_grid_deltas(u['lon'].values, u['lat'].values)
    adv = v.copy(deep=True)
    for ilvl in var['level'].values:
        for it in var['time'].values:
            for idt in var['dtime'].values:
                for imdl in var['member'].values:
                    u2d = u.sel(level=ilvl,time=it,dtime=idt,member=imdl).squeeze()
                    v2d = v.sel(level=ilvl,time=it,dtime=idt,member=imdl).squeeze()
                    var2d = var.sel(level=ilvl,time=it,dtime=idt,member=imdl).squeeze()
                    u2d = utl.stda_to_quantity(u2d)
                    v2d = utl.stda_to_quantity(v2d)
                    var2d = utl.stda_to_quantity(var2d)
                    adv2d=mpcalc.advection(var2d,u=u2d,v=v2d,dx=dx,dy=dy)
                    adv.loc[dict(level=ilvl,time=it,dtime=idt,member=imdl)] = np.array(adv2d)
                    adv.attrs['var_units'] = str(adv2d.units)
    adv = utl.quantity_to_stda_byreference(var.attrs['var_name']+'adv', adv.values * units(adv.attrs['var_units']), u)
    return adv


def vorticity(u, v):
    '''

    [Calculate the vertical vorticity of the horizontal wind.]
    [only for grid stda]
    Arguments:
        u {[stda]} -- [x component of the wind. ]
        v {[stda]} -- [y component of the wind. ]
    '''

    x, y = np.meshgrid(u['lon'].values, u['lat'].values)
    x = x * units('degrees')
    y = y * units('degrees')

    dx, dy = mpcalc.lat_lon_grid_deltas(u['lon'].values, u['lat'].values)

    vort = v.copy(deep=True)
    for ilvl in u['level'].values:
        for it in u['time'].values:
            for idt in u['dtime'].values:
                for imdl in u['member'].values:
                    u2d = u.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
                    v2d = v.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()

                    u2d = utl.stda_to_quantity(u2d)  # m/s
                    v2d = utl.stda_to_quantity(v2d)  # m/s

                    vort2d = mpcalc.vorticity(u2d, v2d, dx=dx, dy=dy)  # 垂直涡度  '1 / second'

                    vort.loc[dict(level=ilvl, time=it, dtime=idt, member=imdl)] = np.array(vort2d)
                    vort.attrs['var_units'] = str(vort2d.units)

    vort = utl.quantity_to_stda_byreference('vort', vort.values * units(vort.attrs['var_units']), u)

    return vort

def frontogenesis(thta, u, v):
    '''

    [Calculate the 2D kinematic frontogenesis of a temperature field.]
    [only for grid stda]
    Arguments:
        thta {[stda]} -- [Potential temperature. ]
        u {[stda]} -- [x component of the wind. ]
        v {[stda]} -- [y component of the wind. ]
    '''
    x, y = np.meshgrid(u['lon'].values, u['lat'].values)
    x = x * units('degrees')
    y = y * units('degrees')

    dx, dy = mpcalc.lat_lon_grid_deltas(u['lon'].values, u['lat'].values)
    
    fg = v.copy(deep=True)
    for ilvl in u['level'].values:
        for it in u['time'].values:
            for idt in u['dtime'].values:
                for imdl in u['member'].values:
                    thta2d = thta.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
                    u2d = u.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
                    v2d = v.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
                
                    thta2d = utl.stda_to_quantity(thta2d)  # degC
                    u2d = utl.stda_to_quantity(u2d)  # m/s
                    v2d = utl.stda_to_quantity(v2d)  # m/s

                    fg2d = mpcalc.frontogenesis(thta2d, u2d, v2d, dx=dx, dy=dy)  # kelvin / meter / second

                    fg.loc[dict(level=ilvl, time=it, dtime=idt, member=imdl)] = np.array(fg2d)
                    fg.attrs['var_units'] = str(fg2d.units)

    fg = utl.quantity_to_stda_byreference('fg', fg.values * units(fg.attrs['var_units']), u)

    return fg


def absolute_vorticity(u, v):
    '''

    [Calculate the absolute vorticity of the horizontal wind.]
    [only for grid stda]
    Arguments:
        u {[stda]} -- [x component of the wind. ]
        v {[stda]} -- [y component of the wind. ]
    '''

    x, y = np.meshgrid(u['lon'].values, u['lat'].values)
    x = x * units('degrees')
    y = y * units('degrees')

    dx, dy = mpcalc.lat_lon_grid_deltas(u['lon'].values, u['lat'].values)

    absv = v.copy(deep=True)
    for ilvl in u['level'].values:
        for it in u['time'].values:
            for idt in u['dtime'].values:
                for imdl in u['member'].values:
                    u2d = u.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
                    v2d = v.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()

                    u2d = utl.stda_to_quantity(u2d)  # m/s
                    v2d = utl.stda_to_quantity(v2d)  # m/s

                    absv2d = mpcalc.absolute_vorticity(u2d, v2d, dx, dy, y)  # 绝对涡度  '1 / second'

                    absv.loc[dict(level=ilvl, time=it, dtime=idt, member=imdl)] = np.array(absv2d)
                    absv.attrs['var_units'] = str(absv2d.units)

    absv = utl.quantity_to_stda_byreference('absv', absv.values * units(absv.attrs['var_units']), u)

    return absv



def potential_vorticity_baroclinic(thta, pres, u, v):
    '''

    [Calculate the baroclinic potential vorticity.]

    Arguments:
        thta {[stda]} -- [potential temperature. ]
        pres {[stda]} -- [vertical pressures. ]
        u {[stda]} -- [x component of the wind. ]
        v {[stda]} -- [y component of the wind. ]

    Returns:
        [stda] -- [baroclinic potential vorticity]
    '''

    lons = thta['lon'].values
    lats = thta['lat'].values

    dx, dy = mpcalc.lat_lon_grid_deltas(lons, lats)
    dx = dx[np.newaxis, :, :]
    dy = dy[np.newaxis, :, :]
    lats = lats[np.newaxis, :, np.newaxis] * units('degrees')

    pv = thta.copy(deep=True)
    for it in thta['time'].values:
        for idt in thta['dtime'].values:
            for imdl in thta['member'].values:
                thta3d = thta.sel(time=it, dtime=idt, member=imdl)
                pres3d = pres.sel(time=it, dtime=idt, member=imdl)
                u3d = u.sel(time=it, dtime=idt, member=imdl)
                v3d = v.sel(time=it, dtime=idt, member=imdl)

                thta3d = utl.stda_to_quantity(thta3d) # degC
                pres3d = utl.stda_to_quantity(pres3d) # hPa
                u3d = utl.stda_to_quantity(u3d) # m/s
                v3d = utl.stda_to_quantity(v3d) # m/s

                pv3d = mpcalc.potential_vorticity_baroclinic(thta3d, pres3d, u3d, v3d, dx, dy, lats)
                pv.loc[dict( time=it, dtime=idt, member=imdl)] = np.array(pv3d)
                pv.attrs['var_units'] = str(pv3d.units)

    pv = utl.quantity_to_stda_byreference('pv', pv.values * units(pv.attrs['var_units']), thta)


    return pv


def divergence(u, v):
    '''

    [Calculate the horizontal divergence of a vector.]

    Arguments:
        u {[stda]} -- [x component of the vector]
        v {[stda]} -- [y component of the vector]

    Returns:
        [stda] -- [The horizontal divergence]
    '''
    u_p = utl.stda_to_quantity(u)  # m/s
    v_p = utl.stda_to_quantity(v)  # m/s

    lons = u['lon'].values
    lats = u['lat'].values

    dx, dy = mpcalc.lat_lon_grid_deltas(lons, lats)

    dx = dx[np.newaxis, np.newaxis, np.newaxis, np.newaxis, :, :]
    dy = dy[np.newaxis, np.newaxis, np.newaxis, np.newaxis, :, :]

    div_p = mpcalc.divergence(u_p, v_p, dx=dx, dy=dy)

    div = utl.quantity_to_stda_byreference('div', div_p, u)

    return div
