import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from colorspacious import cspace_converter
from collections import OrderedDict

import os
import sys
import fnmatch

sys.path.append(r'E:\PyProject\metdig_dev')


import metdig.metdig_graphics.cmap.cm as cm_collected

gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))


def plot_color_gradients(cmap_list=[], cmap_type='guide', outdir='./'):

    outpng = os.path.join(outdir, cmap_type + '.png')
    if not os.path.exists(os.path.dirname(outpng)):
        os.makedirs(os.path.dirname(outpng))

    nrows = len(cmap_list)
    fig = plt.figure(figsize=(16, 0.4 * nrows + 0.4))
    axes = fig.subplots(nrows=nrows)
    fig.subplots_adjust(top=0.95, bottom=0.01, left=0.2, right=0.99)
    axes[0].set_title(cmap_type + ' colormaps', fontsize=14)

    for ax, name in zip(axes, cmap_list):
        cmap = cm_collected.get_cmap(cmap_type + '/' + name)
        print(cmap_type + '/' + name, cmap.N)
        ax.imshow(gradient, aspect='auto', cmap=cmap)
        pos = list(ax.get_position().bounds)
        x_text = pos[0] - 0.01
        y_text = pos[1] + pos[3] / 2.
        fig.text(x_text, y_text, name, va='center', ha='right', fontsize=10)

    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axes:
        ax.set_axis_off()

    plt.savefig(outpng, idpi=200, bbox_inches='tight')
    plt.close(fig)


files = fnmatch.filter(os.listdir('../colormaps_met/'), '*.rgb')
cmap_list = list(map(lambda x: x[:-4], files))
plot_color_gradients(cmap_list=cmap_list, cmap_type='met', outdir='./')

cmap_list = ['cs' + str(x) for x in range(1, 47)]
plot_color_gradients(cmap_list=cmap_list, cmap_type='guide', outdir='./')

files = fnmatch.filter(os.listdir('../colormaps_ncl/'), '*.rgb')
cmap_list = list(map(lambda x: x[:-4], files))
plot_color_gradients(cmap_list=cmap_list, cmap_type='ncl', outdir='./')
