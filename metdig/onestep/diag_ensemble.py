# -*- coding: utf-8 -*-

import numpy as np

from metdig.io import get_model_grid

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.onestep.complexgrid_var.pv_div_uv import read_pv_div_uv
from metdig.onestep.complexgrid_var.get_rain import read_rain
from metdig.onestep.complexgrid_var.vort_uv import read_vort_uv
from metdig.onestep.complexgrid_var.wsp import read_wsp

from metdig.products import diag_ensemble as draw_ensemble

import metdig.utl.utl_stda_grid as utl_stda_grid

import metdig.cal as mdgcal

__all__ = [
    'hgt_spaghetti',
]

@date_init('init_time')
def hgt_spaghetti(data_source='cassandra', data_name='ecmwf_ens', init_time=None, fhour=24,
               area='全国',  is_return_data=False, is_draw=True, **products_kwargs):

    ret = {}
    map_extent = get_map_area(area)

    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                            data_name=data_name, var_name='hgt', level=500, extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt}
        ret.update({'data': dataret})

    if is_draw:
        draw_ensemble.draw_hgt_spaghetti(hgt,map_extent=map_extent,**products_kwargs)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    hgt_spaghetti(init_time='21121008',fhour=84)
    plt.show()