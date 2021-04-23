# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
  Collection of color map functions.
"""

import os
import sys
import re
import glob
import pathlib
import pkg_resources
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm
from matplotlib import colors
from matplotlib.colors import ListedColormap, to_rgb, LinearSegmentedColormap
from metdig.metdig_graphics.cmap.cpt import gmtColormap_openfile

pkg_name = 'metdig.metdig_graphics'


def make_cmap(incolors, position=None, rgb=False, hex=False):
    """
    Takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.

    :param incolors: RGB or HEX colors. Arrange your tuples so that
                     the first color is the lowest value for the
                     colorbar and the last is the highest.
    :param position: contains values from 0 to 1 to dictate the
                     location of each color.
    :param rgb: incolors are RGB colors
    :param hex: incolors are HEX colors
    :return: matplotlib color map function.

    :Example:
    >>> incolors = ('#996035','#F2DACD','#1E6EC8','#AAFFFF','#01F6E2',
                    '#00FF00','#03E19F','#26BC0D','#88DB07',
    ...             '#FFFF13','#FFE100','#264CFF','#FF7F00','#FF0000',
                    '#B5003C','#7F0067','#9868B4','#F2EBF5',
    ...             '#ED00ED')
    >>> pos = np.array([250,270,280,285,290,295,300,305,
                        310,315,320,330,335,340,345,350,355,360,370])
    >>> cmap = make_cmap(incolors, position=pos, hex=True)
    >>> show_colormap(cmap)
    """

    _colors = []
    if position is None:
        position = np.linspace(0, 1, len(incolors))
    else:
        position = np.array(position)
        if len(position) != len(incolors):
            # sys.exit("position length must be the same as colors")
            raise Exception("position length must be the same as colors")

    # normalize position if necessary
    if position.max() > 1 or position.min() < 0:
        positions = (
            position - position.min()) / (position.max() - position.min())
    else:
        positions = position

    if hex:
        for i in range(len(incolors)):
            _colors.append(to_rgb(incolors[i]))

    if rgb:
        bit_rgb = np.linspace(0, 1, 256)
        for i in range(len(incolors)):
            _colors.append((bit_rgb[incolors[i][0]],
                            bit_rgb[incolors[i][1]],
                            bit_rgb[incolors[i][2]]))

    cdict = {'red': [], 'green': [], 'blue': []}
    for pos, color in zip(positions, _colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 256)

    return cmap


def get_cmap(name, extend='neither', levels=None, isLinear=False):
    """[获取颜色表，注意：如果levels传参了，则会返回cmap和norm，如果levels没传参，则只会返回cmap。]

    Args:
        name ([type]): [color or colorlist or metdig colormap or matplotlib colorcmap. 
        such as:
            name = '#000000'
            name = 'black'
            name = ['#000000', '#ffffff']
            name = 'met/ape_new'
            name = 'ncl/Blre'
            name = ''
            name = 'jet'
        ]
        extend (str, optional): [both max min neither，仅在填写levels时才生效]. Defaults to 'neither'.
        levels ([list], optional): [长度必须大于等于2的颜色等级]. Defaults to None.
        isLinear ([bool], optional): [是否对colors线性化]. Defaults to False.

    Returns:
        [type]: [cmap [norm]]
    """    
    if isinstance(name, str):
        if name.startswith('met/'):
            colors = met_cmaps(name[4:]).colors
        elif name.startswith('ncl/'):
            colors = ncl_cmaps(name[4:]).colors
        elif name.startswith('guide/'):
            colors = guide_cmaps(name[6:]).colors
        else:
            if name in matplotlib.cm.cmap_d.keys():
                colors = plt.get_cmap(name)(range(256))
            else:
                colors = np.array([name]) # 单个颜色
    else:
        colors = np.array(name)

    if isLinear:
        colors = mpl.colors.LinearSegmentedColormap.from_list("", colors, N=256)(range(256)) # 线性化colors，固定拿出线性化后的256个颜色
    # print(colors * 255)
    # print(colors.shape)

    # 如果levels没有，则直接返回cmap
    if levels is None:
        return  ListedColormap(colors)

    # 确定对应levels和extend的颜色个数
    # 如levels=[1,2,3] extend='both' 则N=4
    # 如levels=[1,2,3] extend='min/max' 则N=3
    # 如levels=[1,2,3] extend='neither' 则N=2
    _levels = np.array(levels)
    if extend == 'both':
        N = _levels.size + 1
    elif extend == 'min':
        N = _levels.size 
    elif extend == 'max':
        N = _levels.size 
    elif extend == 'neither':
        N = _levels.size - 1

    # 确定对应levels和extend的颜色列表
    # 如果颜色少于N则会拉伸颜色列表和N等长
    # 如果颜色大于N则会等会自动跳跃
    idx = np.linspace(0, colors.shape[0] - 1, N, dtype=np.int)
    colors = colors[idx]
    # print(N, idx, colors)

    # 根据extent，使用第一个或者最后一个颜色设置under over，剩余其它颜色生成colormap
    if extend == 'min' and colors.shape[0] >= 2:
        cmap = ListedColormap(colors[1:])
        cmap.set_under(colors[0])
    elif extend == 'max' and colors.shape[0] >= 2:
        cmap = ListedColormap(colors[:-1])
        cmap.set_over(colors[-1])
    elif extend == 'both' and colors.shape[0] >= 3:
        cmap = ListedColormap(colors[1:-1])
        cmap.set_under(colors[0])
        cmap.set_over(colors[-1])
    else:
        cmap = ListedColormap(colors)

    # print(N, cmap.N, extend)
    if isLinear and len(levels) < 256:
        # len(levels) / 
        norm = mpl.colors.BoundaryNorm(levels, cmap.N) # 是否需要自动加细levels？
    else:
        norm = mpl.colors.BoundaryNorm(levels, cmap.N)
    return cmap, norm


def met_cmaps(name):
    """
    Get the met color maps.

    :param name: color map name.
    :return: matlibplot color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        pkg_name, "resources/colormaps_met/" + name + '.rgb')
    if not os.path.isfile(cmap_file):
        return None

    # read color data
    pattern = re.compile(r'(\d\.?\d*)\s+(\d\.?\d*)\s+(\d\.?\d*).*')
    with open(cmap_file) as cmap:
        cmap_buff = cmap.read()
    cmap_buff = re.compile('ncolors.*\n').sub('', cmap_buff)
    if re.search(r'\s*\d\.\d*', cmap_buff):
        rgb = np.asarray(pattern.findall(cmap_buff), 'f4')
    else:
        rgb = np.asarray(pattern.findall(cmap_buff), 'u1') / 255.

    # construct color map
    return ListedColormap(rgb, name=name)


def ncl_cmaps(name):
    """
    Get the ncl color maps.

    :param name: color map name.
    :return: matlibplot color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        pkg_name, "resources/colormaps_ncl/" + name + '.rgb')
    if not os.path.isfile(cmap_file):
        return None

    # read color data
    pattern = re.compile(r'(\d\.?\d*)\s+(\d\.?\d*)\s+(\d\.?\d*).*')
    with open(cmap_file) as cmap:
        cmap_buff = cmap.read()
    cmap_buff = re.compile('ncolors.*\n').sub('', cmap_buff)
    if re.search(r'\s*\d\.\d*', cmap_buff):
        rgb = np.asarray(pattern.findall(cmap_buff), 'f4')
    else:
        rgb = np.asarray(pattern.findall(cmap_buff), 'u1') / 255.

    # construct color map
    return ListedColormap(rgb, name=name)


def guide_cmaps(name):
    """
    Get guide color maps.

    :param name: guide color name number, like cs42.
    :return: matplotlib color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        pkg_name, "resources/colormaps_guide/" + name + '.txt')
    if not os.path.isfile(cmap_file):
        return None

    # # read color data
    # rgb = np.loadtxt(cmap_file)

    # # construct color map
    # return ListedColormap(rgb / 255, name=name)
    # read color data
    pattern = re.compile(r'(\d\.?\d*)\s+(\d\.?\d*)\s+(\d\.?\d*).*')
    with open(cmap_file) as cmap:
        cmap_buff = cmap.read()
    cmap_buff = re.compile('ncolors.*\n').sub('', cmap_buff)
    if re.search(r'\s*\d\.\d*', cmap_buff):
        rgb = np.asarray(pattern.findall(cmap_buff), 'f4')
    else:
        rgb = np.asarray(pattern.findall(cmap_buff), 'u1') / 255.

    # construct color map
    return ListedColormap(rgb, name=name)


def ndfd_cmaps(name):
    """
    Get ndfd color maps.
    refer to https://github.com/eengl/ndfd-colors.

    :param name: color name number, like "PoP12-Blend".
    :return: matplotlib color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        pkg_name, "resources/colormaps_ndfd/" + str(name) + '.cpt')
    if not os.path.isfile(cmap_file):
        return None

    # read color data
    rgb = gmtColormap_openfile(cmap_file, name)

    # construct color map
    return rgb


def linearized_ncl_cmap(name):
    cmap1 = ncl_cmaps(name)
    COLORS = []
    norm = np.linspace(0, 1, cmap1.N - 1)
    for i, n in enumerate(norm):
        COLORS.append((n, np.array(cmap1.colors[i])))
    cmap = mpl.colors.LinearSegmentedColormap.from_list(name, COLORS)
    return cmap


def linearized_cmap(cmap):
    COLORS = []
    norm = np.linspace(0, 1, cmap.N - 1)
    for i, n in enumerate(norm):
        COLORS.append((n, np.array(cmap.colors[i])))
    cmap = mpl.colors.LinearSegmentedColormap.from_list(cmap.name, COLORS)
    return cmap


def get_part_clev_and_cmap(cmap=None, clev_range=[0, 4], color_all=None, clev_slt=None):
    if color_all is not None:
        cmap = mpl.colors.LinearSegmentedColormap.from_list(" ", color_all)
    color_slt = np.array(cmap((clev_slt - clev_range[0]) / (clev_range[-1] - clev_range[0]))).reshape(1, 4)
    return color_slt

def plotcmap_examples(cmap, levels=None, extend='neither', isLinear=False):
    """
    Helper function to plot data with get_cmap function.
    """

    fig = plt.figure()
    ax = fig.add_subplot()

    if levels is not None:
        data = np.random.randint(levels[0], levels[-1], 900).reshape(30, 30)
        cmap, norm = get_cmap(cmap, levels=levels, extend=extend, isLinear=isLinear)
        psm = ax.pcolormesh(data, cmap=cmap, norm=norm, rasterized=True)
        fig.colorbar(psm, ax=ax, extend=extend)
    else:
        data = np.random.randint(0, 100, 900).reshape(30, 30)
        cmap = get_cmap(cmap, isLinear=isLinear)
        psm = ax.pcolormesh(data, cmap=cmap, rasterized=True)
        fig.colorbar(psm, ax=ax)
    plt.show()



if __name__ == '__main__':
    colors = 'met/rain'
    # levels = np.arange(0, 20, 0.2)
    colors = 'yellow'
    levels = [0, 2, 5, 10, 20, 30, 50, 100]

    plotcmap_examples(colors, levels)