import os
import sys

import numpy as np

import cartopy.crs as ccrs

from metdig.graphics import pallete_set
from metdig.graphics.lib.utility import save
from  metdig.graphics.lib.utility import kwargs_wrapper

import matplotlib.pyplot as plt
import glob

@kwargs_wrapper
class horizontal_compose(object):
    def __init__(self, description='', map_extent=(60, 145, 15, 55), output_dir=None, png_name='', is_overwrite=False,**kwargs):

        self.png_name = png_name
        self.output_dir = output_dir
        if((glob.glob(os.path.join(str(self.output_dir), self.png_name)) != []) and (not is_overwrite)): 
            raise Exception('路径下已经有该图'+os.path.join(self.output_dir, self.png_name))
        self.is_return_imgbuf = kwargs.pop('is_return_imgbuf', False)
        self.is_clean_plt = kwargs.pop('is_clean_plt', False)
        self.is_return_figax = kwargs.pop('is_return_figax', False)
        self.is_return_pngname = kwargs.pop('is_return_pngname', False)

        # crs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2] + map_extent[3]) / 2.,
        #                            central_longitude=(map_extent[0] + map_extent[1]) / 2.,
        #                            standard_parallels=[30., 60.])
        # crs = ccrs.PlateCarree()
        # self.fig, self.ax = pallete_set.horizontal_pallete(figsize=(18, 9), crs=crs, map_extent=map_extent,
        #                                                    title=title, forcast_info=description, **kwargs)

        self.fig, self.ax = pallete_set.horizontal_pallete(map_extent=map_extent, forcast_info=description, **kwargs)

    def save(self):
        return save(self.fig, self.ax, self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)

@kwargs_wrapper
class cross_lonpres_compose(object):
    def __init__(self, levels, title='', description='', output_dir=None, png_name='', **kwargs):

        self.png_name = png_name
        self.output_dir = output_dir
        if(glob.glob(os.path.join(str(self.output_dir), self.png_name)) != []): 
            raise Exception('路径下已经有该图'+os.path.join(self.output_dir, self.png_name))
        self.is_return_imgbuf = kwargs.pop('is_return_imgbuf', False)
        self.is_clean_plt = kwargs.pop('is_clean_plt', False)
        self.is_return_figax = kwargs.pop('is_return_figax', False)
        self.is_return_pngname = kwargs.pop('is_return_pngname', False)

        self.fig, self.ax = pallete_set.cross_lonpres_pallete(levels=levels, title=title, forcast_info=description, **kwargs)

    def save(self):
        return save(self.fig, self.ax, self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)

@kwargs_wrapper
class cross_timepres_compose(object):
    def __init__(self, levels, times, title='', description='', output_dir=None, png_name='', **kwargs):

        self.png_name = png_name
        self.output_dir = output_dir
        if(glob.glob(os.path.join(str(self.output_dir), self.png_name)) != []): 
            raise Exception('路径下已经有该图'+os.path.join(self.output_dir, self.png_name))
        self.is_return_imgbuf = kwargs.pop('is_return_imgbuf', False)
        self.is_clean_plt = kwargs.pop('is_clean_plt', False)
        self.is_return_figax = kwargs.pop('is_return_figax', False)
        self.is_return_pngname = kwargs.pop('is_return_pngname', False)

        self.fig, self.ax = pallete_set.cross_timepres_pallete(
            levels=levels, times=np.array(times), title=title, forcast_info=description, **kwargs)

    def save(self):
        return save(self.fig, self.ax, self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)

@kwargs_wrapper
class cross_timeheight_compose(object):
    def __init__(self, heights, times, title='', description='', output_dir=None, png_name='', **kwargs):

        self.png_name = png_name
        self.output_dir = output_dir
        if(glob.glob(os.path.join(str(self.output_dir), self.png_name)) != []): 
            raise Exception('路径下已经有该图'+os.path.join(self.output_dir, self.png_name))
        self.is_return_imgbuf = kwargs.pop('is_return_imgbuf', False)
        self.is_clean_plt = kwargs.pop('is_clean_plt', False)
        self.is_return_figax = kwargs.pop('is_return_figax', False)
        self.is_return_pngname = kwargs.pop('is_return_pngname', False)

        self.fig, self.ax = pallete_set.cross_timeheight_pallete(heights=heights, times=np.array(times), title=title, forcast_info=description, **kwargs)

    def save(self):
        return save(self.fig, self.ax, self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)

@kwargs_wrapper
class skewt_compose(object):
    def __init__(self, title='', description='', output_dir=None, png_name='', **kwargs):

        self.png_name = png_name
        self.output_dir = output_dir
        if(glob.glob(os.path.join(str(self.output_dir), self.png_name)) != []): 
            raise Exception('路径下已经有该图'+os.path.join(self.output_dir, self.png_name))      
        self.is_return_imgbuf = kwargs.pop('is_return_imgbuf', False)
        self.is_clean_plt = kwargs.pop('is_clean_plt', False)
        self.is_return_figax = kwargs.pop('is_return_figax', False)
        self.is_return_pngname = kwargs.pop('is_return_pngname', False)

        self.fig, self.skew = pallete_set.skewt_pallete( title=title, forcast_info=description, **kwargs)

    def save(self):
        return save(self.fig, self.skew.ax, self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)

@kwargs_wrapper
class time_series_left_right_bottom_compose(object):
    def __init__(self,times=None, title_left='', title_right='', label_leftax='', label_rightax='', label_bottomax='', output_dir=None, png_name='', **kwargs):

        self.png_name = png_name
        self.output_dir = output_dir
        if(glob.glob(os.path.join(str(self.output_dir), self.png_name)) != []): 
            raise Exception('路径下已经有该图'+os.path.join(self.output_dir, self.png_name))
        self.is_return_imgbuf = kwargs.pop('is_return_imgbuf', False)
        self.is_clean_plt = kwargs.pop('is_clean_plt', False)
        self.is_return_figax = kwargs.pop('is_return_figax', False)
        self.is_return_pngname = kwargs.pop('is_return_pngname', False)

        self.fig, self.ax_tmp, self.ax_rh, self.ax_uv = pallete_set.time_series_left_right_bottom(times=times,
            title_left=title_left, title_right=title_right, label_leftax=label_leftax, label_rightax=label_rightax, label_bottomax=label_bottomax,**kwargs)

    def save(self):
        return save(self.fig, [self.ax_tmp, self.ax_rh, self.ax_uv], self.png_name, self.output_dir, self.is_return_imgbuf, self.is_clean_plt, self.is_return_figax, self.is_return_pngname)
