# -*- coding: utf-8 -*-

from metdig.metdig_io import get_model_grid

from metdig.metdig_onestep.lib.utility import get_map_area
from metdig.metdig_onestep.lib.utility import mask_terrian
from metdig.metdig_products.diag_veri_synop import draw_compare_gh_uv

import metdig.metdig_utl.utl_stda_grid as utl_stda_grid
import datetime

def compare_gh_uv(data_source='cassandra',
                anl_time=None,anamodel='grapes_gfs',
                data_name='grapes_gfs',fhour=24,
                hgt_lev=500, uv_lev=850,
                is_mask_terrain=True,area='全国', is_return_data=False, is_draw=True,
                **products_kwargs):
    
    ret = {}

    # get area
    map_extent = get_map_area(area)

    hgt_ana = get_model_grid(data_source=data_source, init_time=anl_time, fhour=0, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    u_ana = get_model_grid(data_source=data_source, init_time=anl_time, fhour=0, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    v_ana = get_model_grid(data_source=data_source, init_time=anl_time, fhour=0, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)

    init_time_fcst=anl_time-datetime.timedelta(hours=fhour)
    hgt_fcst = get_model_grid(data_source=data_source, init_time=init_time_fcst, fhour=fhour, data_name=data_name, var_name='hgt', level=hgt_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    u_fcst = get_model_grid(data_source=data_source, init_time=init_time_fcst, fhour=fhour, data_name=data_name, var_name='u', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)
    v_fcst = get_model_grid(data_source=data_source, init_time=init_time_fcst, fhour=fhour, data_name=data_name, var_name='v', level=uv_lev, extent=map_extent, x_percent=0.2, y_percent=0.1)

    if is_return_data:
        dataret = {'hgt_ana': hgt_ana , 'u_ana': u_ana, 'v_ana': v_ana,
                    'hgt_fcst': hgt_fcst , 'u_fcst': u_fcst, 'v_fcst': v_fcst}
        ret.update({'data': dataret})

    # 隐藏被地形遮挡地区
    if is_mask_terrain:
        psfc_ana = get_model_grid(data_source=data_source, init_time=anl_time, fhour=0, data_name=data_name, var_name='psfc', extent=map_extent, x_percent=0.2, y_percent=0.1)
        hgt_ana = mask_terrian(psfc_ana, hgt_lev, hgt_ana)
        u_ana = mask_terrian(psfc_ana, uv_lev, u_ana)
        v_ana = mask_terrian(psfc_ana, uv_lev, v_ana)

        psfc_fcst = get_model_grid(data_source=data_source, init_time=init_time_fcst, fhour=fhour, data_name=data_name, var_name='psfc', extent=map_extent, x_percent=0.2, y_percent=0.1)
        hgt_fcst = mask_terrian(psfc_fcst, hgt_lev, hgt_fcst)
        u_fcst = mask_terrian(psfc_fcst, uv_lev, u_fcst)
        v_fcst = mask_terrian(psfc_fcst, uv_lev, v_fcst)

    if is_draw:
        drawret = draw_compare_gh_uv(
                    hgt_ana, u_ana, v_ana,
                    hgt_fcst, u_fcst, v_fcst,
                    map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

if __name__ == '__main__':
    import datetime
    import matplotlib.pyplot as plt
    anl_time=datetime.datetime(2020,7,20,20)
    compare_gh_uv(anl_time=anl_time,data_source='cmadaas',area='华中')
    plt.show()        