
import os
import datetime

import sys

from .era5 import ERA5DataService

from .lib import utl_era5
from .lib import config_era5 as CONFIG


def download_hourly_pressure_levels(init_time,
                                    var_names=['hgt', 'u', 'v', 'vvel', 'rh', 'tmp', 'pv', 'div'],
                                    levels=['200', '225', '250', '300', '350', '400', '450', '500', '550', '600',
                                            '650', '700', '750', '775', '800', '825', '850', '875', '900', '925', '950', '975', '1000'
                                            ],
                                    extent=[50, 160, 0, 70],
                                    download_dir=None,
                                    ):
    cache_dir = download_dir if download_dir else CONFIG.get_cache_dir()

    for var_name in var_names:
        era5_var = utl_era5.era5_variable(var_name=var_name, data_type='high')
        for level in levels:
            cache_file = os.path.join(cache_dir, '{0:%Y%m%d%H%M}/hourly/{1}/{2}/{0:%Y%m%d%H%M}_{3}_{4}_{5}_{6}.nc'.format(init_time, var_name, level, extent[0], extent[1], extent[2], extent[3]))
            ERA5DataService().download_hourly_pressure_levels(init_time, era5_var, level, cache_file, extent=extent)


def download_hourly_single_levels(init_time,
                                  var_names=['u10m', 'v10m', 'psfc', 'tcwv', 'prmsl'],
                                  extent=[50, 160, 0, 70],
                                  download_dir=None,
                                  ):
    cache_dir = download_dir if download_dir else CONFIG.get_cache_dir()

    for var_name in var_names:
        era5_var = utl_era5.era5_variable(var_name, data_type='surface')
        cache_file = os.path.join(cache_dir, '{0:%Y%m%d%H%M}/hourly/{1}/{0:%Y%m%d%H%M}_{2}_{3}_{4}_{5}.nc'.format(init_time, var_name, extent[0], extent[1], extent[2], extent[3]))
        ERA5DataService().download_hourly_single_levels(init_time, era5_var, cache_file, extent=extent)


def download_hourly(init_time,
                    pressure_var_names=['hgt', 'u', 'v', 'vvel', 'rh', 'tmp', 'pv', 'div'],
                    pressure_levels=['200', '225', '250', '300', '350', '400', '450', '500', '550', '600',
                                     '650', '700', '750', '775', '800', '825', '850', '875', '900', '925', '950', '975', '1000'
                                     ],
                    single_var_names=['u10m', 'v10m', 'psfc', 'tcwv', 'prmsl'],
                    extent=[50, 160, 0, 70],
                    download_dir=None,
                    ):
    download_hourly_pressure_levels(init_time, var_names=pressure_var_names, levels=pressure_levels, extent=extent, download_dir=download_dir)
    download_hourly_single_levels(init_time, var_names=single_var_names, extent=extent, download_dir=download_dir)


if __name__ == '__main__':
    init_time = datetime.datetime(2020, 1, 1, 0)
    download_hourly(init_time)
