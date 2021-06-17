
import numpy as np

from metdig.io.cassandra import get_wind_profiler_bytimerange

from metdig.products import observation_unusual as draw_unusual

import metdig.cal as mdgcal
import metdig.utl as mdgstda

__all__ = [
    'wind_profiler',
]


def wind_profiler(obs_st_time=None, obs_ed_time=None, id_selected=51463, is_return_data=False, is_draw=True, **products_kwargs):
    ret = {}

    wsp = get_wind_profiler_bytimerange(obs_st_time, obs_ed_time, data_name='wind_profiler', var_name='wsp', id_selected=id_selected)
    wdir = get_wind_profiler_bytimerange(obs_st_time, obs_ed_time, data_name='wind_profiler', var_name='wdir', id_selected=id_selected)

    # 计算uv
    u, v = mdgcal.wind_components(wsp, wdir)

    # 转成格点stda
    u = mdgstda.stastda_to_gridstda(u, xdim='time', ydim='level')
    v = mdgstda.stastda_to_gridstda(v, xdim='time', ydim='level')

    # 时间维度简单稀疏化
    step = int(u.stda.time.size / 40)
    u = u.isel(time=slice(0, -1, step))
    v = v.isel(time=slice(0, -1, step))

    if is_return_data:
        dataret = {'u': u, 'v': v}
        ret.update({'data': dataret})

    # plot
    if is_draw:
        drawret = draw_unusual.draw_wind_profiler(u, v, id_selected, obs_st_time, obs_ed_time, **products_kwargs)
        ret.update(drawret)

    if ret:
        return ret
