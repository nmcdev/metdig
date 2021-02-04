# -*- coding: utf-8 -*-

'''

'''


import numpy as np

import metpy.calc as mpcalc
from metpy.units import units

from .lib import utility as utl


def absolute_vorticity(u, v):
    '''

    [Calculate the absolute vorticity of the horizontal wind.]

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


def divergence(u, v, dim_order=None):
    '''

    [Calculate the horizontal divergence of a vector.]

    Arguments:
        u {[stda]} -- [x component of the vector]
        v {[stda]} -- [y component of the vector]

    Keyword Arguments:
        dim_order {[str or None, optional]} -- [The ordering of dimensions in passed in arrays. 
            Can be one of None, 'xy', or 'yx'. 
            'xy' indicates that the dimension corresponding to x is the leading dimension, followed by y. 
            'yx' indicates that x is the last dimension, preceded by y. None indicates 
            that the default ordering should be assumed, which is ‘yx’. 
            Can only be passed as a keyword argument, i.e. func(…, dim_order=’xy’)] (default: {None})

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

    div_p = mpcalc.divergence(u_p, v_p, dx, dy, dim_order=dim_order)

    div = utl.quantity_to_stda_byreference('div', div_p, u)

    return div
