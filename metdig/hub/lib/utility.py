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


def get_labels_dist(num):
    '''
    [获取label类型图的分布]
    '''
    if num == 1:
        return (1, 1)
    if num == 2:
        return (2, 1)

    if num > 2 and num <= 4:
        return (2, 2)

    if num > 4 and num <= 9:
        return (3, 3)

    if num > 9 and num <= 16:
        return (4, 4)
    if num > 16 and num <= 25:
        return (5, 5)


def get_nearest_init_time(fhour, data_name='', func=None, func_other_args={}):
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
        func_args['data_name'] = data_name
        func_args['is_return_imgbuf'] = True
        func_args['is_draw'] = False # 由于one_step增加is_draw参数，此处仅读取数据不绘图增加效率
        ret = mult_process(func=func, func_args_all=[func_args], max_workers=1, force_max_workers=True)
        if len(ret) > 0:
            tag = True
            break
        else:
            print(func_args['init_time'], func_args['fhour'], data_name, 'find failed. next.')
    if tag == True:
        # 取到第一对init_time fhour
        print(func_args['init_time'], func_args['fhour'], data_name, 'find success. end.')
        return func_args['init_time']
    else:
        print('can not get any data! init_time=[{:%Y%m%d%H}-{:%Y%m%d%H}] fhour=24'.format(sys_time, sys_time - datetime.timedelta(hours=23)))
        return None

    return None


def mult_process(func=None, func_args_all=[], max_workers=6, force_max_workers=False):
    '''

    [多进程绘图]

    Keyword Arguments:
        func {[type]} -- [函数] (default: {None})
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
    # print('cpu_count={}, use max_workers={}'.format(os.cpu_count(), max_workers))

    all_ret = []

    with futures.ProcessPoolExecutor(max_workers=max_workers) as executer:
        # 提交所有绘图任务
        all_task = [executer.submit(func, **_) for _ in func_args_all]

        # 等待
        futures.wait(all_task, return_when=futures.ALL_COMPLETED)

        # 取返回值
        for task in all_task:
            exp = task.exception()
            if exp is None:
                all_ret.append(task.result())
            else:
                print(exp)
                pass
    return all_ret


def save_animation(img_bufs, output_dir, gif_name, is_clean_plt=True):
    '''
    保存成gif
    '''
    if len(img_bufs) == 0:
        return None
    gif_path = None
    if output_dir:
        gif_path = os.path.join(output_dir, gif_name)
        with imageio.get_writer(gif_path, format='GIF', mode='I', fps=1, loop=0) as writer:
            for imgbuf in img_bufs:
                writer.append_data(imgbuf)

    if is_clean_plt == False:
        gif_path = BytesIO()
        with imageio.get_writer(gif_path, format='GIF', mode='I', fps=1, loop=0) as writer:
            for imgbuf in img_bufs:
                writer.append_data(imgbuf)
        img = Image(data=gif_path.getvalue())
        display(img)

    return gif_path


'''
def save_animation_bak(img_bufs, output_dir, gif_name):
    # 
    # 保存成gif
    # 
    if len(img_bufs) == 0:
        return None
        
    gif_path = None
    if output_dir:
        gif_path = os.path.join(output_dir, gif_name)
        print(gif_name)
        # with imageio.get_writer(gif_path, mode='I', fps=1, loop=0) as writer:
        #     for imgbuf in img_bufs:
        #         writer.append_data(imgbuf)

        import matplotlib.animation as animation
        fig = plt.figure(figsize=(16, 9))
        ax = fig.add_subplot(111)
        ax.axis('off')
        ims = []
        for i, imgbuf in enumerate(img_bufs):
            im = ax.imshow(imgbuf, animated=True)
            if i == 0:
                ax.imshow(imgbuf)  # show an initial one first
            ims.append([im])
        ani = animation.ArtistAnimation(fig, ims, interval=1000, repeat_delay=1000, repeat=True, blit=True)
        print(gif_name)
        ani.save(gif_path, writer='pillow')
        # plt.show()

        # plt.close(fig)

    return gif_path
'''


def save_tab(img_bufs, output_dir, png_name, tab_size=(30, 18), is_clean_plt=True):
    '''
    保存成tab，多图叠加
    '''
    if len(img_bufs) == 0:
        return None
    # 开始绘图
    fig = plt.figure(figsize=tab_size)
    nrows, ncols = get_labels_dist(len(img_bufs))
    for i, imgbuf in enumerate(img_bufs):
        # print(imgbuf.shape)
        ax = fig.add_subplot(nrows, ncols, i + 1)
        ax.axis('off')
        ax.imshow(imgbuf)
    plt.tight_layout()  # 调整整体空白
    plt.subplots_adjust(wspace=0.02, hspace=0.02)  # 调整子图间距

    # 输出
    png_path = None
    if output_dir:
        png_path = os.path.join(output_dir, png_name)
        plt.savefig(png_path, idpi=200, bbox_inches='tight')

    if is_clean_plt:
        plt.close(fig)

    return png_path


def save_list(img_bufs, output_dir, png_names, list_size=(16, 9), is_clean_plt=True):
    '''
    保存成list，多图分开绘制
    '''
    png_path_list = []
    for imgbuf, png_name in zip(img_bufs, png_names):
        fig = plt.figure(figsize=list_size)
        ax = fig.add_subplot(111)
        ax.axis('off')
        ax.imshow(imgbuf)
        plt.tight_layout()  # 调整整体空白
        plt.subplots_adjust(wspace=0.02, hspace=0.02)  # 调整子图间距# 输出
        if output_dir:
            png_path = os.path.join(output_dir, png_name)
            png_path_list.append(png_path)
            plt.savefig(png_path, idpi=200, bbox_inches='tight')
        if is_clean_plt:
            plt.close(fig)
    return png_path_list
