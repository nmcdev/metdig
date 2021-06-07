# -*- coding: utf-8 -*-

'''
演变
'''
import os
import datetime
import copy

from metdig.hub.lib.utility import save_list
from metdig.hub.lib.utility import save_animation,save_tab
from metdig.hub.lib.utility import mult_process
from metdig.hub.lib.utility import get_onestep_ret_imgbufs
from metdig.hub.lib.utility import get_onestep_ret_pngnames



def model_evolution(init_time=None, fhours=[12, 18, 24, 30, 36], data_name='ecmwf',
                   func=None, func_other_args={}, max_workers=6,
                   output_dir=None, show='list',tab_size=(30, 18), list_size=(16, 9), 
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
        tab_size {tuple} -- [如果show='tab'时生效，输出图片分辨率] (default: {(30, 18)})
    
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
        func_args['is_return_pngname'] = True
        func_args['is_return_imgbuf'] = True
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
        gif_name = 'evolution_{}_{}_{:%Y%m%d%H}_{:03d}_{:03d}.gif'.format(func.__name__, data_name, init_time, fhours[0], fhours[-1])
        ret = save_animation(all_img_bufs, output_dir, gif_name, is_clean_plt=is_clean_plt)

    elif show == 'tab':
        png_name = 'evolution_{}_{}_{:%Y%m%d%H}_{:03d}_{:03d}.png'.format(func.__name__, 'models', init_time, fhours[0], fhours[-1])
        ret = save_tab(all_img_bufs, output_dir, png_name, tab_size=tab_size, is_clean_plt=is_clean_plt)
        
    if ret:
        return ret


def analysis_evolution(init_time=None, data_name='era5',data_source='cds',
                   func=None, func_other_args={}, max_workers=6,
                   output_dir=None, show='list',tab_size=(30, 18), list_size=(16, 9), 
                   is_clean_plt=False): 
    '''
    
    [演变]
    
    Keyword Arguments:
        init_time {[list]} -- [分析时间,datetime] (default: {None})
        data_name {[str]} -- [模式名] (default: {'era5'})
        data_source {[str]} -- [数据服务名] (default: {'cds'})
        func {[type]} -- [函数名] (default: {None})
        func_other_args {function} -- [函数参数字典] (default: {{}})
        max_workers {number} -- [最大进程数] (default: {6})
        output_dir {[type]} -- [输出目录] (default: {None})
        show {str} -- ['list', show all plots in one cell.
                       'animation', show gif animation.] (default: {'list'})
        tab_size {tuple} -- [如果show='tab'时生效，输出图片分辨率] (default: {(30, 18)})
    
    Returns:
        [type] -- [description]
    '''
    # 参数准备
    func_args_all = []
    for iinit in init_time:
        func_args =  copy.deepcopy(func_other_args)
        func_args['init_time'] = iinit
        func_args['fhour'] = 0
        func_args['data_name'] = data_name
        func_args['data_source'] = data_source
        func_args['is_return_pngname'] = True
        func_args['is_return_imgbuf'] = True
        func_args_all.append(func_args)

    # 多进程绘图
    all_ret = mult_process(func=func, func_args_all=func_args_all, max_workers=max_workers)
    all_img_bufs = get_onestep_ret_imgbufs(all_ret)
    all_png_names = get_onestep_ret_pngnames(all_ret)


    ret = None
    if show == 'list':
        ret = save_list(all_img_bufs, output_dir, all_png_names, list_size=list_size, is_clean_plt=is_clean_plt)
    elif show == 'animation':
        gif_name = 'evolution_{}_{}_{:%Y%m%d%H}_{:%Y%m%d%H}.gif'.format(func.__name__, data_name, init_time[0], init_time[-1])
        ret = save_animation(all_img_bufs, output_dir, gif_name, is_clean_plt=is_clean_plt)

    elif show == 'tab':
        png_name = 'evolution_{}_{}_{:%Y%m%d%H}_{:%Y%m%d%H}.png'.format(func.__name__, 'models', init_time[0], init_time[-1])
        ret = save_tab(all_img_bufs, output_dir, png_name, tab_size=tab_size, is_clean_plt=is_clean_plt)
        
    if ret:
        return ret