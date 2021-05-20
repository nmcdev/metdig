# -*- coding: utf-8 -*-

'''

'''
import os
import datetime
import copy
import imageio
import matplotlib.pyplot as plt

from metdig.hub.lib.utility import get_nearest_init_time

from metdig.hub.lib.utility import save_animation
from metdig.hub.lib.utility import save_tab
from metdig.hub.lib.utility import save_list
from metdig.hub.lib.utility import mult_process


def modelver_vs_anl(anl_time=None, anl_data_name='ecmwf', ninit=4, init_interval=12, data_name='ecmwf',
                    func=None, func_other_args={}, max_workers=6,
                    output_dir=None, show='animation', tab_size=(30, 18), list_size=(16, 9),
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
    init_time = None
    fhour = None
    if anl_time is None:
        if anl_data_name == 'era5':
            print('era5为再分析数据，请给定anl_time')
            return
        # 获得最近的一次000时效预报数据
        init_time = get_nearest_init_time(24, anl_data_name, func, func_other_args)
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
            func_args['data_name'] = anl_data_name
        else:
            func_args['data_name'] = data_name
        func_args['is_return_imgbuf'] = True
        print(func_args['init_time'], func_args['fhour'], func_args['data_name'])
        func_args_all.append(func_args)

    # 多进程绘图
    all_ret = mult_process(func=func, func_args_all=func_args_all, max_workers=max_workers)
    all_img_buf = [ret['img_buf'] for ret in all_ret]
    all_png_name = [ret['png_name'] for ret in all_ret]

    # 输出
    if show == 'list':
        all_pic = save_list(all_img_buf, output_dir, all_png_name, list_size=list_size, is_clean_plt=is_clean_plt)
        return all_pic
    elif show == 'animation':
        gif_name = 'modelver_vs_anl_{}_{}_{:%Y%m%d%H}_{:03d}_{:03d}.gif'.format(func.__name__, data_name, init_time, ninit, init_interval)
        gif_path = save_animation(all_img_buf, output_dir, gif_name, is_clean_plt=is_clean_plt)
        return gif_path
    elif show == 'tab':
        png_name = 'modelver_vs_anl_{}_{}_{:%Y%m%d%H}_{:03d}_{:03d}.png'.format(func.__name__, data_name, init_time, ninit, init_interval)
        png_path = save_tab(all_img_buf, output_dir, png_name, tab_size=tab_size, is_clean_plt=is_clean_plt)
        return png_path

    return None
