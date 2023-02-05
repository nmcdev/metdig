# -*- coding: utf-8 -*-


import io
import sys
import os
import datetime
import copy

import imageio
import numpy as np
import numba as nb
import matplotlib.pyplot as plt

from concurrent import futures

from IPython.display import Image, display
from io import BytesIO

import logging
_log = logging.getLogger(__name__)


def get_labels_dist(num):
    '''
    [获取label类型图的分布]
    '''
    if num == 1:
        return (1, 1)
    if num == 2:
        return (1, 2)

    if num > 2 and num <= 4:
        return (2, 2)

    if num > 4 and num <= 9:
        return (3, 3)

    if num > 9 and num <= 16:
        return (4, 4)
    if num > 16 and num <= 25:
        return (5, 5)


def get_nearest_init_time(fhour, data_source='', data_name='', func=None, func_other_args={}):
    '''
    以系统时间为起点， 获取最近fhour时预报的起报时间
    '''

    # 以系统时间为起点，固定fhour=0，逐1小时往前推，直至取到第一对init_time fhour=0，目的是获得最近的一次000时效预报数据
    sys_time = datetime.datetime.now().strftime('%Y%m%d%H')  # 系统时间
    sys_time = datetime.datetime.strptime(sys_time, '%Y%m%d%H')
    tag = False
    for i in range(24):  # 逐个往前推
        func_args = copy.deepcopy(func_other_args)
        func_args['init_time'] = sys_time - datetime.timedelta(hours=i)
        func_args['fhour'] = 0
        func_args['data_name'] = data_source
        func_args['data_name'] = data_name
        func_args['is_return_imgbuf'] = True
        func_args['is_draw'] = False # 由于one_step增加is_draw参数，此处仅读取数据不绘图增加效率
        ret = mult_process(func=func, func_args_all=[func_args], max_workers=1, force_max_workers=True)
        if len(ret) > 0:
            tag = True
            break
        else:
            _log.info(f'''{func_args['init_time']} {func_args['fhour']} {data_name} find failed. next.''')
    if tag == True:
        # 取到第一对init_time fhour
        _log.info(f'''{func_args['init_time']} {func_args['fhour']} {data_name} find success. end.''')
        return func_args['init_time']
    else:
        raise Exception('can not get any data! init_time=[{:%Y%m%d%H}-{:%Y%m%d%H}] fhour=24'.format(sys_time, sys_time - datetime.timedelta(hours=23)))
        return None

    return None


def mult_process(func=None, func_args_all=[], max_workers=6, force_max_workers=True):
    '''

    [多进程绘图]

    Keyword Arguments:
        func {[type]} -- [函数 or list] (default: {None})如果是函数，list长度须于func_args_all一致
        func_args_all {list} -- [函数参数] (default: {[]})
        max_workers {number} -- [进程池大小] (default: {6})
        force_max_workers {bool} -- [是否强制使用max_workers参数，默认关闭] (default: {False})

    Returns:
        [list] -- [有效的返回结果]
    '''
    if len(func_args_all) == 0:
        return []

    # 多进程绘图
    if force_max_workers == False:
        use_sys_cpu = max(1, os.cpu_count() - 2)  # 可使用的cpu核心数为cpu核心数-2
        max_workers = min(max_workers, use_sys_cpu)  # 最大进程数
    _log.debug('cpu_count={}, use max_workers={}'.format(os.cpu_count(), max_workers))

    all_ret = []
    # with futures.ProcessPoolExecutor(max_workers=max_workers) as executer:
    # 提交所有绘图任务
    executer=futures.ProcessPoolExecutor(max_workers=max_workers)
    if(isinstance(func,list)):
        all_task = [executer.submit(func[_ifunc], **_) for _ifunc,_ in enumerate(func_args_all)]
    else:
        all_task = [executer.submit(func, **_) for _ in func_args_all]

    # 等待
    futures.wait(all_task, return_when=futures.ALL_COMPLETED)

    # 取返回值
    for task in all_task:
        exp = task.exception()
        if exp is None:
            all_ret.append(task.result())
        else:
            _log.debug(exp)
            pass
    executer.shutdown()
    return all_ret


def save_animation(img_bufs, output_dir, gif_name, fps=2, is_clean_plt=True):
    '''
    保存成gif
    '''
    if len(img_bufs) == 0:
        return None
    gif_path = None
    if output_dir:
        gif_path = os.path.join(output_dir, gif_name)
        with imageio.get_writer(gif_path, format='GIF', mode='I', fps=fps, loop=0) as writer:
            for imgbuf in img_bufs:
                writer.append_data(imgbuf)

    if is_clean_plt == False:
        gif_path = BytesIO()
        with imageio.get_writer(gif_path, format='GIF', mode='I', fps=fps, loop=0) as writer:
            for imgbuf in img_bufs:
                writer.append_data(imgbuf)
        img = Image(data=gif_path.getvalue())
        display(img)

    return gif_path


def save_tab(img_bufs, output_dir, png_name, tab_size=(30, 18),tab_dist=None, is_clean_plt=True):
    '''
    保存成tab，多图叠加
    '''
    if len(img_bufs) == 0:
        return None
    # 开始绘图
    fig = plt.figure(figsize=tab_size)
    if(tab_dist is None):
        nrows, ncols = get_labels_dist(len(img_bufs))
    else:
        nrows=tab_dist[0]
        ncols=tab_dist[1]
    for i, imgbuf in enumerate(img_bufs):
        ax = fig.add_subplot(nrows, ncols, i + 1)
        ax.axis('off')
        ax.imshow(imgbuf)
    plt.tight_layout()  # 调整整体空白
    plt.subplots_adjust(wspace=0.02, hspace=0.02)  # 调整子图间距

    # 输出
    png_path = None
    if output_dir:
        png_path = os.path.join(output_dir, png_name)
        plt.savefig(png_path, dpi=100, bbox_inches='tight')

    if is_clean_plt:
        plt.close(fig)

    return png_path


def save_list(img_bufs, output_dir, png_paths, list_size=(16, 9), is_clean_plt=True):
    '''
    保存成list，多图分开绘制
    '''
    png_path_list = []
    for imgbuf, png_path in zip(img_bufs, png_paths):
        fig = plt.figure(figsize=list_size)
        ax = fig.add_subplot(111)
        ax.axis('off')
        ax.imshow(imgbuf)
        plt.tight_layout()  # 调整整体空白
        plt.subplots_adjust(wspace=0.02, hspace=0.02)  # 调整子图间距# 输出
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            outpng = os.path.join(output_dir, png_path)
            png_path_list.append(outpng)
            plt.savefig(outpng, dpi=200, bbox_inches='tight')
        if is_clean_plt:
            plt.close(fig)
    return png_path_list


def get_onestep_ret_imgbufs(all_ret):
    imgbufs = []
    for ret in all_ret:
        if ret is None:
            continue 
        if 'img_buf' in ret.keys():
            imgbufs.append(ret['img_buf'])
    return imgbufs

def get_onestep_ret_pngnames(all_ret):
    pics = []
    for ret in all_ret:
        if ret is None:
            continue 
        if 'png_name' in ret.keys():
            pics.append(ret['png_name'])
    return pics

def strparsetime(dt):
    # 字符型日期转datetime
    if isinstance(dt, str):
        if len(dt) == 10:
            dt = datetime.datetime.strptime(dt, '%Y%m%d%H')
        elif len(dt) == 8:
            dt = datetime.datetime.strptime(dt, '%y%m%d%H')
        else:
            raise Exception('time must be datetime or str like 2001010100(%Y%m%d%H) or str like 01010100(%y%m%d%H)')
    return dt