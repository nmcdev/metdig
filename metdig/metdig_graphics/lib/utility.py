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
import PIL

pkg_name = 'metdig.metdig_graphics'


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
        print("Micaps 17 file error: " + str(err))
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


def plt_kwargs_lcn_set(cmap_def, norm_def, levels_def, **kwargs):
    # 关于levels cmap norm设置的规则，如果kwargs设置了levels cmap norm则逐项顶掉预设值
    levels = kwargs.pop('levels', None)
    cmap = kwargs.pop('cmap', None)
    norm = kwargs.pop('norm', None)
    if levels is None:
        levels = levels_def
    if cmap is None:
        cmap = cmap_def
    if norm is None:
        norm = norm_def
    return cmap, norm, levels, kwargs


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

'''
# 弃用，该方法frombuff reshape 出错
def get_imgbuf_from_fig(fig, dpi=200):
    # define a function which returns an image as numpy array from figure
    io_buf = io.BytesIO()
    fig.savefig(io_buf, format='raw', dpi=dpi)  # save raw
    io_buf.seek(0)


    # raw to image array
    img_arr = np.reshape(np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
                         newshape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1))
    io_buf.close()

    # import matplotlib
    # print(matplotlib.get_backend())
    # print(fig.bbox.bounds)
    # print(fig.canvas.get_width_height())
    # print(img_arr.shape)
    # Qt5Agg
    # (0.0, 0.0, 3600.0, 1800.0)
    # (1800, 900)
    # (1800, 3600, 4)

    # TkAgg
    # (0.0, 0.0, 1800.0, 900.0)
    # (1800, 900)
    # (900, 1800, 16)


    # image 去除周围空白
    print(img_arr.shape)
    img_arr = img_trim(img_arr)

    return img_arr

def get_imgbuf_from_fig(fig):
    # define a function which returns an image as numpy array from figure
    # raw to image array
    fig.canvas.draw()
    pil_img = PIL.Image.frombytes('RGBA', fig.canvas.get_width_height(), fig.canvas.buffer_rgba().tobytes())
    img_arr = np.array(pil_img)

    # 去除周围空白
    # print(img_arr.shape)
    img_arr = img_trim(img_arr) 
    
    return img_arr
'''


def get_imgbuf_from_fig(fig, dpi=200):
    # define a function which returns an image as numpy array from figure
    # raw to image array
    io_buf = io.BytesIO()
    fig.savefig(io_buf, format='png', dpi=dpi)  # save raw
    io_buf.seek(0)

    pil_img =  PIL.Image.open(io_buf)
    img_arr = np.array(pil_img)

    # 去除周围空白
    # print(img_arr.shape)
    img_arr = img_trim(img_arr) 
    
    return img_arr