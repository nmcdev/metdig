# -*- coding: utf-8 -*-

'''

'''
import os
import datetime
import copy

from metdig.hub.lib.utility import get_nearest_init_time

from metdig.hub.lib.utility import save_animation
from metdig.hub.lib.utility import save_tab
from metdig.hub.lib.utility import save_list
from metdig.hub.lib.utility import mult_process
from metdig.hub.lib.utility import get_onestep_ret_imgbufs
from metdig.hub.lib.utility import get_onestep_ret_pngnames
from metdig.hub.lib.utility import strparsetime

import logging
_log = logging.getLogger(__name__)

__all__ = [
    'modelver_vs_anl',
]

def modelver_vs_anl(anl_time=None, anl_data_source='cassandra', anl_data_name='ecmwf',
                    ninit=4, init_interval=12, data_source='cassandra', data_name='ecmwf',
                    func=None, func_other_args={}, max_workers=6,
                    output_dir=None, show='tab', tab_size=(30, 18), list_size=(16, 9),
                    is_clean_plt=False):
    '''

    [基于零场的分析场或再分析场的天气学检验]

    Keyword Arguments:
        anl_time {[datetime]} -- [零场的分析场或再分析场时间] (default: {None})
        anl_data_name {[str]} -- [零场的分析场或再分析场模式名] (default: {None})
        ninit {number} -- [起报次数] (default: {4})
        init_interval {number} -- [不同起报时间的时间间隔] (default: {12})
        data_name {[str]} -- [预报场模式名] (default: {None})
        func {[function]} -- [函数名] (default: {None})
        func_other_args {dict} -- [函数参数字典] (default: {{}})
        max_workers {number} -- [最大进程数] (default: {6})
        output_dir {[str]} -- [输出目录] (default: {None})
        show {str} -- ['list', show all plots in one cell.
                       'tab', show one plot in each tab page. 
                       'animation', show gif animation.] (default: {'animation'})
        tab_size {tuple} -- [如果show='tab'时生效，输出图片分辨率] (default: {(30, 18)})
        list_size {tuple} -- [如果show='tab'时生效，输出图片分辨率] (default: {(16, 9)})

    Returns:
        [type] -- [description]
    '''
    anl_time = strparsetime(anl_time)

    init_time = None
    fhour = None
    if anl_time is None:
        if anl_data_name == 'era5':
            raise Exception('era5为再分析数据，请给定anl_time')
        # 获得最近的一次000时效预报数据
        init_time = get_nearest_init_time(24, anl_data_source, anl_data_name, func, func_other_args)
        fhour = 0
    else:
        # fhour固定为0，此时对于如ecwmf只有anl_time=08/20时才会找得到
        init_time = datetime.datetime(anl_time.year, anl_time.month, anl_time.day, anl_time.hour)
        fhour = 0

    func_args_all = []
    for i in range(ninit):
        func_args = copy.deepcopy(func_other_args)
        func_args['init_time'] = init_time - datetime.timedelta(hours=init_interval * i)
        func_args['fhour'] = fhour + init_interval * i
        if i == 0:
            func_args['data_source'] = anl_data_source
            func_args['data_name'] = anl_data_name
        else:
            func_args['data_source'] = data_source
            func_args['data_name'] = data_name
        func_args['is_return_pngname'] = True
        func_args['is_return_imgbuf'] = True
        _log.info(f'''{func_args['init_time']} {func_args['fhour']} {func_args['data_name']}''')
        func_args_all.append(func_args)

    # 多进程绘图
    all_ret = mult_process(func=func, func_args_all=func_args_all, max_workers=max_workers)
    all_img_bufs = get_onestep_ret_imgbufs(all_ret)
    all_png_names = get_onestep_ret_pngnames(all_ret)

    # 输出
    ret = None
    if show == 'list':
        ret = save_list(all_img_bufs, output_dir, all_png_names, list_size=list_size, is_clean_plt=is_clean_plt)
    elif show == 'animation':
        gif_name = 'modelver_vs_anl_{}_{}_{:%Y%m%d%H}_{:03d}_{:03d}.gif'.format(func.__name__, data_name, init_time, ninit, init_interval)
        ret = save_animation(all_img_bufs, output_dir, gif_name, is_clean_plt=is_clean_plt)
    elif show == 'tab':
        png_name = 'modelver_vs_anl_{}_{}_{:%Y%m%d%H}_{:03d}_{:03d}.png'.format(func.__name__, data_name, init_time, ninit, init_interval)
        ret = save_tab(all_img_bufs, output_dir, png_name, tab_size=tab_size, is_clean_plt=is_clean_plt)

    if ret:
        return ret
