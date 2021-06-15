# -*- coding: utf-8 -*-


import sys
import os
import locale
import datetime
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl

from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes

import cartopy.crs as ccrs
import cartopy.feature as cfeature

from metpy.plots import SkewT

import metdig.graphics.lib.utl_plotmap as utl_plotmap
import metdig.graphics.lib.utility as utl

def plt_base_env():
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')


def horizontal_pallete(figsize=(16, 9), crs=ccrs.PlateCarree(), map_extent=(60, 145, 15, 55),
                       title='', title_fontsize=23, forcast_info='', nmc_logo=False,
                       add_china=True, add_city=True, add_background=True, add_south_china_sea=True, add_grid=True):
    plt_base_env() # 初始化字体中文等

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(projection=ccrs.PlateCarree())

    ax.set_title(title, loc='left', fontsize=title_fontsize)

    # set_map_extent
    map_extent2 = utl_plotmap.adjust_map_ratio(ax, map_extent=map_extent, datacrs=ccrs.PlateCarree())

    # add grid lines
    if add_grid:
        gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=100)
        gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
        gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    if add_china:
        utl_plotmap.add_china_map_2cartopy_public(ax, name='coastline', edgecolor='gray', lw=0.8, zorder=100, alpha=0.5)
        utl_plotmap.add_china_map_2cartopy_public(ax, name='province', edgecolor='gray', lw=0.5, zorder=100)
        utl_plotmap.add_china_map_2cartopy_public(ax, name='nation', edgecolor='black', lw=0.8, zorder=100)
        utl_plotmap.add_china_map_2cartopy_public(ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=100, alpha=0.5)
        pass

    if add_city:
        small_city = False
        if(map_extent2[1] - map_extent2[0] < 25):
            small_city = True
        utl_plotmap.add_city_on_map(ax, map_extent=map_extent2, transform=ccrs.PlateCarree(),
                                    zorder=101, size=13, small_city=small_city)

    if add_background:
        # ax.add_feature(cfeature.OCEAN)
        # utl_plotmap.add_cartopy_background(ax, name='RD')
        ax.add_feature(cfeature.LAND, facecolor='#EBDBB2')
        ax.add_feature(cfeature.OCEAN, facecolor='#C8EBFA')


    if add_south_china_sea:
        l, b, w, h = ax.get_position().bounds
        utl_plotmap.add_south_china_sea_png(pos=[l + w - 0.094, b, 0.11, 0.211], name='simple')  # 直接贴图

    l, b, w, h = ax.get_position().bounds
    if nmc_logo:
        if forcast_info:
            bax_h = 0.1
            bax = plt.axes([l, b + h - bax_h, 0.25, bax_h], facecolor='#FFFFFFCC')
            bax.set_yticks([])
            bax.set_xticks([])
            bax.axis([0, 10, 0, 10])
            bax.text(2.5, 9.8, forcast_info, size=15, va='top', ha='left',)

        utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h - 0.1, .1, .1], which='nmc', size='Xlarge')
    else:
        if forcast_info:
            bax_h = 0.025 * len(forcast_info.strip().split('\n'))
            bax = plt.axes([l, b + h - bax_h, 0.2, bax_h], facecolor='#FFFFFFCC')
            bax.set_yticks([])
            bax.set_xticks([])
            bax.axis([0, 10, 0, 10])
            bax.text(0.5, 9.8, forcast_info, size=15, va='top', ha='left',)

    return fig, ax


def cross_lonpres_pallete(figsize=(16, 9), levels=None, title='', forcast_info='', nmc_logo=False):

    plt_base_env() # 初始化字体中文等

    fig = plt.figure(figsize=figsize)
    ax = plt.axes()

    ax.set_title(title, loc='right', fontsize=25)

    # Adjust the y-axis to be logarithmic
    ax.set_yscale('symlog')
    ax.set_yticklabels(np.arange(levels[0], levels[-1], -100))
    ax.set_ylim(levels[0], levels[-1])
    ax.set_yticks(np.arange(levels[0], levels[-1], -100))

    ax.set_ylabel('Pressure (hPa)')
    ax.set_xlabel('Longitude')

    if forcast_info:
        l, b, w, h = ax.get_position().bounds
        bax = plt.axes([l, b + h, .25, .1], facecolor='#FFFFFFCC')
        bax.axis('off')
        bax.set_yticks([])
        bax.set_xticks([])
        bax.axis([0, 10, 0, 10])
        bax.text(1.5, 0.4, forcast_info, size=11)

    if nmc_logo:
        l, b, w, h = ax.get_position().bounds
        utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h, 0.07, 0.07], which='nmc', size='Xlarge')

    return fig, ax


def cross_timepres_pallete(figsize=(16, 9), levels=None, times=None, title='', forcast_info='', nmc_logo=False, reverse_time=True):
    """[时间剖面画板初始化]

    Args:
        figsize (tuple, optional): [图形比例大小]. Defaults to (16, 9).
        levels ([type], optional): [垂直层次坐标]. Defaults to None.
        times ([type], optional): [时间坐标]. Defaults to None.
        title (str, optional): [画板标题]. Defaults to ''.
        forcast_info (str, optional): [时间信息标注]. Defaults to ''.
        reverse_time (bool, optional): [时间轴是否反转]. Defaults to True.

    Returns:
        [type]: [description]
    """
    if(reverse_time):
        times = times[::-1]

    plt_base_env() # 初始化字体中文等

    fig = plt.figure(figsize=figsize)
    ax = plt.axes()

    ax.set_title(title, loc='right', fontsize=25)

    xstklbls = mpl.dates.DateFormatter('%m月%d日%H时')
    ax.xaxis.set_major_formatter(xstklbls)
    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_fontsize(15)
        label.set_horizontalalignment('right')

    for label in ax.get_yticklabels():
        label.set_fontsize(15)

    ax.set_yscale('symlog')
    ax.set_ylabel('高度 （hPa）', fontsize=15)
    ax.set_yticklabels([100, 925, 850, 700, 600, 500, 400, 300])
    ax.set_yticks([100, 925, 850, 700, 600, 500, 400, 300])
    ax.set_ylim(levels.max(), levels.min())
    ax.set_xlim(times[0], times[-1])

    if forcast_info:
        l, b, w, h = ax.get_position().bounds
        bax = plt.axes([l, b + h, .25, .1], facecolor='#FFFFFFCC')
        bax.axis('off')
        bax.set_yticks([])
        bax.set_xticks([])
        bax.axis([0, 10, 0, 10])
        bax.text(1.5, 0.4, forcast_info, size=11)

    if nmc_logo:
        l, b, w, h = ax.get_position().bounds
        utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h, 0.07, 0.07], which='nmc', size='Xlarge')

    return fig, ax

def profile_pallete(figsize=(16, 9), levels=None, times=None, title='', forcast_info='', nmc_logo=False, reverse_time=True):
    if(reverse_time):
        times = times[::-1]

    plt_base_env() # 初始化字体中文等

    fig = plt.figure(figsize=figsize)
    ax = plt.axes()

    ax.set_title(title, loc='right', fontsize=25)

    xstklbls = mpl.dates.DateFormatter('%m月%d日%H时')
    ax.xaxis.set_major_formatter(xstklbls)
    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_fontsize(15)
        label.set_horizontalalignment('right')

    for label in ax.get_yticklabels():
        label.set_fontsize(15)

    ax.set_ylabel('高度/m', fontsize=15)
    ax.set_yticklabels([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])
    # ax.set_yticks([100, 925, 850, 700, 600, 500, 400, 300])
    ax.set_ylim(0, 5000)
    ax.set_xlim(times[0], times[-1])

    if forcast_info:
        l, b, w, h = ax.get_position().bounds
        bax = plt.axes([l, b + h, .25, .1], facecolor='#FFFFFFCC')
        bax.axis('off')
        bax.set_yticks([])
        bax.set_xticks([])
        bax.axis([0, 10, 0, 10])
        bax.text(1.5, 0.4, forcast_info, size=11)

    if nmc_logo:
        l, b, w, h = ax.get_position().bounds
        utl.add_logo_extra_in_axes(pos=[l - 0.02, b + h, 0.07, 0.07], which='nmc', size='Xlarge')

    return fig, ax


def time_series_left_right_bottom(figsize=(16, 4.5), title_left='', title_right='', label_leftax='', label_rightax='', label_bottomax=''):

    plt_base_env() # 初始化字体中文等

    fig = plt.figure(figsize=figsize)

    ax_left = HostAxes(fig, [0.1, 0.28, .8, .62])
    ax_right = ParasiteAxes(ax_left, sharex=ax_left)

    # append axes
    ax_left.parasites.append(ax_right)

    # invisible right axis of ax
    ax_left.grid(axis='x', which='minor', ls='--')
    ax_left.axis['right'].set_visible(False)
    ax_left.axis['right'].set_visible(False)
    ax_left.axis['left'].label.set_fontsize(15)
    ax_left.axis['left'].major_ticklabels.set_fontsize(15)
    ax_left.tick_params(length=10)
    ax_left.tick_params(axis='y', labelsize=100)
    ax_left.set_ylabel(label_leftax)
    ax_left.set_xticklabels([' '])
    ax_left.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H'))  # 设置格式
    ax_left.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 20)))  # 单位是小时
    ax_left.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=(8, 11, 14, 17, 20, 23, 2, 5)))  # 单位是小时
    ax_left.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))  # 将此y轴次刻度标签设置为1的倍数
    ax_left.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5))  # 将此y轴主刻度标签设置为5的倍数
    fig.add_axes(ax_left)

    ax_right.axis['right'].set_visible(True)
    ax_right.axis['right'].major_ticklabels.set_visible(True)
    ax_right.axis['right'].label.set_visible(True)
    ax_right.axis['right'].label.set_fontsize(15)
    ax_right.axis['right'].major_ticklabels.set_fontsize(15)
    ax_right.set_ylabel(label_rightax)

    plt.title(title_left, loc='left', fontsize=21)
    plt.title(title_right, loc='right', fontsize=15)

    ax_bottom = plt.axes([0.1, 0.16, .8, .12])
    ax_bottom.grid(axis='x', which='both', ls='--')
    ax_bottom.tick_params(length=5, axis='x')
    ax_bottom.tick_params(length=0, axis='y')
    ax_bottom.tick_params(axis='x', labelsize=15)
    ax_bottom.set_ylabel(label_bottomax, fontsize=15)
    # ax_bottom.axis('off')
    ax_bottom.set_yticklabels([' '])
    ax_bottom.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H'))  # 设置格式
    ax_bottom.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=(8, 20)))  # 单位是小时
    ax_bottom.xaxis.set_minor_locator(mpl.dates.HourLocator(byhour=(8, 11, 14, 17, 20, 23, 2, 5)))  # 单位是小时

    return fig, ax_left, ax_right, ax_bottom


def skewt_pallete(figsize=(9, 9), title='', title_fontsize=23, forcast_info='', nmc_logo=False):

    plt_base_env() # 初始化字体中文等

    fig = plt.figure(figsize=figsize)

    skew = SkewT(fig, rotation=45)

    skew.ax.set_title(title, loc='left', fontsize=title_fontsize)

    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-40, 60)

    if nmc_logo:
        if forcast_info:
            bax_h = 0.08
            l, b, w, h = skew.ax.get_position().bounds
            bax = plt.axes([l, b + h - bax_h, .32, bax_h], facecolor='#FFFFFFCC')
            bax.set_yticks([])
            bax.set_xticks([])
            bax.axis([0, 10, 0, 10])
            bax.text(2.5, 9.8, forcast_info, size=11, va='top', ha='left',)

        l, b, w, h = skew.ax.get_position().bounds
        utl.add_logo_extra_in_axes(pos=[l - 0.0, b + h - 0.075, .07, .07], which='nmc', size='Xlarge')
    else:
        if forcast_info:
            bax_h = 0.02 * len(forcast_info.strip().split('\n'))
            l, b, w, h = skew.ax.get_position().bounds
            bax = plt.axes([l, b + h - bax_h, .28, bax_h], facecolor='#FFFFFFCC')
            bax.set_yticks([])
            bax.set_xticks([])
            bax.axis([0, 10, 0, 10])
            bax.text(0.5, 9.8, forcast_info, size=11, va='top', ha='left',)

    return fig, skew
