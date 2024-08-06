# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.lines as lines

import metdig.graphics.pallete_set as pallete_set
from metdig.graphics.lib.utility import save

import metdig.cal as mdgcal
import metpy.calc as mpcalc
from metpy.units import units
from metdig.graphics.lib.utility import kwargs_wrapper

@kwargs_wrapper
def plot_1d(ax, stda, xdim='fcst_time', c='#FF6600', linewidth=3,**kwargs):
    
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_value(xdim)
    curve = ax.plot(x, y, c=c,linewidth=linewidth, **kwargs)

    return curve



@kwargs_wrapper
def graphy_plot(ax, graphy,color='red',linewidth=4,linestyle = "-", add_clabel=False, cb_text=''):
    
    features = graphy["features"]
    clabel_index = 1
    for value in features.values():
        line = value["axes"]
        point = np.array(line["point"])
        if point.size > 0:
            ax.plot(point[:, 0], point[:, 1], color=color, linewidth=linewidth,linestyle=linestyle)
            if add_clabel:
                mididx = len(point[:, 0]) // 2
                x = point[:, 0][mididx]
                y = point[:, 1][mididx]
                if not cb_text:
                    text = str(clabel_index)
                else:
                    text = str(cb_text)
                ax.text(x, y, text, 
                    color="white", 
                    fontsize=14, 
                    bbox=dict(boxstyle="square,pad=0", 
                            facecolor='gray', 
                            alpha=0.8, ),
                    ha="center",
                    va="center",
                    )
                clabel_index += 1

@kwargs_wrapper
def shear_plot(ax, graphy,linewidth=1, typec_color='blue', typew_color='red', linestyle='-', add_clabel=False, cb_text=''):
    
    slon = ax.transLimits._boxin.x0
    elon = ax.transLimits._boxin.x1
    slat = ax.transLimits._boxin.y0
    elat = ax.transLimits._boxin.y1

    rlon = elon - slon
    rlat = elat - slat
    fig = ax.get_figure()
    map_width = ax.bbox.width / fig.dpi

    line_width = rlon *  0.015/ map_width
    
    features = graphy["features"]
    concat_line_dict = []
    for value in features.values():
        line = value["axes"] # dict_keys(['cycleType', 'grade', 'hand', 'iscycle', 'lenght', 'line_type', 'point', 'value'])
        # print(line['cycleType'], line['grade'], line['hand'], line['iscycle'], line['lenght'])
        line_type = line["line_type"]
        point = np.array(line["point"])
        dp = np.zeros(point.shape)
        dp[:-1,:] = point[1:,:] - point[:-1,:]
        dp[-1,:] = dp[-2,:]
        length = (dp[:,0]**2 + dp[:,1] **2)**0.5
        dx = -dp[:,1] * line_width/ length
        dy = dp[:,0] * line_width/length

        if line_type =="c":
            ax.plot(point[:, 0] - dx ,point[:,1] - dy, typec_color, linewidth=linewidth, linestyle=linestyle)
            ax.plot(point[:, 0] + dx, point[:, 1] + dy, typec_color, linewidth=linewidth, linestyle=linestyle)
        else:
            ax.plot(point[:, 0] - dx, point[:, 1] - dy, typew_color, linewidth=linewidth, linestyle=linestyle)
            ax.plot(point[:, 0] + dx, point[:, 1] + dy, typew_color,linewidth= linewidth, linestyle=linestyle)
        

        if add_clabel:
            # 合并线，根据首尾点判定是否是同一条线，如果是，则合并
            lon_this = point[:, 0]
            lat_this = point[:, 1]
            xst_this = f'{lon_this[0]:.2f}'
            yst_this = f'{lat_this[0]:.2f}'
            xed_this = f'{lon_this[-1]:.2f}'
            yed_this = f'{lat_this[-1]:.2f}'
            is_concat = False
            for i, ll_last in enumerate(concat_line_dict):
                lon_last = ll_last['lon']
                lat_last = ll_last['lat']
                xst_last = f'{lon_last[0]:.2f}'
                yst_last = f'{lat_last[0]:.2f}'
                xed_last = f'{lon_last[-1]:.2f}'
                yed_last = f'{lat_last[-1]:.2f}'
                # print(xst_this, yst_this, xed_this, yed_this, xst_last, yst_last, xed_last, yed_last)
                # 如果(x0,y0) 和lon，lat的开始相同
                if xst_this == xst_last and yst_this == yst_last:
                    # 这条线的开始点和之前的线的开始点相同
                    # print('concat')
                    # print(lon_this[::-1][-1], lon_last[0])
                    # print(lat_this[::-1][-1], lat_last[0])
                    concat_line_dict[i]['lon'] = np.concatenate((lon_this[::-1], lon_last))
                    concat_line_dict[i]['lat'] = np.concatenate((lat_this[::-1], lat_last))
                    is_concat = True
                    break
                elif xst_this == xed_last and yst_this == yed_last:
                    # 这条线的开始点之前的线的结束点相同这
                    # print('concat')
                    # print(lon_last[-1], lon_this[0])
                    # print(lat_last[-1], lat_this[0])
                    concat_line_dict[i]['lon']  = np.concatenate((lon_last, lon_this))
                    concat_line_dict[i]['lat'] = np.concatenate((lat_last, lat_this))
                    is_concat = True
                    break
                elif xed_this == xst_last and yed_this == lat_last[-0]:
                    # 这条线的结束点和之前的线的开始点相同
                    # print('concat')
                    # print(lon_this[-1], lon_last[0])
                    # print(lat_this[-1], lat_last[0])
                    concat_line_dict[i]['lon']  = np.concatenate((lon_this, lon_last))
                    concat_line_dict[i]['lat'] = np.concatenate((lat_this, lat_last))
                    is_concat = True
                    break
                elif xed_this == xed_last and yed_this == yed_last:
                    # 这条线的结束点之前的线的结束点相同
                    # print('concat')
                    # print(lon_last[-1], lon_this[::-1][0])
                    # print(lat_last[-1], lat_this[::-1][0])
                    concat_line_dict[i]['lon']  = np.concatenate((lon_last, lon_this[::-1]))
                    concat_line_dict[i]['lat']  = np.concatenate((lat_last, lat_this[::-1]))
                    is_concat = True
                    break
            if is_concat == False:
                concat_line_dict.append({'lon': lon_this, 'lat': lat_this})
            continue
    if add_clabel:
        # print(f'共{len(concat_line_dict)}条线')
        clabel_index = 1
        for ll in concat_line_dict:
            if ll['lon'][0] > ll['lon'][-1]: # 固定标记经度小的那个值
                x = ll['lon'][-1]
                y = ll['lat'][-1]
            else:
                x = ll['lon'][0]
                y = ll['lat'][0]
            if not cb_text:
                text = str(clabel_index)
            else:
                text = str(cb_text)
            ax.text(x, y, text, 
                color="white", 
                fontsize=14, 
                bbox=dict(boxstyle="square,pad=0", 
                        facecolor='gray', 
                        alpha=0.8, ),
                ha="center",
                va="center",
                )
            clabel_index += 1

def jet_plot(ax, graphy):
    features = graphy["features"]
    for value in features.values():
        line = value["axes"]
        point = np.array(line["point"])
        npoint = len(line["point"])

        ns = npoint -1
        dx = 0
        dy = 0
        while ns >0:
            ns -= 1
            dx = point[npoint-1,0] - point[ns,0]
            dy = point[npoint-1,1] - point[ns,1]
            dis = (dx**2 + dy**2)**0.5
            if dis > 0.3:
                break

        ax.arrow(point[ns,0],point[ns,1],dx*0.01,dy*0.01,head_width=0.3,head_length = 0.3,fc = "yellow",ec = "yellow")
        ax.plot(point[:ns, 0], point[:ns, 1], "yellow", linewidth=2)