'''


author: 郭楠楠
date: 2023-6-12

'''

import numpy as np


__all__ = [
    'tubing',
]


def tubing(stda, extent_tube_based=None, threshold_tube=0.5):
    r"""Tubing算法
    By 郭楠楠

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
