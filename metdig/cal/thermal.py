# -*- coding: utf-8 -*-

import numpy as np
import math

import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units

from metdig.cal.lib import utility as utl
import metdig.utl as mdgstda
from metdig.cal.lib.utility import unifydim_stda, check_stda

__all__ = [
    'potential_temperature',
    'equivalent_potential_temperature',
    'apparent_temperature',
    'dry_static_energy',
    'moist_static_energy',
]


@check_stda(['pres', 'tmp'])
@unifydim_stda(['pres', 'tmp'])
def potential_temperature(pres, tmp):
    '''

    [Calculate the potential temperature.

    Uses the Poisson equation to calculation the potential temperature given pressure and temperature]

    Arguments:
        pres {[stda]} -- [total atmospheric pressure]
        tmp {[stda]} -- [air temperature]
    '''
    pres_p = utl.stda_to_quantity(pres)  # hPa
    tmp_p = utl.stda_to_quantity(tmp)  # degC

    thta_p = mpcalc.potential_temperature(pres_p, tmp_p)  # kelvin

    thta = utl.quantity_to_stda_byreference('thta', thta_p, tmp)  # degC

    return thta

@check_stda(['pres', 'tmp'])
@unifydim_stda(['pres', 'tmp'])
def saturation_equivalent_potential_temperature(pres, tmp):
    '''

    [Calculate equivalent potential temperature.]

    Arguments:
        pres {[stda]} -- [Total atmospheric pressure]
        tmp {[stda]} -- [temperature of parcel]

    Returns:
        [stda] -- [The equivalent potential temperature of the parcel]
    '''
    pres_p = utl.stda_to_quantity(pres)  # hPa
    tmp_p = utl.stda_to_quantity(tmp)  # degC

    thetaes_p = mpcalc.saturation_equivalent_potential_temperature(pres_p, tmp_p)  # kelvin

    thetaes = utl.quantity_to_stda_byreference('thetaes', thetaes_p, tmp)  # kelvin

    return thetaes

if __name__=='__main__':
    import metdig
    from datetime import datetime
    import metdig.utl.utl_stda_grid as utl_stda_grid
    tmp=metdig.io.get_model_grids(init_time=datetime(2022,1,7,8),fhours=[12,18],
                            data_source='cassandra',data_name='ecmwf',var_name='tmp',level=500)
    pressure = utl_stda_grid.gridstda_full_like_by_levels(tmp, tmp.level.values.tolist())
    thetaes=saturation_equivalent_potential_temperature(pressure,tmp)
    print(thetaes)

@check_stda(['pres', 'tmp', 'td'])
@unifydim_stda(['pres', 'tmp', 'td'])
def equivalent_potential_temperature(pres, tmp, td):
    '''

    [Calculate equivalent potential temperature.]

    Arguments:
        pres {[stda]} -- [Total atmospheric pressure]
        tmp {[stda]} -- [temperature of parcel]
        td {[stda]} -- [dewpoint of parcel]

    Returns:
        [stda] -- [The equivalent potential temperature of the parcel]
    '''
    pres_p = utl.stda_to_quantity(pres)  # hPa
    tmp_p = utl.stda_to_quantity(tmp)  # degC
    td_p = utl.stda_to_quantity(td)  # degC

    theta_p = mpcalc.equivalent_potential_temperature(pres_p, tmp_p, td_p)  # kelvin

    theta = utl.quantity_to_stda_byreference('theta', theta_p, tmp)  # kelvin

    return theta


@check_stda(['tmp', 'wsp', 'p_vapor'])
@unifydim_stda(['tmp', 'wsp', 'p_vapor'])
def apparent_temperature(tmp, wsp, p_vapor):
    '''

    [计算体感温度]

    Arguments:
        tmp {[stda]} -- [temperature]
        wsp {[stda]} -- [wind speed]
        p_vapor {[stda]} -- [水汽压]

    Returns:
        [stda] -- [体感温度]
    '''
    tmp_p = utl.stda_to_quantity(tmp)  # degC
    wsp_p = utl.stda_to_quantity(wsp)  # m/s
    p_vapor_p = utl.stda_to_numpy(p_vapor)

    tmp_p = np.array(tmp_p)
    wsp_p = np.array(wsp_p)

    at_p = (1.07 * tmp_p + 0.2 * p_vapor_p - 0.65 * wsp_p - 2.7)*units('degC')  # 体感温度

    at = utl.quantity_to_stda_byreference('at', at_p, tmp)

    return at


@check_stda(['hgt', 'tmp'])
@unifydim_stda(['hgt', 'tmp'])
def dry_static_energy(hgt,tmp):
    """Calculate the dry static energy of parcels.

    This function will calculate the dry static energy following the first two terms of
    equation 3.72 in [Hobbs2006]_.

    Args:
        Parameters
        height (stda) – Atmospheric height

        temperature (stda) – Air temperature

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
    hgt_p = hgt.stda.quantity
    tmp_p = tmp.stda.quantity
    drsteg_p = mpcalc.dry_static_energy(hgt_p, tmp_p)
    drsteg = utl.quantity_to_stda_byreference('drsteg', drsteg_p, tmp)
    return drsteg


@check_stda(['hgt', 'tmp', 'spfh'])
@unifydim_stda(['hgt', 'tmp', 'spfh'])
def moist_static_energy(hgt,tmp, sfph):
    """Calculate the moist static energy of parcels.

    This function will calculate the moist static energy following
    equation 3.72 in [Hobbs2006]_.

    Args:
        Parameters
        height (stda) – Atmospheric height

        temperature (stda) – Air temperature

        sfph (stda) – specific_humidity
      
    """    
    hgt_p = hgt.stda.quantity
    tmp_p = tmp.stda.quantity
    spfh_p = sfph.stda.quantity
    mosteg_p = mpcalc.moist_static_energy(hgt_p, tmp_p, spfh_p)
    mosteg = utl.quantity_to_stda_byreference('mosteg', mosteg_p, tmp)
    return mosteg