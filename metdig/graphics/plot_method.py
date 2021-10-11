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
def plot_1d(ax, stda, xdim='fcst_time', c='#FF6600', linewidth=3,**kwargs):
    
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_value(xdim)
    curve = ax.plot(x, y, c=c,linewidth=linewidth, **kwargs)

    return curve
