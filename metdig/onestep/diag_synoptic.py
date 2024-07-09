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

from metdig.products import diag_synoptic as draw_synoptic

import metdig.utl.utl_stda_grid as utl_stda_grid

import metdig.cal as mdgcal

__all__ = [
    'vpbt_img',
    'irbt_img',
    'uvstream_wsp',
    'syn_composite',
    'hgt_uv_prmsl',
    'hgt_uv_rain',
    'hgt_uv_wsp',
    'pv_div_uv',
]

@date_init('init_time')
def vpbt_img(data_source='cassandra', data_name='cma_gfs', init_time=None, fhour=24,
               is_mask_terrain=True,
               area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    vpbt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='vpbt',  extent=map_extent)

    if is_return_data:
        dataret = {'vpbt': vpbt}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_synoptic.draw_vpbt(vpbt, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
# if __name__=='__main__':
#     import matplotlib.pyplot as plt
#     vpbt_img(data_source='cassandra',data_name='ecmwf')
#     plt.show()

@date_init('init_time')
def irbt_img(data_source='cassandra', data_name='cma_gfs', init_time=None, fhour=24,
               is_mask_terrain=True,
               area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    irbt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='irbt',  extent=map_extent)

    if is_return_data:
        dataret = {'irbt': irbt}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_synoptic.draw_irbt(irbt, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    
@date_init('init_time')
def uvstream_wsp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
               uv_lev=200, is_mask_terrain=True,
               area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)

    # calculate
    wsp = mdgcal.wind_speed(u, v)

    if is_return_data:
        dataret = {'u': u, 'v': v, 'wsp': wsp}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        wsp = mask_terrian(psfc, wsp)

    # plot
    if is_draw:
        drawret = draw_synoptic.draw_uvstream_wsp(u, v, wsp, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def syn_composite(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                  hgt_lev=500, uv_lev=850, wsp_lev=200, vort_lev=500, is_mask_terrain=True,
                  area='全国',  is_return_data=False, is_draw=True, add_city=False, add_background_style=False,
                  **products_kwargs):
    ret = {}
    # get area
    map_extent = get_map_area(area)

    # get data
    vort500, u500, v500 = read_vort_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=vort_lev, extent=map_extent)
    wsp200, u200, v200 = read_wsp(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=wsp_lev, extent=map_extent)
    hgt500 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                            data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u850 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v850 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    prmsl = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='prmsl', extent=map_extent)
    tcwv = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='tcwv', extent=map_extent)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt500 = mask_terrian(psfc, hgt500)
        vort500 = mask_terrian(psfc, vort500)
        u850 = mask_terrian(psfc, u850)
        v850 = mask_terrian(psfc, v850)

    if is_return_data:
        dataret = {'hgt': hgt500, 'u850': u850, 'v850': v850, 'wsp200': wsp200, 'prmsl': prmsl}
        ret.update({'data': dataret})

    prmsl_attrs = prmsl.attrs
    prmsl = prmsl.rolling(lon=10, lat=10, min_periods=1, center=True).mean()
    prmsl.attrs = prmsl_attrs

    vort500_attrs = vort500.attrs
    vort500 = vort500.rolling(lon=10, lat=10, min_periods=1, center=True).mean()
    vort500.attrs = vort500_attrs

    # plot
    if is_draw:
        drawret = draw_synoptic.draw_syn_composite(hgt500, vort500, u850, v850, wsp200, prmsl, tcwv,
                                                   map_extent=map_extent, add_city=add_city, add_background_style=add_background_style,
                                                   **products_kwargs)

        ret.update(drawret)

    if ret:
        return ret

# if __name__ == '__main__':
#     import matplotlib.pyplot as plt
#     syn_composite(uv_lev=925,hgt_lev=200)
#     plt.show()

@date_init('init_time')
def hgt_uv_prmsl(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                 hgt_lev=500, uv_lev=850, is_mask_terrain=True,
                 area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}
    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    prmsl = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='prmsl', extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'prmsl': prmsl}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)

    # plot
    if is_draw:
        drawret = draw_synoptic.draw_hgt_uv_prmsl(hgt, u, v, prmsl, map_extent=map_extent, **products_kwargs)

        ret.update(drawret)

    if ret:
        return ret
if __name__=='__main__':
    import matplotlib.pyplot as plt
    from datetime import datetime
    ret=hgt_uv_prmsl(data_source='cmadaas',data_name='cma_ra',init_time=datetime(2023,1,3,8),fhour=0,is_return_data=True,is_draw=True)
    plt.show()

@date_init('init_time')
def hgt_uv_rain(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,atime=6,
                  hgt_lev=500, uv_lev=850, is_mask_terrain=True,
                  area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    if(int(atime/2) >=3 ):
        atime_mid=int(atime/2)
    else:
        atime_mid=atime
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour-atime_mid,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour-atime_mid, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour-atime_mid, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    rain06 = read_rain(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, atime=atime, extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'rain06': rain06}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour-atime_mid, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)

    # plot
    if is_draw:
        drawret = draw_synoptic.draw_hgt_uv_rain06(hgt, u, v, rain06, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    hgt_uv_rain(data_source='cmadaas')
    plt.show()

@date_init('init_time')
def hgt_uv_wsp(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
               hgt_lev=500, uv_lev=850, is_mask_terrain=True,
               area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)

    # calculate
    wsp = mdgcal.wind_speed(u, v)

    # 隐藏被地形遮挡地区
    psfc=None
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        wsp = mask_terrian(psfc, wsp)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'wsp': wsp, 'psfc': psfc}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_synoptic.draw_hgt_uv_wsp(hgt, u, v, wsp, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

# if __name__=='__main__':
#     from datetime import datetime
#     hgt_uv_wsp(init_time=datetime(2022,1,31,14),data_name='era5',data_source='cds',fhour=0)

@date_init('init_time')
def pv_div_uv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
              lvl_ana=200, levels=[700, 600, 500, 400, 300, 250, 200, 100], is_mask_terrain=True,
              area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    pv, div, u, v = read_pv_div_uv(data_source=data_source, init_time=init_time, fhour=fhour,
                                   data_name=data_name, lvl_ana=lvl_ana, levels=levels, extent=map_extent)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        pv = mask_terrian(psfc, pv)
        div = mask_terrian(psfc, div)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        
    if is_return_data:
        dataret = {'pv': pv, 'u': u, 'v': v, 'div': div}
        ret.update({'data': dataret})
    # smooth
    pv = mdgcal.smooth_n_point(pv, 9, 2)
    div = mdgcal.smooth_n_point(div, 9, 2)

    # plot
    if is_draw:
        drawret = draw_synoptic.draw_pv_div_uv(pv, div, u, v, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
