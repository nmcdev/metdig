# -*- coding: utf-8 -*-

import io
import datetime
import os
import numba as nb
import numpy as np
import pandas as pd
import pkg_resources
import matplotlib.pyplot as plt
import matplotlib.image as image
import matplotlib.patches as patches
import PIL
from functools import wraps

from scipy.ndimage.filters import minimum_filter, maximum_filter

import logging
_log = logging.getLogger(__name__)

pkg_name = 'metdig.graphics'



import cartopy.io.img_tiles as cimgt
import cartopy.crs as ccrs
class TDT_img(cimgt.GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        url = 'https://webst01.is.autonavi.com/appmaptile?x=%s&y=%s&z=%s&style=6'% (x, y, z)
        return url
class TDT_ter(cimgt.GoogleTiles):
    def _image_url(self, tile, cache=True):
        x, y, z = tile
        # url = 'http://server.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/tile/%s/%s/%s'% (z, y, x)
        # url = 'http://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/%s/%s/%s'% (z, y, x)
        url = 'http://cache1.arcgisonline.cn/arcgis/rest/services/ChinaOnlineCommunity/MapServer/tile/%s/%s/%s'% (z, y, x)
        # url = 'http://server.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/%s/%s/%s'% (z, y, x)

        return url

class TDT(cimgt.GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        url = 'http://wprd01.is.autonavi.com/appmaptile?x=%s&y=%s&z=%s&lang=zh_cn&size=1&scl=1&style=7'% (x, y, z)
        return url

class TDT_Hillshade(cimgt.GoogleTiles):
    def _image_url(self, tile, cache=True):
        x, y, z = tile
        # url = 'http://server.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/tile/%s/%s/%s'% (z, y, x)
        url = 'http://server.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/%s/%s/%s'% (z, y, x)
        return url
def kwargs_wrapper(func):
    '''
    关键字传参时，使用kwargs={...}字典的方式，顶替掉原函数中的同名的关键字参数
    Example:
        @kwargs_wrapper()
        def func(a, b, c=3, d=4, **kwargs):
            print('c =', c)
            print('d =', d)
            print('kwargs =', kwargs)

        func(1, 2, c=-1, d=-1, e=5, kwargs={'c': 4})
        output:
        c = 4
        d = -1
        kwargs = {'e': 5}
    '''
    @wraps(func)
    def inner(*args, **kwargs):
        attrs = kwargs.pop('kwargs', None)
        if attrs:
            if isinstance(attrs, dict):
                kwargs.update(**attrs)
            else:
                kwargs['kwargs'] = attrs
        return func(*args, **kwargs)
    return inner


def read_micaps_17(fname, limit=None):
    """
    Read Micaps 17 type file (general scatter point)
    此类数据主要用于读站点信息数据
    :param fname: micaps file name.
    :param limit: region limit, [min_lat, min_lon, max_lat, max_lon]
    :return: data, pandas type
    :Examples:
    >>> data = read_micaps_3('../resources/sta2513.dat')
    """

    # check file exist
    if not os.path.isfile(fname):
        return None

    # read contents
    try:
        with open(fname, 'r') as f:
            #txt = f.read().decode('GBK').replace('\n', ' ').split()
            txt = f.read().replace('\n', ' ').split()
    except IOError as err:
        _log.error("Micaps 17 file error: " + str(err))
        return None

    # head information
    head_info = txt[2]

    # date and time
    nsta = int(txt[3])

    # cut data
    txt = np.array(txt[4:])
    txt.shape = [nsta, 7]

    # initial data
    columns = list(['ID', 'lat', 'lon', 'alt', 'temp1', 'temp2', 'Name'])
    data = pd.DataFrame(txt, columns=columns)

    # cut the region
    if limit is not None:
        data = data[(limit[0] <= data['lat']) & (data['lat'] <= limit[2]) &
                    (limit[1] <= data['lon']) & (data['lon'] <= limit[3])]

    data['nstation'] = nsta

    # check records
    if len(data) == 0:
        return None
    # return
    return data


def add_logo_extra_in_axes(pos=[0.1, 0.1, .2, .4],
                           which='nmc', size='medium', **kwargs):
    """
    :axes_pos:[left,bottom,increase_left,increase_right]
    :param which: Which logo to plot 'nmc', 'cmc'
    :param size: Size of logo to be used. Can be:
                 'small' for 40 px square
                 'medium' for 75 px square
                 'large' for 150 px square.
    :param kwargs:
    """
    fname_suffix = {
        'small': '_small.png', 'medium': '_medium.png',
        'large': '_large.png', 'Xlarge': '_Xlarge.png'}
    fname_prefix = {'nmc': 'nmc', 'cma': 'cma', 'wmo': 'wmo'}
    try:
        fname = fname_prefix[which] + fname_suffix[size]
        fpath = "resources/logo/" + fname
    except KeyError:
        raise ValueError('Unknown logo size or selection')
    logo = image.imread(pkg_resources.resource_filename(pkg_name, fpath))

    ax = plt.axes(pos, frameon=False, xticks=[], yticks=[])
    ax.imshow(logo, alpha=1, zorder=0)
    ax.axis('off')


@nb.jit()
def img_trim(img):
    '''
    裁剪去除图像周边白边
    '''
    img2 = img[:, :, :3].sum(axis=2)  # 透过度不参与计算
    (row, col) = img2.shape
    tempr0 = 0
    tempr1 = row - 1
    tempc0 = 0
    tempc1 = col - 1

    # 765 是255+255+255,如果是黑色背景就是0+0+0，彩色的背景，将765替换成其他颜色的RGB之和，这个会有一点问题，因为三个和相同但颜色不一定同
    for r in range(0, row):
        tag = False
        for c in range(0, col):
            if img2[r, c] != 765:
                tempr0 = r
                tag = True
                break
        if tag == True:
            break

    for r in range(row - 1, 0, -1):
        tag = False
        for c in range(0, col):
            if img2[r, c] != 765:
                tempr1 = r
                tag = True
                break
        if tag == True:
            break

    for c in range(0, col):
        tag = False
        for r in range(0, row):
            if img2[r, c] != 765:
                tempc0 = c
                tag = True
                break
        if tag == True:
            break

    for c in range(col - 1, 0, -1):
        tag = False
        for r in range(0, row):
            if img2[r, c] != 765:
                tempc1 = c
                tag = True
                break
        if tag == True:
            break

    new_img = img[tempr0:tempr1 + 1, tempc0:tempc1 + 1, :]
    return new_img


def get_imgbuf_from_fig(fig, dpi=200):
    # define a function which returns an image as numpy array from figure
    # raw to image array
    io_buf = io.BytesIO()
    fig.savefig(io_buf, format='png', dpi=dpi)  # save raw
    io_buf.seek(0)

    pil_img = PIL.Image.open(io_buf)
    img_arr = np.array(pil_img)

    # 去除周围空白
    # print(img_arr.shape)
    img_arr = img_trim(img_arr)

    return img_arr


def save(fig, ax, png_name, output_dir=None, is_return_imgbuf=False, is_clean_plt=False, is_return_figax=False, is_return_pngname=False):
    # 保存图片通用方法
    ret = {
        # 'png_name': None,
        # 'output_dir': None,
        # 'pic_path': None,
        # 'img_buf': None,
        # 'fig': None,
        # 'ax': None,
    }
    if is_return_pngname:
        ret['png_name'] = png_name

    # save
    if output_dir:
        if(not os.path.exists(output_dir)):
            os.makedirs(output_dir)
        out_png = os.path.join(output_dir, png_name)
        _log.info(out_png)
        ret['output_dir'] = output_dir
        ret['pic_path'] = out_png
        plt.savefig(out_png, dpi=200, bbox_inches='tight')

    if is_return_imgbuf:
        ret['img_buf'] = get_imgbuf_from_fig(fig)

    if is_clean_plt:
        plt.close(fig)

    if is_return_figax:
        ret['fig'] = fig
        ret['ax'] = ax

    return ret


@kwargs_wrapper
def add_colorbar(ax, img, ticks=None, label='', label_size=20, tick_size=15,pos='bottom', rect=None,  orientation='horizontal', pad=0, **kwargs):
    """[summary]

    Args:
        ax ([type]): [description]
        img ([type]): [description]
        ticks ([list], optional): [colorbar刻度]. Defaults to None.
        label (str, optional): [colorbar标题]. Defaults to ''.
        label_size (int, optional): [description]. Defaults to 20.
        pos (str, optional): [bottom right; 如果rect填写，则pos不生效]. Defaults to 'bottom'.
        rect ([type], optional): [4-tuple of floats *rect* = ``[left, bottom, width, height]``.]. Defaults to None.
        orientation (str, optional): [horizontal vertical; 如果pos='bottom'，则强制为'horizontal'; 如果pos='right'，则强制为vertical; 如果rect填写，才根据参数设置]. Defaults to 'horizontal'.
        pad (float, optional): [colorbar和ax的偏移距离]. Defaults to 0.
    """
    if rect:
        cax = plt.axes(rect)
    else:
        if pos == 'bottom':
            l, b, w, h = ax.get_position().bounds
            cax = plt.axes([l, b - h * 0.05 - pad, w, h * 0.02])
            orientation = 'horizontal'
        elif pos == 'right':
            l, b, w, h = ax.get_position().bounds
            cax = plt.axes([l + 0.01 + w + pad, b, 0.015, h])
            orientation = 'vertical'
        elif pos == 'lower center':
            l, b, w, h = ax.get_position().bounds
            cax = plt.axes([l+w/3., b - h * 0.05 + pad, w/3, h * 0.02])
        elif pos == 'lower left':
            l, b, w, h = ax.get_position().bounds
            cax = plt.axes([l, b - h * 0.05 + pad, w/3, h * 0.02])
        elif pos == 'lower right':
            l, b, w, h = ax.get_position().bounds
            cax = plt.axes([l+w*2/3, b - h * 0.05 + pad, w/3, h * 0.02])
        elif pos == 'right center':
            l, b, w, h = ax.get_position().bounds
            cax = plt.axes([l + 0.01 + w + pad, b+h/3, 0.015, h/3])
            orientation = 'vertical'
        elif pos == 'right top':
            l, b, w, h = ax.get_position().bounds
            cax = plt.axes([l + 0.01 + w + pad, b+h*2/3, 0.015, h/3])
            orientation = 'vertical'
        elif pos == 'right bottom':
            l, b, w, h = ax.get_position().bounds
            cax = plt.axes([l + 0.01 + w + pad, b, 0.015, h/3])
            orientation = 'vertical'

    cb = plt.colorbar(img, cax=cax, ticks=ticks, orientation=orientation, **kwargs)
    # cb.ax.tick_params(labelsize='x-large')
    cb.ax.tick_params(labelsize=tick_size)
    cb.set_label(label, size=label_size)
    return cb


def add_patchlegend(ax, labels, colors, **kwargs):
    myp = list(map(lambda c: patches.Patch(color=c, alpha=1), colors))
    ax.legend(handles=myp, labels=labels,  **kwargs)


def extrema(mat, mode='wrap', window=50):
    mn = minimum_filter(mat, size=window, mode=mode)
    mx = maximum_filter(mat, size=window, mode=mode)
    return np.nonzero(mat == mn), np.nonzero(mat == mx)
