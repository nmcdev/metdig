# -*- coding: utf-8 -*-

from metdig.io import get_model_grid

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.onestep.complexgrid_var.spfh import read_spfh
from metdig.onestep.complexgrid_var.wvfl import read_wvfl
import metdig.cal as mdgcal

from metdig.products import diag_moisture as draw_moisture

__all__ = [
    'hgt_uv_tcwv',
    'hgt_uv_rh',
    'hgt_uv_spfh',
    'hgt_uv_wvfl',
]

@date_init('init_time')
def hgt_uv_wvfldiv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                hgt_lev=500, uv_lev=850, wvfldiv_lev=850, smt_stp=1, is_mask_terrain=True,
                area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    _u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=wvfldiv_lev, extent=map_extent)
    _v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=wvfldiv_lev, extent=map_extent)
    _spfh = read_spfh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=wvfldiv_lev, extent=map_extent)
    
    _u = mdgcal.gaussian_filter(_u, smt_stp)
    _v = mdgcal.gaussian_filter(_v, smt_stp)
    _spfh = mdgcal.gaussian_filter(_spfh, smt_stp)

    wvfldiv=mdgcal.water_wapor_flux_divergence(_u,_v,_spfh)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        wvfldiv = mask_terrian(psfc, wvfldiv)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'wvfldiv': wvfldiv}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_moisture.draw_hgt_uv_wvfldiv(hgt, u, v, wvfldiv, map_extent=map_extent,  data_name='cma_gfs', **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    hgt_uv_wvfldiv(area='西南涡',uv_lev=850,wvfldiv_lev=850)
    plt.show()
@date_init('init_time')
def hgt_uv_tcwv(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
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
    tcwv = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='tcwv', extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'vvel': tcwv}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)

    # plot
    if is_draw:
        drawret = draw_moisture.draw_hgt_uv_tcwv(hgt, u, v, tcwv, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def hgt_uv_rh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
              hgt_lev=500, uv_lev=850, rh_lev=850, is_mask_terrain=True,
              area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    rh = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                        data_name=data_name, var_name='rh', level=rh_lev, extent=map_extent)


    # 隐藏被地形遮挡地区
    psfc=None
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        rh = mask_terrian(psfc, rh)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'rh': rh, 'psfc':psfc}
        ret.update({'data': dataret})
        
    # plot
    if is_draw:
        drawret = draw_moisture.draw_hgt_uv_rh(hgt, u, v, rh, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def hgt_uv_spfh(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                hgt_lev=500, uv_lev=850, spfh_lev=850, is_mask_terrain=True,
                area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    spfh = read_spfh(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=spfh_lev, extent=map_extent)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'spfh': spfh}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        spfh = mask_terrian(psfc, spfh)

    # plot
    if is_draw:
        drawret = draw_moisture.draw_hgt_uv_spfh(hgt, u, v, spfh, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
# if __name__ == '__main__':
#     from datetime import datetime
#     hgt_uv_spfh(init_time=datetime(2021,11,7,2),data_name='era5',data_source='cds',
#         uv_lev=850,spfh_lev=850,hgt_lev=850,area=(105,136,20,55))

@date_init('init_time')
def hgt_uv_wvfl(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24,
                hgt_lev=500, uv_lev=850, wvfl_lev=850, is_mask_terrain=True,
                area='全国',  is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    hgt = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour,
                         data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    wvfl = read_wvfl(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=wvfl_lev, extent=map_extent)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        wvfl = mask_terrian(psfc, wvfl)

    if is_return_data:
        dataret = {'hgt': hgt, 'u': u, 'v': v, 'wvfl': wvfl}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_moisture.draw_hgt_uv_wvfl(hgt, u, v, wvfl, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
