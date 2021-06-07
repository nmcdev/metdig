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

import logging
_log = logging.getLogger(__name__)

__all__ = [
    'model_stability',
]

def model_stability(target_time=None, latest_init_time=None, ninit=4, init_interval=12, data_name='ecmwf',
                     func=None, func_other_args={}, max_workers=6,
                     output_dir=None, show='animation', tab_size=(30, 18), list_size=(16, 9),
                     is_clean_plt=False):
    '''

    [稳定性]

    Keyword Arguments:
        target_time {[datetime]} -- [某个时刻] (default: {None})
        latest_init_time {[datetime]} -- [距target_time最近的一次起报时间] (default: {None})
        ninit {number} -- [起报次数] (default: {4})
        init_interval {number} -- [不同起报时间的时间间隔] (default: {12})
        data_name {[str]} -- [模式名] (default: {None})
        func {[function]} -- [函数名] (default: {None})
        func_other_args {dict} -- [函数参数字典] (default: {{}})
        max_workers {number} -- [最大进程数] (default: {6})
        output_dir {[str]} -- [输出目录] (default: {None})
        show {str} -- ['list', show all plots in one cell.
                       'tab', show one plot in each tab page. 
                       'animation', show gif animation.] (default: {'animation'})
        tab_size {tuple} -- [如果show='tab'时生效，输出图片分辨率] (default: {(30, 18)})
        list_size {tuple} -- [如果show='list'时生效，输出图片分辨率] (default: {(16, 9)})

    Returns:
        [type] -- [description]
    '''
    if latest_init_time is None:
        # 获得最近的一次模式起报时间
        latest_init_time = get_nearest_init_time(24, data_name, func, func_other_args)
    else:
        latest_init_time = datetime.datetime(latest_init_time.year, latest_init_time.month, latest_init_time.day, latest_init_time.hour)

    # 如果target_time为空，则取latest_init_time+36
    if target_time is None:
        target_time = latest_init_time + datetime.timedelta(hours=36) 
    target_time = datetime.datetime(target_time.year, target_time.month, target_time.day, target_time.hour)
    if target_time < latest_init_time:
        raise Exception('target_time({:%Y%m%d%H}) < latest_init_time({:%Y%m%d%H})'.format(target_time, latest_init_time))

    init_time = latest_init_time
    fhour = int((target_time - latest_init_time).total_seconds() / 60 / 60)

    func_args_all = []
    for i in range(ninit):
        func_args = copy.deepcopy(func_other_args)
        func_args['init_time'] = init_time - datetime.timedelta(hours=init_interval * i)
        func_args['fhour'] = fhour + init_interval * i
        func_args['data_name'] = data_name
        func_args['is_return_pngname'] = True
        func_args['is_return_imgbuf'] = True
        if func_args['fhour'] < 0:
            continue
        _log.info(f'''{func_args['init_time']} {func_args['fhour']}''')
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
        gif_name = 'stability_{}_{}_{:%Y%m%d%H}_{:03d}_{:03d}.gif'.format(func.__name__, data_name, target_time, ninit, init_interval)
        ret = save_animation(all_img_bufs, output_dir, gif_name, is_clean_plt=is_clean_plt)
    elif show == 'tab':
        png_name = 'stability_{}_{}_{:%Y%m%d%H}_{:03d}_{:03d}.png'.format(func.__name__, data_name, target_time, ninit, init_interval)
        ret = save_tab(all_img_bufs, output_dir, png_name, tab_size=tab_size, is_clean_plt=is_clean_plt)

    if ret:
        return ret
