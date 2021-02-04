# -*- coding: utf-8 -*-

'''
演变
'''
import os
import datetime
import imageio
import copy
import matplotlib.pyplot as plt

from metdig.metdig_hub.lib.utility import save_list
from metdig.metdig_hub.lib.utility import save_animation
from metdig.metdig_hub.lib.utility import mult_process



def model_evolution(init_time=None, fhours=[12, 18, 24, 30, 36], data_name='ecmwf',
                   func=None, func_other_args={}, max_workers=6,
                   output_dir=None, show='list', list_size=(16, 9), 
                   is_clean_plt=False): 
    '''
    
    [演变]
    
    Keyword Arguments:
        init_time {[datetime]} -- [起报时间] (default: {None})
        fhours {[list]} -- [预报时效列表] (default: {None})
        data_name {[str]} -- [模式名] (default: {None})
        func {[type]} -- [函数名] (default: {None})
        func_other_args {function} -- [函数参数字典] (default: {{}})
        max_workers {number} -- [最大进程数] (default: {6})
        output_dir {[type]} -- [输出目录] (default: {None})
        show {str} -- ['list', show all plots in one cell.
                       'animation', show gif animation.] (default: {'list'})
    
    Returns:
        [type] -- [description]
    '''
    # 参数准备
    func_args_all = []
    for fhour in fhours:
        func_args =  copy.deepcopy(func_other_args)
        func_args['init_time'] = init_time
        func_args['fhour'] = fhour
        func_args['data_name'] = data_name
        func_args['is_return_imgbuf'] = True
        func_args_all.append(func_args)

    # 多进程绘图
    all_ret = mult_process(func=func, func_args_all=func_args_all, max_workers=max_workers)
    all_img_buf = [ret['img_buf'] for ret in all_ret]
    all_png_name= [ret['png_name'] for ret in all_ret]

    if show == 'list':
        all_pic = save_list(all_img_buf, output_dir, all_png_name, list_size=list_size, is_clean_plt=is_clean_plt)
        return all_pic
    elif show == 'animation':
        gif_name = 'evolution_{}_{}_{:%Y%m%d%H}_{:03d}_{:03d}.gif'.format(func.__name__, data_name, init_time, fhours[0], fhours[-1])
        gif_path = save_animation(all_img_buf, output_dir, gif_name, is_clean_plt=is_clean_plt)
        return gif_path
        
    return None
