# -*- coding: utf-8 -*-

import numpy as np

import metpy.calc as mpcalc
from metpy.units import units as mpunits

from metdig.cal.lib import utility as utl
import metdig.utl as mdgstda
from metdig.cal.lib.utility import unifydim_stda, check_stda

__all__ = [
    'cal_snow_sleet_rain',
]


@check_stda(['rain_data', 'snow_data'])
@unifydim_stda(['rain_data', 'snow_data'])
def cal_snow_sleet_rain(rain_data, snow_data):
    sleet = rain_data.where(((rain_data - snow_data) > 0.1) & (snow_data > 0.1))
    sleet.attrs = mdgstda.get_stda_attrs(var_name='sleet',valid_time=rain_data.attrs['valid_time'],data_source=snow_data.attrs['data_source'],level_type=snow_data.attrs['level_type'])

    snow = rain_data.where(((rain_data - snow_data) < 0.1) & (snow_data > 0.1))
    snow.attrs = mdgstda.get_stda_attrs(var_name='snow',valid_time=snow_data.attrs['valid_time'],snow_data=snow.attrs['data_source'],level_type=snow_data.attrs['level_type'])

    rain = rain_data.where((rain_data > 0.1) & (snow_data < 0.1))
    rain.attrs = mdgstda.get_stda_attrs(var_name='rain',valid_time=rain_data.attrs['valid_time'],data_source=rain_data.attrs['data_source'],level_type=rain_data.attrs['level_type'])

    return snow, sleet,  rain
