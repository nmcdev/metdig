# -*- coding: utf-8 -*-

'''

'''

import numpy as np
import xarray as xr
from numba import njit

import metpy.calc as mpcalc
from metpy.units import units

from metdig.cal.other import distance
from metdig.cal.lib import utility as utl
import metdig.utl.utl_stda_grid as utl_stda_grid
from metdig.cal.lib.utility import unifydim_stda, check_stda

__all__ = [
    'geostrophic_wind',
    'vertical_velocity_pressure',
    'vertical_velocity',
    'var_advect',
    'vorticity',
    'frontogenesis',
    'absolute_vorticity',
    'potential_vorticity_baroclinic',
    'divergence',
    'shear_vorticity',
    'storm_relative_helicity',
    'kinematic_flux',

]

@check_stda(['hgt'])
def geostrophic_wind(hgt):
    ug=hgt.copy()
    vg=hgt.copy()
    for ilvl in hgt['level'].values:
        for it in hgt['time'].values:
            for idt in hgt['dtime'].values:
                for imdl in hgt['member'].values:
                    hgt_pp = hgt.sel(level=ilvl,time=it,dtime=idt,member=imdl).stda.quantity
                    dx, dy = mpcalc.lat_lon_grid_deltas(hgt['lon'].values, hgt['lat'].values)
                    x, y = np.meshgrid(hgt['lon'].values, hgt['lat'].values)
                    y = y * units('degrees')
                    ug2d, vg2d = mpcalc.geostrophic_wind(hgt_pp,dx, dy,y)#,dx,dy,lat_2d*units('degree'))
                    # absv2d = mpcalc.absolute_vorticity(ug, vg, dx, dy, y)  # 绝对涡度  '1 / second'
                    ug.loc[dict(level=ilvl, time=it, dtime=idt, member=imdl)] = np.array(ug2d)
                    vg.loc[dict(level=ilvl, time=it, dtime=idt, member=imdl)] = np.array(vg2d)

    ug = utl.quantity_to_stda_byreference('ug', ug.values * vg2d.units, ug)
    vg = utl.quantity_to_stda_byreference('vg', vg.values *  ug2d.units, vg)
    return ug,vg

@check_stda(['w', 'tmp'])
@unifydim_stda(['w', 'tmp'])
def vertical_velocity_pressure(w, tmp, mir=0):
    '''

    [Calculate vvel from w assuming hydrostatic conditions.]

    Arguments:
        w  {[stda]} -- [ Vertical velocity in terms of height.]
        temperature {[stda]} -- [Air temperature.]
        mir {[stda]} -- [Mixing ratio of air. ]
    '''
    omega = utl.stda_to_quantity(w)
    temperature = utl.stda_to_quantity(tmp)
    pressure = utl_stda_grid.gridstda_full_like_by_levels(tmp, tmp.level.values.tolist())
    pressure = utl.stda_to_quantity(pressure)
    vvel = mpcalc.vertical_velocity_pressure(omega, pressure, temperature, mir)
    vvel = utl.quantity_to_stda_byreference('vvel', vvel, w)
    return vvel

@check_stda(['vvel', 'tmp'])
@unifydim_stda(['vvel', 'tmp'])
def vertical_velocity(vvel, tmp, mir=0):
    '''

    [Calculate w from omega assuming hydrostatic conditions.]

    Arguments:
        vvel {[stda]} -- [omega.]
        temperature {[stda]} -- [Air temperature.]
        mir {[stda]} -- [Mixing ratio of air. ]
    '''
    omega = utl.stda_to_quantity(vvel)
    temperature = utl.stda_to_quantity(tmp)
    pressure = utl_stda_grid.gridstda_full_like_by_levels(tmp, tmp.level.values.tolist())
    pressure = utl.stda_to_quantity(pressure)
    w = mpcalc.vertical_velocity(omega, pressure, temperature, mir)
    w = utl.quantity_to_stda_byreference('w', w, vvel)
    return w

@check_stda(['var', 'u', 'v'])
@unifydim_stda(['var', 'u', 'v'])
def var_advect(var, u, v):
    '''

    [Calculate the absolute vorticity of the horizontal wind.]

    Arguments:
        var {[stda]} -- [any variable.]
        u {[stda]} -- [x component of the wind.]
        v {[stda]} -- [y component of the wind. ]
    '''

    dx, dy = mpcalc.lat_lon_grid_deltas(u['lon'].values, u['lat'].values)
    adv = xr.zeros_like(u).copy()
    for ilvl in var['level'].values:
        for it in var['time'].values:
            for idt in var['dtime'].values:
                for imdl in var['member'].values:
                    u2d = u.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
                    v2d = v.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
                    var2d = var.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
                    u2d = utl.stda_to_quantity(u2d)
                    v2d = utl.stda_to_quantity(v2d)
                    var2d = utl.stda_to_quantity(var2d)
                    adv2d = mpcalc.advection(var2d, u=u2d, v=v2d, dx=dx, dy=dy)
                    adv.loc[dict(level=ilvl, time=it, dtime=idt, member=imdl)] = np.array(adv2d)
                    adv.attrs['var_units'] = str(adv2d.units)
    adv = utl.quantity_to_stda_byreference(var.attrs['var_name']+'adv', adv.values * units(adv.attrs['var_units']), u)
    return adv


@check_stda(['u', 'v'])
@unifydim_stda(['u', 'v'])
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


@check_stda(['thta', 'u', 'v'])
@unifydim_stda(['thta', 'u', 'v'])
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


@check_stda(['u', 'v'])
@unifydim_stda(['u', 'v'])
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


@check_stda(['thta', 'pres', 'u', 'v'])
@unifydim_stda(['thta', 'pres', 'u', 'v'])
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

                thta3d = utl.stda_to_quantity(thta3d)  # degC
                pres3d = utl.stda_to_quantity(pres3d)  # hPa
                u3d = utl.stda_to_quantity(u3d)  # m/s
                v3d = utl.stda_to_quantity(v3d)  # m/s

                pv3d = mpcalc.potential_vorticity_baroclinic(thta3d, pres3d, u3d, v3d, dx, dy, lats)
                pv.loc[dict(time=it, dtime=idt, member=imdl)] = np.array(pv3d)
                pv.attrs['var_units'] = str(pv3d.units)

    pv = utl.quantity_to_stda_byreference('pv', pv.values * units(pv.attrs['var_units']), thta)

    return pv


@check_stda(['u', 'v'])
@unifydim_stda(['u', 'v'])
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


@check_stda(['u', 'v'])
@unifydim_stda(['u', 'v'])
def shear_vorticity(u, v, fill_value=np.nan):
    '''

    [Calculate relative vorticity and its components shear and curvature on a regular lat-lon-grid.]

    Arguments:
        u {[stda]} -- [x component of the vector]
        v {[stda]} -- [y component of the vector]

    Returns:
        [stda] -- [vort: atmosphere_upward_relative_vorticity]
        [stda] -- [shear_vort: shear_component_of_atmosphere_upward_relative_vorticity]
        [stda] -- [curve_vort: curvature_component_atmosphere_upward_relative_vorticity]
    '''

    lons = u['lon'].values
    lats = u['lat'].values
    
    vort = xr.full_like(u, fill_value=fill_value, dtype=np.float64)
    shear_vort = xr.full_like(u, fill_value=fill_value, dtype=np.float64)
    curve_vort = xr.full_like(u, fill_value=fill_value, dtype=np.float64)

    for imember in u.member.values:
        for ilevel in u.level.values:
            for idtime in u.dtime.values:
                for itime in u.time.values:
                    _u_1d = u.sel(member=imember, level=ilevel, dtime=idtime, time=itime)
                    _v_1d = v.sel(member=imember, level=ilevel, dtime=idtime, time=itime)
                    _u_1d_p = utl.stda_to_quantity(_u_1d)  # m/s
                    _v_1d_p = utl.stda_to_quantity(_v_1d)  # m/s
                    _vor, _shear, _curve = __vorticity(np.asarray(_u_1d_p), np.asarray(_v_1d_p), lons, lats, fill_value)
                    vort.loc[dict(member=imember, level=ilevel, dtime=idtime, time=itime)] = _vor
                    shear_vort.loc[dict(member=imember, level=ilevel, dtime=idtime, time=itime)] = _shear
                    curve_vort.loc[dict(member=imember, level=ilevel, dtime=idtime, time=itime)] = _curve
    
    vort = utl.quantity_to_stda_byreference('vort', vort.values * units('1/s'), u)
    shear_vort = utl.quantity_to_stda_byreference('shear_vort', shear_vort.values * units('1/s'), u)
    curve_vort = utl.quantity_to_stda_byreference('curve_vort', curve_vort.values * units('1/s'), u)

    return vort, shear_vort, curve_vort

@njit()
def __vorticity(u, v, lon, lat, fill_value):
    vor = np.zeros_like(u, dtype=np.float64)
    shear = np.zeros_like(u, dtype=np.float64)
    curve = np.zeros_like(u, dtype=np.float64)
    v1 = np.zeros(2)
    v2 = np.zeros(2)

    # loop over all grid points
    for y in range(1, u.shape[0]-1):
        for x in range(1, u.shape[1]-1):
            # any missing values?
            if np.isnan(u[y,x]) or np.isnan(u[y,x+1]) or np.isnan(u[y,x-1]) \
                or np.isnan(u[y+1,x]) or np.isnan(u[y-1,x]) \
                or np.isnan(v[y,x]) or np.isnan(v[y,x+1]) or np.isnan(v[y,x-1]) \
                or np.isnan(v[y+1,x]) or np.isnan(v[y-1,x]):
                vor[y,x] = np.NaN
                shear[y,x] = np.NaN
                curve[y,x] = np.NaN
            
            # distance on globe
            dx = distance(lat[y], lat[y], lon[x+1], lon[x-1], input_in_radian=False)
            dy = distance(lat[y-1], lat[y+1], lon[x], lon[x], input_in_radian=False)
            vor[y,x] = (v[y,x+1]-v[y,x-1]) / dx - (u[y+1,x]-u[y-1,x]) / dy

            # calculate shear-vorticity
            # calculate the wind direction
            wdir = np.arctan2(u[y,x], v[y,x])
            wspd = np.sqrt(u[y,x]**2 + v[y,x]**2)
            sin_wdir = np.sin(wdir)
            cos_wdir = np.cos(wdir)

            # calculate dot-product for four points around the reference point to the reference vector.
            # Use the wind component parallel to the reference vector from all four points and calculate
            # the vorticity based on this component, which results in the shear vorticity.
            #
            # This approach follows Berry et al. 2006.
            # Points:
            #    c
            #  b r a
            #    d

            # point a
            v1[0] = u[y,x]
            v1[1] = v[y,x]
            v2[0] = u[y,x+1]
            v2[1] = v[y,x+1]
            dp = np.dot(v1, v2) / wspd
            v_a = dp * cos_wdir

            # point b
            v2[0] = u[y,x-1]
            v2[1] = v[y,x-1]
            dp = np.dot(v1, v2) / wspd
            v_b = dp * cos_wdir

            # point c
            v2[0] = u[y+1,x]
            v2[1] = v[y+1,x]
            dp = np.dot(v1, v2) / wspd
            u_c = dp * sin_wdir

            # point d 
            v2[0] = u[y-1,x]
            v2[1] = v[y-1,x]
            dp = np.dot(v1, v2) / wspd
            u_d = dp * sin_wdir

            # calculate the shear vorticity
            shear[y,x] = (v_a-v_b) / dx - (u_c-u_d) / dy
    
    # fill values at the borders
    vor[0,:] = np.NaN
    vor[-1,:] = np.NaN
    vor[:,0] = np.NaN
    vor[:,-1] = np.NaN
    
    shear[0,:] = np.NaN
    shear[-1,:] = np.NaN
    shear[:,0] = np.NaN
    shear[:,-1] = np.NaN
    
    # calculate curvature-vorticity 
    curve = np.where(np.logical_or(np.isnan(vor), np.isnan(shear)), np.NaN, vor-shear)

    # replace fill values if something different from NaN is used
    if not np.isnan(fill_value):
        vor = np.where(np.isnan(vor), fill_value, vor)
        shear = np.where(np.isnan(shear), fill_value, shear)
        curve = np.where(np.isnan(curve), fill_value, curve)
    return vor, shear, curve

@check_stda(['hgt', 'u', 'v'])
@unifydim_stda(['hgt', 'u', 'v'])
def storm_relative_helicity(hgt, u, v, depth, bottom=None, storm_u=None, storm_v=None):
    """Calculate storm relative helicity.（螺旋度）

    Calculates storm relative helicity following [Markowski2010]_ pg.230-231

    Args:
        hgt (stda): _description_
        u (stda): _description_
        v (stda): _description_
        depth (float or int): Depth of the layer (unit: km)
        bottom (float or int, optional): Height of layer bottom AGL (default is surface). Defaults to None.
        storm_u (float or int, optional): U component of storm motion (default is 0 m/s). Defaults to None.
        storm_v (float or int, optional): V component of storm motion (default is 0 m/s). Defaults to None.

    Returns:
        [stda] -- [Positive storm-relative helicity]
        [stda] -- [Negative storm-relative helicity]
        [stda] -- [Total storm-relative helicity]
    """
    hgt_p = hgt.stda.quantity
    u_p = u.stda.quantity
    v_p = v.stda.quantity

    positive_srh, negative_srh, total_srh = mpcalc.storm_relative_helicity(hgt_p, u_p, v_p, depth * units('km'), bottom=bottom, storm_u=storm_u, storm_v=storm_v)
    
    return positive_srh, negative_srh, total_srh



@check_stda(['vel', 'b'])
@unifydim_stda(['vel', 'v'])
def kinematic_flux(vel, b, axes, perturbation=False):
    """扰动通量，通用函数，注：可以计算动能收支
    Compute the kinematic flux from two time series.

    Compute the kinematic flux from the time series of two variables `vel`
    and b. Note that to be a kinematic flux, at least one variable must be
    a component of velocity.

    Args:
        vel (stda): A component of velocity
        b (stda): May be a component of velocity or a scalar variable (e.g. Temperature)
        axes (str): The index of the time axis, along which the calculations will be
           performed，e.g. 'member', 'level', 'time', 'dtime', 'lat', 'lon'
        perturbation (bool, optional): `True` if the `vel` and `b` variables are perturbations. If `False`, perturbations
            will be calculated by removing the mean value from each variable. Defaults to `False`. Defaults to False.

    Returns:
        stda: _description_
    """
    vel_p = vel.stda.quantity
    b_p = b.stda.quantity

    stda_axes = ['member', 'level', 'time', 'dtime', 'lat', 'lon']
    axis = stda_axes.index(axes)

    kf_p = mpcalc.kinematic_flux(vel_p, b_p, perturbation=perturbation, axis=axis)
    kf_p = np.expand_dims(kf_p, axis=axis)

    kf = vel.isel({axes: [0]}) # 上述计算内部对axis这一维度平均计算，用第一个值代替这一维保证stda维度完整
    kf.name = 'data'
    kf.values = kf_p.magnitude
    kf.attrs['var_name'] = 'kinematic_flux'
    kf.attrs['var_cn_name'] = ''
    kf.attrs['var_units'] = str(kf_p.units)
    return kf