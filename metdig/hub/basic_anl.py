# -*- coding: utf-8 -*-

'''

'''
import sys
import os
import datetime
from concurrent import futures

from metdig.hub.lib.utility import save_animation
from metdig.hub.lib.utility import save_tab
from metdig.hub.lib.utility import save_list
from metdig.hub.lib.utility import mult_process
from metdig.hub.lib.utility import get_onestep_ret_imgbufs
from metdig.hub.lib.utility import get_onestep_ret_pngnames

import logging
_log = logging.getLogger(__name__)

__all__ = [
    'model_basic_anl',
]

def model_basic_anl(func=None, func_other_args=None, max_workers=6,
                   output_dir=None, output_name=None, show='tab', tab_size=(30, 18), list_size=(16, 9),
                   is_clean_plt=False):
    '''

    [基础分析方法，通用模式分析]

    Keyword Arguments:
        func {[type]} -- [函数名或函数名构成的list，当func和func_other_args均为长度大于1的list时，必须保证list长度相同，否则无法一一对应] (default: {None})
        func_other_args {[函数参数字典或函数字典构成的list，当func和func_other_args均为长度大于1的list时，必须保证list长度相同，否则无法一一对应]} -- [函数参数字典] (default: {None})
        max_workers {number} -- [最大进程数] (default: {6})
        output_dir {[str]} -- [输出目录] (default: {None})
        output_name {[str]} -- [输出文件名，仅在show=tab or show=animation时生效，如果不填，则使用默认文件名] (default: {None})
        show {str} -- ['list', show all plots in one cell.
                       'tab', show one plot in each tab page. 
                       'animation', show gif animation.] (default: {'tab'})
        tab_size {tuple} -- [如果show='tab'时生效，输出图片分辨率] (default: {(30, 18)})
        list_size {tuple} -- [如果show='tab'时生效，输出图片分辨率] (default: {(16, 9)})
        is_clean_plt {bool} -- [description] (default: {True})
    '''
    if func is None or func_other_args is None:
        raise Exception('error! func or func_other_args is None')

    if not isinstance(func, list):
        func = [func]
    if not isinstance(func_other_args, list):
        func_other_args = [func_other_args]

    if len(func) == 0:
        raise Exception('error! len(func) == 0')
    if len(func_other_args) == 0:
        raise Exception('error! len(func_other_args) == 0')

    if len(func) > 1 and len(func_other_args) > 1 and len(func) != len(func_other_args):
        raise Exception('error! len(func) !=  len(func_other_args), can not match')

    for _ in func_other_args:
        _['is_return_pngname'] = True
        _['is_return_imgbuf'] = True

    # 多进程绘图
    use_sys_cpu = max(1, os.cpu_count() - 2)  # 可使用的cpu核心数为cpu核心数-2
    max_workers = min(max_workers, use_sys_cpu)  # 最大进程数
    with futures.ProcessPoolExecutor(max_workers=max_workers) as executer:
        if len(func) == 1:
            all_task = [executer.submit(func[0], **b) for b in func_other_args]

        elif len(func_other_args) == 1:
            all_task = [executer.submit(a, **func_other_args[0])for a in func]

        else:
            all_task = [executer.submit(a, **b) for (a, b) in zip(func, func_other_args)]

        # 等待
        futures.wait(all_task, return_when=futures.ALL_COMPLETED)

        # 取返回值
        all_ret = []
        for task in all_task:
            exp = task.exception()
            if exp is None:
                all_ret.append(task.result())
            else:
                _log.debug(exp)
                pass

    all_img_bufs = get_onestep_ret_imgbufs(all_ret)
    all_png_names = get_onestep_ret_pngnames(all_ret)


    # 输出
    ret = None
    if show == 'list':
        ret = save_list(all_img_bufs, output_dir, all_png_names, list_size=list_size, is_clean_plt=is_clean_plt)
    elif show == 'animation':
        if not output_name:
            output_name = 'basic_analysis.gif'
        ret = save_animation(all_img_bufs, output_dir, output_name, is_clean_plt=is_clean_plt)
    elif show == 'tab':
        if not output_name:
            output_name = 'basic_analysis.png'
        ret = save_tab(all_img_bufs, output_dir, output_name, tab_size=tab_size, is_clean_plt=is_clean_plt)

    if ret:
        return ret
