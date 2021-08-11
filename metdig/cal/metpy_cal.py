'''
metpy.cal所有方法，先在本py中补充，后续将移到cal层
https://unidata.github.io/MetPy/latest/api/generated/metpy.calc
原则：
1. 参数名使用stda要素名
2. 计算时需要包含stda各个维度
3. 不区分站点网格型stda，如果某个函数只支持站点或者网格，请在函数说明中标注
4. 参数需尽量保持为stda，如果不是，请在参数说明中标注
5，如果某些函数不适应于stda，则先空着不写
6，优先做要素计算相关方法
'''


import numpy as np
import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units
from metpy import constants as mpconsts

from metdig.cal.lib import utility as utl


def add_height_to_pressure(pres, height):
    '''

    [Calculate the pressure at a certain height above another pressure level. 

    This assumes a standard atmosphere [NOAA1976].]

    Args:
        pres {[stda]} -- [Pressure level]
        height {[stda]} -- [Height above a pressure level]

    Returns:
        [stda]: [Corresponding pressure value for the height above the pressure level]
    '''


def add_pressure_to_height(height, pres):
    '''

    [Calculate the height at a certain pressure above another height. 

    This assumes a standard atmosphere [NOAA1976].]

    Args:
        height {[stda]} -- [Height leve]
        pres {[stda]} -- [Pressure above height level]

    Returns:
        [stda]: [The corresponding height value for the pressure above the height level]
    '''


def density(pres, tmp, mixing_ratio):
    '''

    [Calculate density. 

    This calculation must be given an air parcel’s pressure, temperature, and mixing ratio. 
    The implementation uses the formula outlined in [Hobbs2006] pg.67.]

    Args:
        pres {[stda]} -- [Total atmospheric pressure]
        tmp {[stda]} -- [Air temperature]
        mixing_ratio {[stda]} -- [Mass mixing ratio (dimensionless)]

    Returns:
        [stda]: [Corresponding density of the parcel]
    '''


def dry_lapse(pres, tmp, reference_pres=None):
    '''

    [Calculate the temperature at a level assuming only dry processes.

    This function lifts a parcel starting at temperature, conserving potential temperature. 
    The starting pressure can be given by reference_pressure.]

    Args:
        pres {[stda]} -- [Atmospheric pressure level(s) of interest]
        tmp {[stda]} -- [Starting temperature]
        reference_pres {[stda]} -- [Reference pressure; if not given, it defaults to the first element of the pressure array.]

    Returns:
        [stda]: [The parcel’s resulting temperature at levels given by pressure]
    '''


def dry_static_energy(height, tmp):
    '''

    [Calculate the dry static energy of parcels.

    This function will calculate the dry static energy following the first two terms of equation 3.72 in [Hobbs2006].]

    Args:
        height {[stda]} -- [Atmospheric height]
        tmp {[stda]} -- [Air temperature]

    Returns:
        [stda]: [Dry static energy]
    '''


def geopotential_to_height(hgt):
    '''

    [Compute height above sea level from a given geopotential.

    Calculates the height above mean sea level from geopotential using the following formula,
    which is derived from the definition of geopotential as given in [Hobbs2006]_ Pg. 69 Eq
    3.21, along with an approximation for variation of gravity with altitude:

    .. math:: z = \frac{\Phi R_e}{gR_e - \Phi}

    (where :math:`\Phi` is geopotential, :math:`z` is height, :math:`R_e` is average Earth
    radius, and :math:`g` is standard gravity).]

    Args:
        hgt {[stda]} -- [Geopotential]

    Returns:
        [stda]: [Corresponding value(s) of height above sea level]
    '''


def height_to_geopotential(height):
    '''

    [Compute geopotential for a given height above sea level.

    Calculates the geopotential from height above mean sea level using the following formula,
    which is derived from the definition of geopotential as given in [Hobbs2006]_ Pg. 69 Eq
    3.21, along with an approximation for variation of gravity with altitude:

    .. math:: \Phi = \frac{g R_e z}{R_e + z}

    (where :math:`\Phi` is geopotential, :math:`z` is height, :math:`R_e` is average Earth
    radius, and :math:`g` is standard gravity).]

    Args:
        height {[stda]} -- [Height above sea level]

    Returns:
        [stda]: [Corresponding geopotential value(s)]
    '''


def mean_pressure_weighted(pres, *args, height=None, bottom=None, depth=None):
    '''

    [Calculate pressure-weighted mean of an arbitrary variable through a layer.

    Layer top and bottom specified in height or pressure.]

    Args:
        pres {[stda]} -- [Atmospheric pressure profile]
        args {[stda]} -- [Parameters for which the pressure-weighted mean is to be calculated]
        height {[stda]} -- [Heights from sounding. Standard atmosphere heights assumed (if needed) if no heights are given]
        bottom {[stda]} -- [The bottom of the layer in either the provided height coordinate
                            or in pressure. Don't provide in meters AGL unless the provided
                            height coordinate is meters AGL. Default is the first observation,
                            assumed to be the surface.]
        depth {[stda]} -- [Depth of the layer in meters or hPa]

    Returns:
        [stda]: [list of layer mean value for each profile in args]
    '''


def sigma_to_pressure(sigma, pres_sfc, pres_top):
    '''

    [Calculate pressure from sigma values.]

    Args:
        sigma {[stda]} -- [Sigma levels to be converted to pressure levels]
        pres_sfc {[stda]} -- [Surface pressure value]
        pres_top {[stda]} -- [Pressure value at the top of the model domain]

    Returns:
        [stda]: [Pressure values at the given sigma levels]
    '''


def static_stability(pres, tmp, vertical_dim=0):
    '''

    [Calculate the static stability within a vertical profile.

    .. math:: \sigma = -\frac{RT}{p} \frac{\partial \ln \theta}{\partial p}

    This formula is based on equation 4.3.6 in [Bluestein1992]_.]

    Args:
        pres {[stda]} -- [Profile of atmospheric pressure]
        tmp {[stda]} -- [Profile of temperature]
        vertical_dim {[int]} -- [The axis corresponding to vertical in the pressure and temperature arrays, defaults to 0]

    Returns:
        [stda]: []
    '''


def temperature_from_potential_temperature(pres, thta):
    '''

    [Calculate the temperature from a given potential temperature.

    Uses the inverse of the Poisson equation to calculate the temperature from a given potential temperature at a specific pressure level.]

    Args:
        pres {[stda]} -- [Total atmospheric pressure]
        thta {[stda]} -- [Potential temperature]

    Returns:
        [stda]: [Temperature corresponding to the potential temperature and pressure]
    '''


def thickness_hydrostatic(pres, tmp, mixing_ratio=None,
                          molecular_weight_ratio=mpconsts.epsilon, bottom=None, depth=None):
    '''

    [Calculate the thickness of a layer via the hypsometric equation.

    This thickness calculation uses the pressure and temperature profiles (and optionally
    mixing ratio) via the hypsometric equation with virtual temperature adjustment.

    .. math:: Z_2 - Z_1 = -\frac{R_d}{g} \int_{p_1}^{p_2} T_v d\ln p,

    Which is based off of Equation 3.24 in [Hobbs2006]_.

    This assumes a hydrostatic atmosphere. Layer bottom and depth specified in pressure.]

    Args:
        pres {[stda]} -- [Atmospheric pressure profile]
        tmp {[stda]} -- [Atmospheric temperature profile]
        mixing_ratio {[stda, optional]} -- [Profile of dimensionless mass mixing ratio. 
                                            If none is given, virtual temperature is simply set to be the given temperature]
        molecular_weight_ratio {[stda or float, optional]} -- [The ratio of the molecular weight of the constituent gas to that assumed for air. 
                                                               Defaults to the ratio for water vapor to dry air. (ϵ≈0.622)]
        bottom {[stda, optional]} -- [The bottom of the layer in pressure. Defaults to the first observation.]
        depth {[stda, optional]} -- [The depth of the layer in hPa. Defaults to the full profile if bottom is not given, and 100 hPa if bottom is given.]

    Returns:
        [stda]: [The thickness of the layer in meters]
    '''


def dewpoint(vapor_pressure):
    '''

    [Calculate the ambient dewpoint given the vapor pressure.

    This function inverts the [Bolton1980] formula for saturation vapor pressure to instead calculate the temperature.
    .. math:: T = \frac{243.5 log(e / 6.112)}{17.67 - log(e / 6.112)]

    Args:
        vapor_pressure {[stda]} -- [ Water vapor partial pressure]

    Returns:
        [stda]: [Dewpoint temperature]
    '''


def mixing_ratio(partial_press, total_press, molecular_weight_ratio=mpconsts.epsilon):
    '''

    [Calculate the mixing ratio of a gas.

    This calculates mixing ratio given its partial pressure and the total pressure of the air. 
    There are no required units for the input arrays, other than that they have the same units.]

    Args:
        partial_press {[stda]} -- [Partial pressure of the constituent gas]
        total_press {[stda]} -- [Total air pressure]
        molecular_weight_ratio {[stda or float]} -- [The ratio of the molecular weight of the constituent gas to that assumed for air. 
                                                     Defaults to the ratio for water vapor to dry air (ϵ≈0.622).]

    Returns:
        [stda]: [The (mass) mixing ratio, dimensionless (e.g. Kg/Kg or g/g)]
    '''


def mixing_ratio_from_relative_humidity(pres, tmp, rh):
    '''

    [Calculate the mixing ratio from relative humidity, temperature, and pressure.]

    Args:
        pres {[stda]} -- [Total atmospheric pressure]
        tmp {[stda]} -- [Air temperature]
        rh {[stda]} -- [The relative humidity expressed as a unitless ratio in the range [0, 1]. Can also  a percentage if proper units are attached.]

    Returns:
        [stda]: [Mixing ratio (dimensionless)]
    '''


def mixing_ratio_from_specific_humidity(spfh):
    '''

    [Calculate the mixing ratio from specific humidity]

    Args:
        spfh {[stda]} -- [Specific humidity of air]

    Returns:
        [stda]: [Mixing ratio]
    '''


def moist_lapse(pres, tmp, reference_pressure=None):
    '''

    [Calculate the temperature at a level assuming liquid saturation processes.

    This function lifts a parcel starting at temperature. The starting pressure can be given by reference_pressure. 
    Essentially, this function is calculating moist pseudo-adiabats.]

    Args:
        pres {[stda]} -- [Atmospheric pressure level(s) of interest]
        tmp {[stda]} -- [Starting temperature]
        reference_pressure {[stda]} -- [Reference pressure; if not given, it defaults to the first element of the pressure array.]

    Returns:
        [stda]: [The resulting parcel temperature at levels given by pressure]
    '''


def moist_static_energy(height, tmp, spfh):
    '''

    [Calculate the moist static energy of parcels.

    This function will calculate the moist static energy following equation 3.72 in [Hobbs2006].]

    Args:
        height {[stda]} -- [Atmospheric height]
        tmp {[stda]} -- [Air temperature]
        spfh {[stda]} -- [Atmospheric specific humidity]

    Returns:
        [stda]: [Moist static energy]
    '''


def precipitable_water(pres, td, *, bottom=None, top=None):
    '''

    [Calculate precipitable water through the depth of a sounding.]

    Args:
        pres {[stda]} -- [Atmospheric pressure profile]
        td {[stda]} -- [Atmospheric dewpoint profile]
        bottom {[stda]} -- [Bottom of the layer, specified in pressure. Defaults to None (highest pressure).]
        top {[stda]} -- [Top of the layer, specified in pressure. Defaults to None (lowest pressure).]

    Returns:
        [stda]: [Precipitable water in the layer]
    '''


def psychrometric_vapor_pressure_wet(pres, dry_bulb_temperature, wet_bulb_temperature, psychrometer_coefficient=None):
    '''
    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def relative_humidity_from_dewpoint(tmp, td):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def relative_humidity_from_mixing_ratio(pres, tmp, mixing_ratio):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def relative_humidity_from_specific_humidity(pres, tmp, spfh):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def relative_humidity_wet_psychrometric(pres, dry_bulb_temperature, wet_bulb_temperature, **kwargs):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def saturation_equivalent_potential_temperature(pres, tmp):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def saturation_mixing_ratio(total_pres, tmp):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def saturation_vapor_pressure(tmp):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def specific_humidity_from_mixing_ratio(mixing_ratio):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def thickness_hydrostatic_from_relative_humidity(pres, tmp, rh, bottom=None, depth=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def vapor_pressure(pres, mixing_ratio):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def vertical_velocity_pressure(w, pres, tmp, mixing_ratio=0):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def virtual_potential_temperature(pres, tmp, mixing_ratio,
                                  molecular_weight_ratio=mpconsts.epsilon):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def virtual_temperature(tmp, mixing_ratio, molecular_weight_ratio=mpconsts.epsilon):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def wet_bulb_temperature(pres, tmp, td):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def bulk_shear(pres, u, v, height=None, bottom=None, depth=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def bunkers_storm_motion(pres, u, v, height):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def cape_cin(pres, tmp, td, parcel_profile, which_lfc='bottom',
             which_el='top'):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def critical_angle(pres, u, v, height, u_storm, v_storm):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def el(pres, tmp, dewpoint, parcel_temperature_profile=None, which='top'):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def lfc(pres, tmp, td, parcel_temperature_profile=None, dewpoint_start=None, which='top'):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def lifted_index(pres, tmp, parcel_profile):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def mixed_layer(pres, *args, height=None, bottom=None, depth=None, interpolate=True):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def mixed_layer_cape_cin(pres, tmp, dewpoint, **kwargs):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def mixed_parcel(pres, tmp, td, parcel_start_pressure=None, height=None, bottom=None, depth=None, interpolate=True):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def most_unstable_cape_cin(pres, tmp, td, **kwargs):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def most_unstable_parcel(pres, tmp, td, height=None, bottom=None, depth=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def parcel_profile(pres, tmp, td):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def parcel_profile_with_lcl(pres, tmp, td):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def parcel_profile_with_lcl_as_dataset(pres, tmp, td):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def significant_tornado(sbcape, surface_based_lcl_height, storm_helicity_1km, shear_6km):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def storm_relative_helicity(height, u, v, depth, *, bottom=None, storm_u=None, storm_v=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def supercell_composite(mucape, effective_storm_helicity, effective_shear):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def surface_based_cape_cin(pres, tmp, td):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def absolute_momentum(u, v, index='index'):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def advection(scalar, u=None, v=None, w=None, *, dx=None, dy=None, dz=None, x_dim=- 1, y_dim=- 2, vertical_dim=- 3):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def ageostrophic_wind(height, u, v, dx=None, dy=None, latitude=None, x_dim=-1, y_dim=-2):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def coriolis_parameter(lat):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def exner_function(pres, reference_pressure=mpconsts.P0):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def geostrophic_wind(height, dx=None, dy=None, latitude=None, x_dim=-1, y_dim=-2):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def inertial_advective_wind(u, v, u_geostrophic, v_geostrophic, dx=None, dy=None, lat=None, x_dim=-1, y_dim=-2):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def kinematic_flux(vel, b, perturbation=False, axis=-1):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def montgomery_streamfunction(height, tmp):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def potential_vorticity_baroclinic(potential_temperature, pres, u, v, dx=None, dy=None, latitude=None, x_dim=-1, y_dim=-2, vertical_dim=-3):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def potential_vorticity_barotropic(height, u, v, dx=None, dy=None, lat=None, x_dim=-1, y_dim=-2):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def q_vector(u, v, tmp, pres, dx=None, dy=None, static_stability=1, x_dim=-1, y_dim=-2):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def shearing_deformation(u, v, dx=None, dy=None, x_dim=-1, y_dim=-2):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def stretching_deformation(u, v, dx=None, dy=None, x_dim=-1, y_dim=-2):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def total_deformation(u, v, dx=None, dy=None, x_dim=-1, y_dim=-2):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def brunt_vaisala_frequency(height, potential_temperature, vertical_dim=0):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def brunt_vaisala_frequency_squared(height, potential_temperature, vertical_dim=0):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def brunt_vaisala_period(height, potential_temperature, vertical_dim=0):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def friction_velocity(u, w, v=None, perturbation=False, axis=-1):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def gradient_richardson_number(height, potential_temperature, u, v, vertical_dim=0):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def tke(u, v, w, perturbation=False, axis=-1):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def first_derivative(f, axis=None, x=None, delta=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def gradient(f, axes=None, coordinates=None, deltas=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def laplacian(f, axes=None, coordinates=None, deltas=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def lat_lon_grid_deltas(lon, lat, x_dim=-1, y_dim=-2, geod=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def normal_component(data_x, data_y, index='index'):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def second_derivative(f, axis=None, x=None, delta=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def tangential_component(data_x, data_y, index='index'):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def unit_vectors_from_cross_section(cross, index='index'):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def apparent_temperature(tmp, rh, wsp, face_level_winds=False, mask_undefined=True):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def heat_index(tmp, rh, mask_undefined=True):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def windchill(tmp, wsp, face_level_winds=False, mask_undefined=True):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def altimeter_to_sea_level_pressure(altimeter_value, height, tmp):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def altimeter_to_station_pressure(altimeter_value, height):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def height_to_pressure_std(height):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def pressure_to_height_std(pres):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def smooth_gaussian(scalar_grid, n):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def smooth_window(scalar_grid, window, es=1, normalize_weights=True):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def smooth_rectangular(scalar_grid, size, es=1):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def smooth_circular(scalar_grid, radius, es=1):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def angle_to_direction(input_angle, full=False, level=3):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def azimuth_range_to_lat_lon(azimuths, ranges, center_lon, center_lat, geod=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def find_bounding_indices(arr, values, axis, from_below=True):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def find_intersections(x, a, b, direction='all', log_x=False):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def get_layer(pres, *args, height=None, bottom=None, depth=None, interpolate=True):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def get_layer_heights(height, depth, *args, bottom=None, interpolate=True, with_agl=False):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def get_perturbation(ts, axis=- 1):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def isentropic_interpolation(levels, pres, tmp, *args, vertical_dim=0,
                             temperature_out=False, max_iters=50, eps=1e-6,
                             bottom_up_search=True, **kwargs):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def isentropic_interpolation_as_dataset(levels, tmp, *args, max_iters=50, eps=1e-06, bottom_up_search=True):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def nearest_intersection_idx(a, b):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def parse_angle(input_dir):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def reduce_point_density(points, radius, priority=None):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''


def resample_nn_1d(a, centers):
    '''

    []

    Args:
         {[stda]} -- []
         {[stda]} -- []
         {[stda]} -- []

    Returns:
        [stda]: []
    '''
