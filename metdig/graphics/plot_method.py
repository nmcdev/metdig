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
def graphy_plot(ax, graphy,color='red',linewidth=4,linestyle = "-",):
    
    features = graphy["features"]
    for value in features.values():
        line = value["axes"]
        point = np.array(line["point"])
        if point.size > 0:
            ax.plot(point[:, 0], point[:, 1], color=color, linewidth=linewidth,linestyle=linestyle)

@kwargs_wrapper
def shear_plot(ax, graphy,linewidth=1):
    
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
    for value in features.values():
        line = value["axes"]
        line_type = line["line_type"]
        point = np.array(line["point"])
        dp = np.zeros(point.shape)
        dp[:-1,:] = point[1:,:] - point[:-1,:]
        dp[-1,:] = dp[-2,:]
        length = (dp[:,0]**2 + dp[:,1] **2)**0.5
        dx = -dp[:,1] * line_width/ length
        dy = dp[:,0] * line_width/length

        if line_type =="c":
            ax.plot(point[:,0] - dx ,point[:,1] - dy,"b",linewidth = linewidth)
            ax.plot(point[:, 0] + dx, point[:, 1] + dy, "b",linewidth =  linewidth)
        else:
            ax.plot(point[:, 0] - dx, point[:, 1] - dy, "r",linewidth =  linewidth)
            ax.plot(point[:, 0] + dx, point[:, 1] + dy, "r",linewidth =  linewidth)


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