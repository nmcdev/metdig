# -*- coding: utf-8 -*-

import numpy as np
import math

import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units

from .lib import utility as utl
import metdig.utl as mdgstda

__all__ = [
    'lcl',
    'parcel_profile',
]


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
