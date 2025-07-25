# -*- coding: utf-8 -*-

'''
多模式对比
'''
import os
import copy
import datetime

from metdig.hub.lib.utility import save_tab
from metdig.hub.lib.utility import save_list
from metdig.hub.lib.utility import mult_process
from metdig.hub.lib.utility import get_onestep_ret_imgbufs
from metdig.hub.lib.utility import get_onestep_ret_pngnames
from metdig.hub.lib.utility import strparsetime

__all__ = [
    'models_compare',
]


def models_compare(init_time=None, fhour=24, data_names=['ecmwf', 'cma_gfs', 'ncep_gfs', 'cma_meso_3km'],
                   func=None, func_other_args={}, max_workers=6,
                   output_dir=None, show='tab', tab_size=(30, 18), list_size=(16, 9),tab_dist=None,
                   is_clean_plt=False):
    '''

    [多模式对比]

    Keyword Arguments:
        init_time {[datetime]} -- [起报时间] (default: {None})
        fhour {[number]} -- [预报时效] (default: {None})
        data_names {[list]} -- [多模式列表] (default: {None})
        func {[function]} -- [函数名] (default: {None})
        func_other_args {dict} -- [函数参数字典] (default: {{}})
        max_workers {number} -- [最大进程数] (default: {6})
        output_dir {[str]} -- [输出目录] (default: {None})
        show {str} -- ['list', show all plots in one cell.
                       'tab', show one plot in each tab page. ] (default: {'tab'})
        tab_size {tuple} -- [如果show='tab'时生效，输出图片分辨率] (default: {(30, 18)})

    '''
    init_time = strparsetime(init_time)

    # 参数准备
    func_args_all = []
    for data_name in data_names:
        func_args = copy.deepcopy(func_other_args)
        func_args['init_time'] = init_time
        func_args['fhour'] = fhour
        func_args['data_name'] = data_name
        func_args['is_return_imgbuf'] = True
        func_args['is_return_pngname'] = True
        func_args_all.append(func_args)

    # 多进程绘图
    all_ret = mult_process(func=func, func_args_all=func_args_all, max_workers=max_workers)
    all_img_bufs = get_onestep_ret_imgbufs(all_ret)
    all_png_names = get_onestep_ret_pngnames(all_ret)

    # 输出
    ret = None
    if show == 'list':
        ret = save_list(all_img_bufs, output_dir, all_png_names, list_size=list_size, is_clean_plt=is_clean_plt)
    elif show == 'tab':
        png_name = 'compare_{}_{}_{:%Y%m%d%H}_{:03d}.png'.format(func.__name__, 'models', init_time, fhour)
        ret = save_tab(all_img_bufs, output_dir, png_name, tab_size=tab_size, tab_dist=tab_dist,is_clean_plt=is_clean_plt)

    if ret:
        return ret
