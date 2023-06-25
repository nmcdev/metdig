from datetime import datetime,timedelta
import xarray as xr
import numpy as np
from scipy.stats import t
from metdig.cal.lib.utility import unifydim_stda, check_stda

__all__ = [
    'ensemble_sensitive',
    'tubing'
]

def critical_r(sig_lev,n):
    #求双边显著性临界相关系数
    #sig_lev=0.99 or 0.95 or 0.90 显著性水平
    #n 自由度
#     tt=r*np.sqrt((n-2))/(np.sqrt((1-r**2)))
    sig_lev2=1-(1-sig_lev)/2.
#     print(sig_lev2)
    tt=t.ppf(sig_lev2,n)
    r=np.sqrt((tt**2/(n-2+tt**2)))
    return r

@check_stda(['var_x', 'var_y'])
@unifydim_stda(['var_x', 'var_y'])
def ensemble_sensitive(var_x,var_y,mean_area,sig_lev):
    #var_x敏感度自变量
    #var_y敏感度因变量
    #mean_area敏感度平均区域
    #sig_lev显著性水平
    #返回敏感性相关矩阵和对应sig_lev显著性水平的临界相关系数
    var_y_mean=var_y.mean({'lon':mean_area[0:2],'lat':mean_area[2:4]}).expand_dims({'lon':[np.mean(mean_area[0:2])],'lat':[np.mean(mean_area[2:4])]})
    corr=xr.corr(var_x.isel(level=0).squeeze(),var_y_mean.isel(level=0).squeeze(),dim='member')
    dims_cor=list(corr.dims)
    dims_y=list(var_x.dims)
    for dim in dims_y:
        if((dim not in dims_cor) and (dim != 'member')):
            sensitive=corr.expand_dims({dim:var_x[dim]})
    sensitive=corr.expand_dims({'member':[var_x['member'].values[0].split('-')[0]]})
    sig_r=critical_r(0.95,len(var_x.member))
    return sensitive,sig_r

if __name__ == '__main__':
    import metdig
    var1=metdig.io.get_model_grids(init_time=datetime(2022,11,2,8),var_name='u',level=500,data_name='ecmwf_ens',data_source='cmadaas',fhours=[3,6])
    var2=metdig.io.get_model_grids(init_time=datetime(2022,11,2,8),var_name='rain',data_name='ecmwf_ens',data_source='cmadaas',fhours=[3,6])
    test=ensemble_sensitive(var1,var2,mean_area=[100,110,30,40],sig_lev=0.95)
    print(test)


@check_stda(['stda'])
def tubing(stda, extent_tube_based=None, threshold_tube=0.5):
    r"""Tubing算法
    author: 郭楠楠
    date: 2023-6-12

    Parameters
    ----------
    hgt : `stda`
        暂时只支持数据只包含单个平面的情景

    extent_tube_based : `list`, optional
        extent of the tube, such as [70., 136., 10., 55.]
        default to None

    threshold_tube : `int`, optional
        default to 0.5

    Returns
    -------
    `dict`
        以字典形式返回
    """

    '''
    part1: Central Cluster

    ;The ensemble mean (EM) is defined as the average of the ensemble forecasts (fl) .
    ;The n distances dm(i) from each ensemble forecast to the EM are computed (Euclidean Distance).
    ;The ensemble forecast that is closest to the EM, min[dm(i)], becomes the first member of the central cluster. This is iterated until the central cluster limits are reached. 
    ;Spread-dependent configuration: the limitation depends on the actual ensemble spread. For example, the central cluster variance is limited to 50% of the total ensemble variance.
    ;The distance from the last ensemble forecast classified in the central cluster to the EM becomes the radius r of the classification.

    '''
    configurations = 1 # 1:Spread-dependent configuration; 2:Season-dependent configuration

    lat = stda.lat.values
    lon = stda.lon.values
    if extent_tube_based is not None:
        index_lat = np.where((lat >= extent_tube_based[2]) & (lat <= extent_tube_based[3]))[0]
        index_lon = np.where((lon >= extent_tube_based[0]) & (lon <= extent_tube_based[1]))[0]
        fl = stda.isel(lat=index_lat, lon=index_lon)
    else:
        fl = stda

    fl_sq = np.squeeze(fl)
    EM = fl_sq.mean(dim='member')
    dm = np.sqrt(((fl_sq-EM)**2).sum(dim=['lat', 'lon']))

    # 按照偏离均值3倍标准差来排除异常值,筛出到距离集合平均过近的异常点（这决定了中央类的半径），因此只用考虑左侧的异常
    left = dm.values.mean()-3*dm.values.std()
    dm_normal = dm[left < dm]

    member_sort_index = np.argsort(dm_normal.values)
    vari_central = 0
    n = 0

    if configurations == 1:
        vari_total = np.var(dm_normal)
        while vari_central < vari_total*threshold_tube:
            n += 1
            member_central = member_sort_index[0:n+1]
            dm_central = dm_normal[member_central]
            vari_central = np.var(dm_central)

    else:
        vari_total  # 保留未来升级设置
        while vari_central < vari_total*threshold_tube:
            n += 1
            member_central = member_sort_index[0:n+1]
            dm_central = dm_normal[member_central]
            vari_central = np.var(dm_central)

    r = dm_normal[member_sort_index[n]].values

    '''
    part2: Tubes

    ; The matrix d of ensemble forecasts interdistances is computed.
    ; The ensemble forecast that is farthest from the ensemble mean, max[dm(i)], becomes the extreme of the first tube.
    ; For each ensemble forecasts member(i) that has not been classified in the central cluster, that is, not a tube extreme, 
      and whose distance dm(i) to the ensemble mean is maximum, if the two following operations are achieved for each existing tube extreme, member(i) is a member
      of the tube j
      1、the projection of dm(i) on the of the axis of the exist tube j  defined as dd(i, j)>0
      2、the distance of member(i) to the axis of tube j defined as  dx(i, j) < r 

    '''

    member_tubes = member_sort_index[n+1:]
    tubes_index = dict()
    tubes_index.setdefault(1, []).append(member_sort_index[-1])
    dd = np.zeros((len(member_tubes), len(member_tubes)))
    dx2 = np.zeros((len(member_tubes), len(member_tubes)))

    for iim, im in enumerate(member_tubes):
        for jjm, jm in enumerate(member_tubes):
            d = np.sqrt(((fl_sq.isel(member=im)-fl_sq.isel(member=jm))**2).sum(dim=['lat', 'lon']))
            dm2_i = np.square(dm_normal.isel(member=im).values)
            dm2_j = np.square(dm_normal.isel(member=jm).values)
            dd[iim, jjm] = (dm2_i+dm2_j-np.square(d))/(2*dm_normal.isel(member=jm))
            dx2[iim, jjm] = dm2_i-np.square(dd[iim, jjm])

    it = 1
    for i in range(len(member_tubes)-2, -1, -1):
        tubes_number = list(tubes_index.keys())
        criteria = 0
        for it in tubes_number:
            tubes_extrem = tubes_index[it][0]
            tubes_extrem_index = np.argwhere(member_tubes == tubes_extrem)
            if dx2[i, tubes_extrem_index] < np.square(r) and dd[i, tubes_extrem_index] > 0:
                criteria += 1
                tubes_index[it].append(member_tubes[i])
        if not(member_tubes[i] in sum(list(tubes_index.values()), [])) and criteria == 0:
            it += 1
            tubes_index.setdefault(it, []).append(member_tubes[i])
    return {
        'tubes_index': tubes_index,
        'member_central': member_central,
        'vari_total': vari_total,
        # 'vari_total': vari_total.values,
        'r': r
    }
