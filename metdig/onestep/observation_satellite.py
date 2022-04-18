# -*- coding: utf-8 -*-

import datetime
import numpy as np

from metdig.io.cassandra import get_model_grid
from metdig.io.cassandra import get_obs_stations
from metdig.io.cassandra import get_fy_awx

from metdig.onestep.complexgrid_var.div_uv import read_div_uv
from metdig.onestep.complexgrid_var.pv_div_uv import read_pv_div_uv
from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import mask_terrian
from metdig.onestep.lib.utility import date_init

from metdig.products import observation_satellite as draw_obssate

import metdig.cal as mdgcal

__all__ = [
    'fy2g_ir1_hgt_uv_wsp',
    'fy4air_sounding_hgt',
]

def fy4a_c009_hgt_uv_prmsl(ir_obs_time=None,
                        init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
                        hgt_lev=500,uv_lev=850,
                        is_mask_terrain=True,
                        area=[70,140,15,55], is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=9, extent=map_extent)
    hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    prmsl = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='prmsl', extent=map_extent)

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
    prmsl = mdgcal.gaussian_filter(prmsl, sigma=2, order=0)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'prmsl': prmsl}
        ret.update({'data': dataret})

    # plot
    if is_draw:

        drawret = draw_obssate.draw_fy4a_c009_hgt_uv_prmsl(ir, hgt, u, v, prmsl, map_extent=map_extent,**products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

if __name__=='__main__':
    import matplotlib.pyplot as plt
    fy4a_c009_hgt_uv_prmsl(ir_obs_time=datetime.datetime(2022,4,12,8),
        init_time=datetime.datetime(2022,4,12,8),fhour=3,add_city=False)
    plt.show()

def fy4a_c012_hgt_uv_prmsl(ir_obs_time=None,
                        init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
                        hgt_lev=500,uv_lev=850,
                        is_mask_terrain=True,
                        area=[70,140,15,55], is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=12, extent=map_extent)
    hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    prmsl = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='prmsl', extent=map_extent)

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
    prmsl = mdgcal.gaussian_filter(prmsl, sigma=2, order=0)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'prmsl': prmsl}
        ret.update({'data': dataret})

    # plot
    if is_draw:

        drawret = draw_obssate.draw_fy4a_c012_hgt_uv_prmsl(ir, hgt, u, v, prmsl, map_extent=map_extent,**products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

if __name__=='__main__':
    import matplotlib.pyplot as plt
    fy4a_c012_hgt_uv_prmsl(ir_obs_time=datetime.datetime(2022,4,12,8),
        init_time=datetime.datetime(2022,4,12,8),fhour=3,add_city=False)
    plt.show()

def fy4a_c012_hgt_uv_cape(ir_obs_time=None,
                        init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
                        hgt_lev=500,uv_lev=850,
                        is_mask_terrain=True,
                        area=[70,140,15,55], is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=12, extent=map_extent)
    hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    cape = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='cape', extent=map_extent)

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
    cape = mdgcal.gaussian_filter(cape, sigma=1, order=0)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'cape': cape}
        ret.update({'data': dataret})

    # plot
    if is_draw:

        drawret = draw_obssate.draw_fy4a_c012_hgt_uv_cape(ir, hgt, u, v, cape, map_extent=map_extent,**products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

# def fy4a_c012_hgt_uv_pv(ir_obs_time=None,
#                         init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
#                         hgt_lev=500,uv_lev=850,pv_lev=200,
#                         is_mask_terrain=True,
#                         area=[70,140,15,55], is_return_data=False, is_draw=True, **products_kwargs):
#     ret = {}

#     # get area
#     map_extent = get_map_area(area)

#     # get data
#     ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=12, extent=map_extent)
#     hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
#     u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
#     v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
#     pv, _div, _u, _v = read_pv_div_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, lvl_ana=pv_lev, extent=map_extent,
#                                 levels=[400, 300, 250, 200, 100])

#     hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
#     pv = mdgcal.gaussian_filter(pv, sigma=1, order=0)

#     # 隐藏被地形遮挡地区
#     if is_mask_terrain:
#         psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
#         hgt = mask_terrian(psfc, hgt)
#         u = mask_terrian(psfc, u)
#         v = mask_terrian(psfc, v)
#         pv = mask_terrian(psfc, pv)

#     if is_return_data:
#         dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'pv': pv}
#         ret.update({'data': dataret})

#     # hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

#     # plot
#     if is_draw:

#         drawret = draw_obssate.draw_fy4a_c012_hgt_uv_pv(ir, hgt, u, v, pv, map_extent=map_extent,**products_kwargs)
#         ret.update(drawret)

#     if ret:
#         return ret

def fy4a_c012_hgt_uv_pv(ir_obs_time=None,
                        init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
                        hgt_lev=500,uv_lev=850,pv_lev=200,
                        is_mask_terrain=True,
                        area=[70,140,15,55], is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=12, extent=map_extent)
    hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    pv, _div, _u, _v = read_pv_div_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, lvl_ana=pv_lev, extent=map_extent,
                                levels=[400, 300, 250, 200, 100])

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
    pv = mdgcal.gaussian_filter(pv, sigma=1, order=0)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        pv = mask_terrian(psfc, pv)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'pv': pv}
        ret.update({'data': dataret})

    # hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

    # plot
    if is_draw:

        drawret = draw_obssate.draw_fy4a_c012_hgt_uv_pv(ir, hgt, u, v, pv, map_extent=map_extent,**products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

def fy4a_c009_hgt_uv_wsp(ir_obs_time=None,
                        init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
                        hgt_lev=500,uv_lev=850,wsp_lev=200,
                        is_mask_terrain=True,
                        area=[70,140,15,55], is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=9, extent=map_extent)
    hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    u_wsp = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=wsp_lev, extent=map_extent)
    v_wsp = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=wsp_lev, extent=map_extent)

    wsp=mdgcal.other.wind_speed(u_wsp,v_wsp)

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
    wsp = mdgcal.gaussian_filter(wsp, sigma=1, order=0)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        wsp = mask_terrian(psfc, wsp)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'wsp': wsp}
        ret.update({'data': dataret})

    # hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

    # plot
    if is_draw:

        drawret = draw_obssate.draw_fy4a_c009_hgt_uv_wsp(ir, hgt, u, v, wsp, map_extent=map_extent,**products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

def fy4a_c012_hgt_uv_div(ir_obs_time=None,
                        init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
                        hgt_lev=500,uv_lev=850,div_lev=850,
                        is_mask_terrain=True,
                        area=[70,140,15,55], is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=12, extent=map_extent)
    hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    div, _u, _v = read_div_uv(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, level=div_lev, extent=map_extent)

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
    div = mdgcal.gaussian_filter(div, sigma=1, order=0)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        div = mask_terrian(psfc, div)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'div': div}
        ret.update({'data': dataret})

    # hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

    # plot
    if is_draw:

        drawret = draw_obssate.draw_fy4a_c012_hgt_uv_div(ir, hgt, u, v, div, map_extent=map_extent,
            **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

def fy4a_c012_hgt_uv_spfh(ir_obs_time=None,
                        init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
                        hgt_lev=500,uv_lev=850,spfh_lev=850,
                        is_mask_terrain=True,
                        area=[70,140,15,55], is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=12, extent=map_extent)
    hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    spfh = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='spfh',level=spfh_lev, extent=map_extent)

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
    spfh = mdgcal.gaussian_filter(spfh, sigma=1, order=0)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        spfh = mask_terrian(psfc, spfh)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'spfh': spfh}
        ret.update({'data': dataret})

    # hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

    # plot
    if is_draw:

        drawret = draw_obssate.draw_fy4a_c012_hgt_uv_spfh(ir, hgt, u, v, spfh, map_extent=map_extent,
            **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

def fy4a_c012_hgt_uv_wsp(ir_obs_time=None,
                        init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
                        hgt_lev=500,uv_lev=850,wsp_lev=200,
                        is_mask_terrain=True,
                        area=[70,140,15,55], is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=12, extent=map_extent)
    hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    u_wsp = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=wsp_lev, extent=map_extent)
    v_wsp = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=wsp_lev, extent=map_extent)

    wsp=mdgcal.other.wind_speed(u_wsp,v_wsp)

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
    wsp = mdgcal.gaussian_filter(wsp, sigma=1, order=0)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        wsp = mask_terrian(psfc, wsp)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'wsp': wsp}
        ret.update({'data': dataret})

    # hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

    # plot
    if is_draw:

        drawret = draw_obssate.draw_fy4a_ir1_hgt_uv_wsp(ir, hgt, u, v, wsp, map_extent=map_extent,
            **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

def fy2g_ir1_hgt_uv_wsp(ir_obs_time=None,
                        init_time=None,fhour=12,data_name='cma_gfs',data_source='cmadaas',
                        hgt_lev=500,uv_lev=850,wsp_lev=200,
                        is_mask_terrain=True,
                        area=[50,145,5,60], is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy2g', var_name='tbb', channel=2, extent=map_extent)
    hgt = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent)
    u = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent)
    v = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent)
    u_wsp = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='u', level=wsp_lev, extent=map_extent)
    v_wsp = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='v', level=wsp_lev, extent=map_extent)

    wsp=mdgcal.other.wind_speed(u_wsp,v_wsp)

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)
    wsp = mdgcal.gaussian_filter(wsp, sigma=1, order=0)

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc = get_model_grid(init_time=init_time, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent)
        hgt = mask_terrian(psfc, hgt)
        u = mask_terrian(psfc, u)
        v = mask_terrian(psfc, v)
        wsp = mask_terrian(psfc, wsp)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'u': u, 'v': v, 'wsp': wsp}
        ret.update({'data': dataret})

    # hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

    # plot
    if is_draw:

        drawret = draw_obssate.draw_fy2g_ir1_hgt_uv_wsp(ir, hgt, u, v, wsp, map_extent=map_extent,
            **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

def fy4air_sounding_hgt(ir_obs_time=None, ir_channel=9,
                        sounding_obs_time=None,
                        hgt_init_time=None, hgt_fhour=24,
                        is_mask_terrain=True,
                        area='全国', is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    # get area
    map_extent = get_map_area(area)

    # get data
    ir = get_fy_awx(obs_time=ir_obs_time, data_name='fy4al1', var_name='tbb', channel=ir_channel, extent=map_extent)
    hgt = get_model_grid(init_time=hgt_init_time, fhour=hgt_fhour, data_name='ecmwf', var_name='hgt', level=500, extent=map_extent)
    sounding_wsp = get_obs_stations(obs_time=sounding_obs_time, data_name='plot_high', var_name='wsp', level=500, extent=map_extent)
    sounding_wdir = get_obs_stations(obs_time=sounding_obs_time, data_name='plot_high', var_name='wdir', level=500, extent=map_extent)

    # 计算uv
    sounding_u, sounding_v = mdgcal.wind_components(sounding_wsp, sounding_wdir)
    # 过滤超过100的uv
    sounding_u.stda.where((sounding_u.stda.values < 100) & (sounding_v.stda.values < 100), np.nan)
    sounding_v.stda.where((sounding_u.stda.values < 100) & (sounding_v.stda.values < 100), np.nan)

    if is_return_data:
        dataret = {'ir': ir, 'hgt': hgt, 'sounding_u': sounding_u, 'sounding_v': sounding_v}
        ret.update({'data': dataret})

    hgt = mdgcal.gaussian_filter(hgt, sigma=1, order=0)

    # plot
    if is_draw:
        drawret = draw_obssate.draw_fy4air_sounding_hgt(ir, hgt, sounding_u, sounding_v, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret