# -*- coding: utf-8 -*-

import numpy as np

from scipy import ndimage

import xarray as xr
import metpy.calc as mpcalc

from metdig.cal.lib import utility as utl

__all__ = [
    'dry_static_energy',
    'add_hgt_to_pres',
    'smooth_n_point',
    'gaussian_filter',
    'wind_components',
    'wind_direction',
    'wind_speed'
]


# def mean_pressure_weighted(pres,stda,hgt=None,bottom=None,depth=None):
#     """_summary_
#     Calculate pressure-weighted mean of an arbitrary variable through a layer.
#     Layer top and bottom specified in height or pressure.
#     Only functions on 1D profiles (not higher-dimension vertical cross sections or grids).
#     Args:
#         pres (stda): _description_
#         stda (stda): _description_
#         hgt (stda, optional): _description_. Defaults to None.
#         bottom (stda, optional): _description_. Defaults to None.
#         depth (stda, optional): _description_. Defaults to None.
#     """    

#     adv = xr.zeros_like(stda).copy()
#     for ilvl in stda['level'].values:
#         for it in stda['time'].values:
#             for idt in stda['dtime'].values:
#                 for imdl in stda['member'].values:
#                     u2d = u.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
#                     v2d = v.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
#                     var2d = var.sel(level=ilvl, time=it, dtime=idt, member=imdl).squeeze()
#                     u2d = utl.stda_to_quantity(u2d)
#                     v2d = utl.stda_to_quantity(v2d)
#                     var2d = utl.stda_to_quantity(var2d)
#                     adv2d = mpcalc.advection(var2d, u=u2d, v=v2d, dx=dx, dy=dy)
#                     adv.loc[dict(level=ilvl, time=it, dtime=idt, member=imdl)] = np.array(adv2d)
#                     adv.attrs['var_units'] = str(adv2d.units)
#     adv = utl.quantity_to_stda_byreference(var.attrs['var_name']+'adv', adv.values * units(adv.attrs['var_units']), u)



#     pres_p=pres.stda.quantity
#     stda_p=stda.stda.quantity
#     if(hgt is not None):
#         hgt=hgt.stda.quantity.squeeze()
#     if(bottom is not None):
#         bottom=bottom.stda.quantity.squeeze()
#     if(depth is not None):
#         depth=depth.stda.quantity.squeeze()     

#     var_output=mpcalc.mean_pressure_weighted(pres_p.squeeze(),stda_p.squeeze(),height=hgt.squeeze(),bottom=bottom,depth=depth)

#     print(hgt)
#     return

# if __name__ == '__main__':
#     import metdig
#     from datetime import datetime,timedelta
#     levs=[1000,925,850,700,500]
#     hgt=metdig.io.get_model_3D_grid(init_time=datetime(2022,3,2,20),fhour=24,var_name='hgt',levels=levs,
#         data_source='cassandra',data_name='ecmwf',extent=[100,120,10,20]).sel(lon=[115],lat=[15],method='nearest')
#     spfh=metdig.io.get_model_3D_grid(init_time=datetime(2022,3,2,20),fhour=24,var_name='spfh',levels=levs,
#         data_source='cassandra',data_name='ecmwf',extent=[100,120,10,20]).sel(lon=[115],lat=[15],method='nearest')

#     pres=metdig.utl.gridstda_full_like_by_levels(spfh,spfh['level'].values)
#     geohgt=mean_pressure_weighted(pres,spfh,hgt=hgt)
#     print(geohgt)
def pressure_to_height_std(pressure):
    #Convert pressure data to height using the U.S. standard atmosphere [NOAA1976].
    #The implementation uses the formula outlined in [Hobbs1977] pg.60-61.
    pressure_p=pressure.stda.quantity
    height_p=mpcalc.pressure_to_height_std(pressure_p)
    height=utl.quantity_to_stda_byreference('hgt', height_p, pressure)
    return height


def height_to_geopotential(hgt):
    """_summary_

    Args:
        hgt (stda): height
    """    
    hgt_p=hgt.stda.quantity
    geohgt_p=mpcalc.height_to_geopotential(hgt_p)
    geohgt=utl.quantity_to_stda_byreference('geohgt', geohgt_p, hgt)

    return geohgt

def geopotential_to_height(geohgt):
    """_summary_

    Args:
        geohgt (stda): geopotential height

    example:
        import metdig
        from datetime import datetime,timedelta
        levs=[1000,925,850,700,500]
        geohgt=metdig.io.get_model_3D_grid(init_time=datetime(2022,3,2,20),fhour=24,var_name='hgt',levels=levs,
            data_source='cassandra',data_name='ecmwf',extent=[100,120,10,20])
        geohgt.attrs['var_units']='m**2/s**2'
        hgt=geopotential_to_height(geohgt)

    Returns:
        _type_: _description_
    """
    geohgt_p=geohgt.stda.quantity
    hgt_p=mpcalc.geopotential_to_height(geohgt_p)
    hgt=utl.quantity_to_stda_byreference('hgt', hgt_p, geohgt)
    return hgt

def dry_static_energy(hgt,tmp):
    """_summary_

    Args:
        Parameters
        height (pint.Quantity) – Atmospheric height

        temperature (pint.Quantity) – Air temperature

    example:
        import metdig
        from datetime import datetime,timedelta
        levs=[1000,925,850,700,500]
        hgt=metdig.io.get_model_3D_grid(init_time=datetime(2022,3,2,20),fhour=24,var_name='hgt',levels=levs,
            data_source='cassandra',data_name='ecmwf',extent=[100,120,10,20])
        tmp=metdig.io.get_model_3D_grid(init_time=datetime(2022,3,2,20),fhour=24,var_name='tmp',levels=levs,
            data_source='cassandra',data_name='ecmwf',extent=[100,120,10,20])
        dry_static_energy(hgt,tmp)        
    """    
    hgt_p=hgt.stda.quantity
    tmp_p=tmp.stda.quantity
    drsteg_p=mpcalc.dry_static_energy(hgt_p,tmp_p)
    drsteg=utl.quantity_to_stda_byreference('drsteg', drsteg_p, tmp)
    return drsteg

def dry_lapse(pres,tmp,reference_pres=None,vertical_dim=0):
    """_summary_
    Calculate the temperature at a level assuming only dry processes.

    This function lifts a parcel starting at temperature, conserving potential temperature. The starting pressure can be given by reference_pressure.
    Args:
        Parameters
        pressure (stda) – Atmospheric pressure level(s) of interest

        temperature (stda) – Starting temperature

        reference_pressure (stda) – Reference pressure; if not given, it defaults to the first element of the pressure array.
        
    """    
    pres_p = pres.stda.quantity
    tmp_p = tmp.stda.quantity
    if(reference_pres is not None):
        reference_pres_p=reference_pres.stda.quantity
    tmp_p2 = mpcalc.dry_lapse(pres_p,tmp_p,reference_pres_p,vertical_dim=vertical_dim)
    tmp2=utl.quantity_to_stda_byreference('tmp', tmp_p2, tmp)
    return tmp2

def air_density(pres,tmp,mixr,**kwargs):
    """_summary_
        Calculate air parcel air_density.
        This calculation must be given an air parcel’s pressure, temperature, and mixing ratio. The implementation uses the formula outlined in [Hobbs2006] pg.67.
    Args:
        pres (_type_): _description_
        tmp (_type_): _description_
        mixr (_type_): _description_
    """
    pres_p = pres.stda.quantity
    tmp_p = tmp.stda.quantity
    mixr_p = mixr.stda.quantity
    density_p=mpcalc.density(pres_p,tmp_p,mixr_p,**kwargs)
    density=utl.quantity_to_stda_byreference('density', density_p, tmp)

    return density

def add_pres_to_hgt(hgt,pres):
    """_summary_
    'Calculate the height at a certain pressure above another height.'
    metpy.calc.add_pressure_to_height
    Args:
        pressure (stda): _description_
        height (stda): _description_
    """    
    pres_p = pres.stda.quantity
    hgt_p=hgt.stda.quantity
    addhgt_d=mpcalc.add_pressure_to_height(hgt_p,pres_p)
    addhgt = utl.quantity_to_stda_byreference('hgt', addhgt_d, hgt)
    
    return addhgt


def add_hgt_to_pres(pres,hgt):
    """_summary_
    'Calculate the pressure at a certain height above another pressure level.'
    metpy.calc.add_height_to_pressure
    Args:
        pressure (stda): _description_
        height (stda): _description_
    """    
    pres_p = pres.stda.quantity
    hgt_p=hgt.stda.quantity
    addpres_d=mpcalc.add_height_to_pressure(pres_p,hgt_p)
    addpres = utl.quantity_to_stda_byreference('pres', addpres_d, pres)
    
    return addpres


def smooth_n_point(stda_data, n=5, passes=1):
    '''
    see detail:
    metpy.calc.smooth_n_point
    '''
    result = stda_data.copy(deep=True)
    for a in range(result.coords['member'].size):
        for b in range(result.coords['level'].size):
            for c in range(result.coords['time'].size):
                for d in range(result.coords['dtime'].size):
                    scalar_grid = stda_data.values[a, b, c, d]
                    scalar_grid = mpcalc.smooth_n_point(scalar_grid, n=n, passes=passes)
                    result.values[a, b, c, d] = scalar_grid
    return result


def gaussian_filter(input_stda, sigma, order=0, output=None, mode='reflect', cval=0.0, truncate=4.0):
    '''
    see detail: 
    scipy.ndimage.gaussian_filter
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter.html
    '''
    result = input_stda.copy(deep=True)
    for a in range(result.coords['member'].size):
        for b in range(result.coords['level'].size):
            for c in range(result.coords['time'].size):
                for d in range(result.coords['dtime'].size):
                    scalar_grid = input_stda.values[a, b, c, d]
                    scalar_grid = ndimage.gaussian_filter(scalar_grid, sigma, order=order, output=output, mode=mode, cval=cval, truncate=truncate)
                    result.values[a, b, c, d] = scalar_grid
    return result


def wind_components(wsp, wdir):
    '''

    [Calculate the U, V wind vector components from the speed and direction.]

    Arguments:
        wsp {[stda]} -- [The wind speed (magnitude)]
        wdir {[stda]} -- [The wind direction, specified as the direction from which the wind is blowing (0-2 pi radians or 0-360 degrees), with 360 degrees being North.]

    Returns:
        [u, v (tuple of stda) ] -- [The wind components in the X (East-West) and Y (North-South) directions, respectively]
    '''
    wsp_p = utl.stda_to_quantity(wsp)  # m/s
    wdir_p = utl.stda_to_quantity(wdir)  # degree

    u_p, v_p = mpcalc.wind_components(wsp_p, wdir_p)  # m/s

    u = utl.quantity_to_stda_byreference('u', u_p, wsp)
    v = utl.quantity_to_stda_byreference('v', v_p, wsp)

    return u, v


def wind_direction(u, v):
    '''

    [Compute the wind speed from u and v-components.]

    Arguments:
        u {[stda]} -- [Wind component in the X (East-West) direction]
        v {[stda]} -- [Wind component in the Y (East-West) direction]

    Returns:
        [wind speed (stda)] -- [The speed of the wind]
    '''
    u_p = utl.stda_to_quantity(u)  # m/s
    v_p = utl.stda_to_quantity(v)  # m/s

    wdir_p = mpcalc.wind_direction(u_p, v_p)  # degree

    wdir = utl.quantity_to_stda_byreference('wdir', wdir_p, u)

    return wdir


def wind_speed(u, v):
    '''

    [Compute the wind speed from u and v-components.]

    Arguments:
        u {[stda]} -- [Wind component in the X (East-West) direction]
        v {[stda]} -- [Wind component in the Y (East-West) direction]

    Returns:
        [wind speed (stda)] -- [The speed of the wind]
    '''
    u_p = utl.stda_to_quantity(u)  # m/s
    v_p = utl.stda_to_quantity(v)  # m/s

    wsp_p = mpcalc.wind_speed(u_p, v_p)

    wsp = utl.quantity_to_stda_byreference('wsp', wsp_p, u)

    return wsp
