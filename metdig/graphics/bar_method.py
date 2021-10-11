# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.lines as lines
from pint import unit

import metdig.graphics.pallete_set as pallete_set
from metdig.graphics.lib.utility import save

import metdig.cal as mdgcal
import metpy.calc as mpcalc
from metpy.units import units
from metdig.graphics.lib.utility import kwargs_wrapper

@kwargs_wrapper
def bar_1d(ax, stda, xdim='fcst_time', color='#FF6600', width=0.1,**kwargs):
    
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_value(xdim)
    curve = ax.bar(x, y, color=color,width=width, **kwargs)

    return curve

def bars_autolabel(ax, rects):
    for rect in rects:
        height = rect.get_height()
        if(height > 0):
            ax.annotate('%.2f' % height,
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')