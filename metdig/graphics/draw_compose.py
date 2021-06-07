import os

import numpy as np

import cartopy.crs as ccrs

from metdig.graphics import pallete_set
from metdig.graphics.lib.utility import save

import matplotlib.pyplot as plt


class horizontal_compose(object):
    def __init__(self, title='', description='', map_extent=(60, 145, 15, 55),
                 add_china=True, add_city=True, add_background=True, add_south_china_sea=True,
                 output_dir=None, png_name='', is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False, is_return_pngname=False,
                 **kwargs):

        # crs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2] + map_extent[3]) / 2.,
        #                            central_longitude=(map_extent[0] + map_extent[1]) / 2.,
        #                            standard_parallels=[30., 60.])
        crs = ccrs.PlateCarree()
        self.fig, self.ax = pallete_set.horizontal_pallete(figsize=(18, 9), crs=crs, map_extent=map_extent,
                                                           title=title, forcast_info=description, add_china=add_china, add_city=add_city,
                                                           add_background=add_background, add_south_china_sea=add_south_china_sea, **kwargs)

        self.png_name = png_name
        self.output_dir = output_dir
        self.is_return_imgbuf = is_return_imgbuf
        self.is_clean_plt = is_clean_plt
        self.is_return_figax = is_return_figax
        self.is_return_pngname = is_return_pngname

    def save(self):
        return save(self.fig, self.ax, self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)


class cross_lonpres_compose(object):
    def __init__(self, levels, title='', description='',
                 output_dir=None, png_name='', is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False, is_return_pngname=False,
                 **kwargs):

        self.fig, self.ax = pallete_set.cross_lonpres_pallete(figsize=(16, 9), levels=levels, title=title, forcast_info=description, **kwargs)

        self.png_name = png_name
        self.output_dir = output_dir
        self.is_return_imgbuf = is_return_imgbuf
        self.is_clean_plt = is_clean_plt
        self.is_return_figax = is_return_figax
        self.is_return_pngname = is_return_pngname

    def save(self):
        return save(self.fig, self.ax, self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)


class cross_timepres_compose(object):
    def __init__(self, levels, times, title='', description='',
                 output_dir=None, png_name='', is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False, is_return_pngname=False,
                 **kwargs):
        self.fig, self.ax = pallete_set.cross_timepres_pallete(
            figsize=(16, 9), levels=levels, times=np.array(times), title=title, forcast_info=description, **kwargs)

        self.png_name = png_name
        self.output_dir = output_dir
        self.is_return_imgbuf = is_return_imgbuf
        self.is_clean_plt = is_clean_plt
        self.is_return_figax = is_return_figax
        self.is_return_pngname = is_return_pngname

    def save(self):
        return save(self.fig, self.ax, self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)

class skewt_compose(object):
    def __init__(self, title='', description='',
                 output_dir=None, png_name='', is_clean_plt=False, is_return_figax=False, is_return_imgbuf=False, is_return_pngname=False,
                 **kwargs):
        self.fig, self.skew = pallete_set.skewt_pallete(figsize=(9, 9), title=title, forcast_info=description, **kwargs)

        self.png_name = png_name
        self.output_dir = output_dir
        self.is_return_imgbuf = is_return_imgbuf
        self.is_clean_plt = is_clean_plt
        self.is_return_figax = is_return_figax
        self.is_return_pngname = is_return_pngname

    def save(self):
        return save(self.fig, self.skew.ax, self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)
