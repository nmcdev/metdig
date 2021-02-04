# -*- coding: utf-8 -*-

import numpy as np

import metpy.calc as mpcalc
from metpy.units import units as mpunits

from .lib import utility  as utl
import metdig.metdig_utl as mdgstda

def cal_snow_sleet_rain(rain_data, snow_data):
    sleet = rain_data.where(((rain_data - snow_data) > 0.1) & (snow_data > 0.1))
    sleet.attrs = mdgstda.get_stda_attrs(var_name='sleet')

    snow = rain_data.where(((rain_data - snow_data) < 0.1) & (snow_data > 0.1))
    snow.attrs = mdgstda.get_stda_attrs(var_name='snow')

    rain = rain_data.where((rain_data > 0.1) & (snow_data < 0.1))
    rain.attrs =mdgstda.get_stda_attrs(var_name='rain')

    return snow, sleet,  rain
