# -*- coding: utf-8 -*-

import numpy as np
import datetime

from metdig.io import get_model_grid
from metdig.io import get_model_grids

from metdig.onestep.lib.utility import get_map_area
from metdig.onestep.lib.utility import date_init

from metdig.products import diag_elements as draw_elements

import metdig.cal as mdgcal

@date_init('init_time')
def t2m_mx24(data_source='cassandra', data_name='nwfd_scmoc', init_time=None, fhour=24, area='全国',
             is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    map_extent = get_map_area(area)

    tmx24_2m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                              var_name='tmx24_2m', throwexp=False)
    if tmx24_2m is None:
        fhours = np.arange(fhour - 21, fhour + 1, 3)
        t2m = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                              var_name='tmx3_2m', throwexp=False)
        if t2m is None:
            t2m = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                                  var_name='t2m', throwexp=False)
            if t2m is None:
                raise Exception('can not get any data')

        tmx24_2m = t2m.isel(dtime=[-1]).copy()
        tmx24_2m.values[:, :, :, 0, :, :] = t2m.max(dim='dtime').values
        tmx24_2m.attrs['var_name'] = 'tmx24_2m'
        tmx24_2m.attrs['var_cn_name'] = '过去24小时2米最高温度'
        tmx24_2m.attrs['valid_time'] = 24

    if is_return_data:
        dataret = {'tmx24_2m': tmx24_2m}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_elements.draw_tmp(tmx24_2m, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def t2m_mn24(data_source='cassandra', data_name='nwfd_scmoc', init_time=None, fhour=24, area='全国',
             is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    map_extent = get_map_area(area)

    tmn24_2m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                              var_name='tmn24_2m', throwexp=False)
    if tmn24_2m is None:
        fhours = np.arange(fhour - 21, fhour + 1, 3)
        t2m = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                              var_name='tmn3_2m', throwexp=False)
        if t2m is None:
            t2m = get_model_grids(data_source=data_source, init_time=init_time, fhours=fhours, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                                  var_name='t2m', throwexp=False)
            if t2m is None:
                raise Exception('can not get any data')

        tmn24_2m = t2m.isel(dtime=[-1]).copy()
        tmn24_2m.values[:, :, :, 0, :, :] = t2m.min(dim='dtime').values
        tmn24_2m.attrs['var_name'] = 'tmn24_2m'
        tmn24_2m.attrs['var_cn_name'] = '过去24小时2米最低温度'
        tmn24_2m.attrs['valid_time'] = 24

    if is_return_data:
        dataret = {'tmn24_2m': tmn24_2m}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_elements.draw_tmp(tmn24_2m, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def mslp_gust10m(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, t_gap=3, area='全国',
                 is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    map_extent = get_map_area(area)

    if t_gap == 3:
        gust10m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                                 var_name='gust10m_3h', extent=map_extent)
    elif t_gap == 6:
        gust10m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                                 var_name='gust10m_6h', extent=map_extent)
    else:
        raise Exception('t_gap must be 3 or 6')

    prmsl = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                           var_name='prmsl')

    gust10m.attrs['var_cn_name'] = '逐{}小时最大阵风'.format(t_gap)

    if is_return_data:
        dataret = {'gust10m': gust10m, 'prmsl': prmsl}
        ret.update({'data': dataret})

    prmsl = mdgcal.gaussian_filter(prmsl, 5)

    if is_draw:
        drawret = draw_elements.draw_mslp_gust(gust10m, prmsl, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret

@date_init('init_time')
def mslp_gust10m_uv10m(data_source='cassandra', data_name='ecmwf', init_time=None, fhour=24, t_gap=3, area='全国',
                       is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    map_extent = get_map_area(area)

    if t_gap == 3:
        gust10m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                                 var_name='gust10m_3h', extent=map_extent)
    elif t_gap == 6:
        gust10m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                                 var_name='gust10m_6h', extent=map_extent)
    else:
        raise Exception('t_gap must be 3 or 6')
    
    prmsl = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                           var_name='prmsl')
    u10m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                          var_name='u10m')
    v10m = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                          var_name='v10m')

    gust10m.attrs['var_cn_name'] = '逐{}小时最大阵风'.format(t_gap)

    if is_return_data:
        dataret = {'gust10m': gust10m, 'prmsl': prmsl}
        ret.update({'data': dataret})

    prmsl = mdgcal.gaussian_filter(prmsl, 5)
    
    if is_draw:
        drawret = draw_elements.draw_mslp_gust_uv10m(gust10m, prmsl, u10m, v10m, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
    

if __name__=='__main__':
    mslp_gust10m_uv10m()

@date_init('init_time')
def dt2m_mx24(data_source='cassandra', data_name='grapes_gfs', init_time=None, fhour=48, area='全国',
              is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    map_extent = get_map_area(area)

    init_time1 = init_time
    fhours1 = np.arange(fhour - 21, fhour + 1, 3)
    if(fhour >= 48):
        init_time2 = init_time
        fhours2 = np.arange(fhour - 21 - 24, fhour + 1 - 24, 3)
    if(fhour >= 36 and fhour < 48):
        fhours2 = np.arange(fhour - 21 + 12 - 24, fhour + 1 + 12 - 24, 3)
        init_time2 = init_time - datetime.timedelta(hours=12)
    if(fhour >= 24 and fhour < 36):
        fhours2 = np.arange(fhour - 21 + 24 - 24, fhour + 1 + 24 - 24, 3)
        init_time2 = init_time - datetime.timedelta(hours=24)
    if(fhour < 24):
        print('fhour should > 24')
        return

    t_2m_1 = get_model_grids(data_source=data_source, init_time=init_time1, fhours=fhours1, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                             var_name='tmx3_2m')
    if t_2m_1 is None:
        t_2m_1 = get_model_grids(data_source=data_source, init_time=init_time1, fhours=fhours1, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                                 var_name='t_2m')
        if t_2m_1 is None:
            raise Exception('can not get any data')

    t_2m_2 = get_model_grids(data_source=data_source, init_time=init_time2, fhours=fhours2, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                             var_name='tmx3_2m')
    if t_2m_2 is None:
        t_2m_2 = get_model_grids(data_source=data_source, init_time=init_time2, fhours=fhours2, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                                 var_name='t_2m')
        if t_2m_2 is None:
            raise Exception('can not get any data')

    dtmx_2m = t_2m_1.isel(dtime=[-1]).copy()
    dtmx_2m.values[:, :, :, 0, :, :] = t_2m_1.max(dim='dtime').values - t_2m_2.max(dim='dtime').values
    dtmx_2m.attrs['var_name'] = 'dtmx_2m'
    dtmx_2m.attrs['var_cn_name'] = '2米最高温度24小时变温'

    if is_return_data:
        dataret = {'dtmx_2m': dtmx_2m}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_elements.draw_dt2m(dtmx_2m, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def dt2m_mn24(data_source='cassandra', data_name='grapes_gfs', init_time=None, fhour=24, area='全国',
              is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    map_extent = get_map_area(area)

    init_time1 = init_time
    fhours1 = np.arange(fhour - 21, fhour + 1, 3)
    if(fhour >= 48):
        init_time2 = init_time
        fhours2 = np.arange(fhour - 21 - 24, fhour + 1 - 24, 3)
    if(fhour >= 36 and fhour < 48):
        fhours2 = np.arange(fhour - 21 + 12 - 24, fhour + 1 + 12 - 24, 3)
        init_time2 = init_time - datetime.timedelta(hours=12)
    if(fhour >= 24 and fhour < 36):
        fhours2 = np.arange(fhour - 21 + 24 - 24, fhour + 1 + 24 - 24, 3)
        init_time2 = init_time - datetime.timedelta(hours=24)
    if(fhour < 24):
        print('fhour should > 24')
        return

    t_2m_1 = get_model_grids(data_source=data_source, init_time=init_time1, fhours=fhours1, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                             var_name='tmn3_2m')
    if t_2m_1 is None:
        t_2m_1 = get_model_grids(data_source=data_source, init_time=init_time1, fhours=fhours1, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                                 var_name='t_2m')
        if t_2m_1 is None:
            raise Exception('can not get any data')

    t_2m_2 = get_model_grids(data_source=data_source, init_time=init_time2, fhours=fhours2, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                             var_name='tmn3_2m')
    if t_2m_2 is None:
        t_2m_2 = get_model_grids(data_source=data_source, init_time=init_time2, fhours=fhours2, data_name=data_name, extent=map_extent, x_percent=0, y_percent=0,
                                 var_name='t_2m')
        if t_2m_2 is None:
            raise Exception('can not get any data')

    dtmn_2m = t_2m_1.isel(dtime=[-1]).copy()
    dtmn_2m.values[:, :, :, 0, :, :] = t_2m_1.min(dim='dtime').values - t_2m_2.min(dim='dtime').values
    dtmn_2m.attrs['var_name'] = 'dtmn_2m'
    dtmn_2m.attrs['var_cn_name'] = '2米最低温度24小时变温'

    if is_return_data:
        dataret = {'dtmn_2m': dtmn_2m}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_elements.draw_dt2m(dtmn_2m, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret


@date_init('init_time')
def dt2m_mean24(data_source='cassandra', data_name='grapes_gfs', init_time=None, fhour=24, area='全国',
                is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    map_extent = get_map_area(area)

    init_time1 = init_time
    fhours1 = np.arange(fhour - 21, fhour + 1, 3)
    if(fhour >= 48):
        init_time2 = init_time
        fhours2 = np.arange(fhour - 21 - 24, fhour + 1 - 24, 3)
    if(fhour >= 36 and fhour < 48):
        fhours2 = np.arange(fhour - 21 + 12 - 24, fhour + 1 + 12 - 24, 3)
        init_time2 = init_time - datetime.timedelta(hours=12)
    if(fhour >= 24 and fhour < 36):
        fhours2 = np.arange(fhour - 21 + 24 - 24, fhour + 1 + 24 - 24, 3)
        init_time2 = init_time - datetime.timedelta(hours=24)
    if(fhour < 24):
        print('fhour should > 24')
        return

    t_2m_1 = get_model_grids(data_source=data_source, init_time=init_time1, fhours=fhours1, data_name=data_name,
                             var_name='t2m', extent=map_extent)
    t_2m_2 = get_model_grids(data_source=data_source, init_time=init_time2, fhours=fhours2, data_name=data_name,
                             var_name='t2m', extent=map_extent)

    dtmean_2m = t_2m_1.isel(dtime=[-1]).copy()
    dtmean_2m.values[:, :, :, 0, :, :] = t_2m_1.mean(dim='dtime').values - t_2m_2.mean(dim='dtime').values
    dtmean_2m.attrs['var_name'] = 'dtmean_2m'
    dtmean_2m.attrs['var_cn_name'] = '2米平均温度24小时变温'

    if is_return_data:
        dataret = {'dtmean_2m': dtmean_2m}
        ret.update({'data': dataret})

    if is_draw:
        drawret = draw_elements.draw_dt2m(dtmean_2m, map_extent=map_extent, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
