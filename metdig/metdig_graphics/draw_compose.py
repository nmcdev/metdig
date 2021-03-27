import os

import cartopy.crs as ccrs

from metdig.metdig_graphics import pallete_set
from metdig.metdig_graphics.lib.utility import save

import matplotlib.pyplot as plt


def horizontal_compose(input,
                       title='',
                       description='',
                       map_extent=(60, 145, 15, 55),
                       add_china=True,
                       add_city=True,
                       add_background=True,
                       add_south_china_sea=True,
                       output_dir=None,
                       png_name='',
                       is_clean_plt=False,
                       is_return_figax=False,
                       is_return_imgbuf=False):
    # ccrs setting
    # crs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2] + map_extent[3]) / 2.,
    #                            central_longitude=(map_extent[0] + map_extent[1]) / 2.,
    #                            standard_parallels=[30., 60.])
    crs = ccrs.PlateCarree()

    # fig initialization
    fig, ax = pallete_set.horizontal_pallete(
        figsize=(18, 9),
        crs=crs,
        map_extent=map_extent,
        title=title,
        forcast_info=description,
        add_china=add_china,
        add_city=add_city,
        add_background=add_background,
        add_south_china_sea=add_south_china_sea,
    )

    for item in input:
        data = item[0]
        func = item[1]
        func_kwargs = {}
        if len(item) == 3:
            func_kwargs = item[2]
        func(ax, data, **func_kwargs)

    return save(fig, ax, png_name, output_dir, is_return_imgbuf, is_clean_plt, is_return_figax)
