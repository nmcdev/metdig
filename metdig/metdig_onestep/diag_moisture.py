# -*- coding: utf-8 -*-

from metdig.metdig_io import get_model_grid

from metdig.metdig_onestep.lib.utility import get_map_area
from metdig.metdig_onestep.lib.utility import mask_terrian
from metdig.metdig_onestep.lib.utility import date_init

from metdig.metdig_onestep.complexgrid_var.spfh import read_spfh
from metdig.metdig_onestep.complexgrid_var.wvfl import read_wvfl

from metdig.metdig_products.diag_moisture import draw_hgt_uv_tcwv
from metdig.metdig_products.diag_moisture import draw_hgt_uv_rh
from metdig.metdig_products.diag_moisture import draw_hgt_uv_spfh
from metdig.metdig_products.diag_moisture import draw_hgt_uv_wvfl


@date_init('init_time')
def hgt_uv_tcwv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                hgt_lev=500, uv_lev=850, is_mask_terrain=True,
                area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    tcwv = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='tcwv', extent=map_extent, x_percent=0.2, y_percent=0.1)
    
    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'vvel': tcwv}
        ret.update({'data': dataret})


    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent, x_percent=0.2, y_percent=0.1)
        hgt = mask_terrian(psfc, hgt_lev, hgt)
        u = mask_terrian(psfc, uv_lev, u)
        v = mask_terrian(psfc, uv_lev, v)

    # plot
    if is_draw:
        drawret = draw_hgt_uv_tcwv(hgt, u, v, tcwv, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    return ret



@date_init('init_time')
def hgt_uv_rh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
              hgt_lev=500, uv_lev=850, rh_lev=850, is_mask_terrain=True,
              area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    rh = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='rh', level=rh_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'rh': rh}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent, x_percent=0.2, y_percent=0.1)
        hgt = mask_terrian(psfc, hgt_lev, hgt)
        u = mask_terrian(psfc, uv_lev, u)
        v = mask_terrian(psfc, uv_lev, v)
        rh = mask_terrian(psfc, rh_lev, rh)

    # plot
    if is_draw:
        drawret = draw_hgt_uv_rh(hgt, u, v, rh, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    return ret



@date_init('init_time')
def hgt_uv_spfh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                hgt_lev=500, uv_lev=850, spfh_lev=850, is_mask_terrain=True,
                area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    spfh = read_spfh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=spfh_lev, extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'spfh': spfh}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent, x_percent=0.2, y_percent=0.1)
        hgt = mask_terrian(psfc, hgt_lev, hgt)
        u = mask_terrian(psfc, uv_lev, u)
        v = mask_terrian(psfc, uv_lev, v)
        spfh = mask_terrian(psfc, spfh_lev, spfh)

    # plot
    if is_draw:
        drawret = draw_hgt_uv_spfh(hgt, u, v, spfh, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    return ret



@date_init('init_time')
def hgt_uv_wvfl(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                hgt_lev=500, uv_lev=850, wvfl_lev=850, is_mask_terrain=True,
                area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    wvfl = read_wvfl(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=wvfl_lev, extent=map_extent)
    
    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent, x_percent=0.2, y_percent=0.1)
        hgt = mask_terrian(psfc, hgt_lev, hgt)
        u = mask_terrian(psfc, uv_lev, u)
        v = mask_terrian(psfc, uv_lev, v)
        wvfl = mask_terrian(psfc, wvfl_lev, wvfl)

    # plot
    if is_draw:
        drawret = draw_hgt_uv_wvfl(hgt, u, v, wvfl, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    return ret

if __name__ == '__main__':
    import datetime
    import matplotlib.pyplot as plt
    hgt_uv_wvfl(init_time='2020110108',add_city=False,data_source='era5')
    plt.show()