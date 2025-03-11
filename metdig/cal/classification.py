'''
聚类
'''

import numpy as np
import math
from datetime import datetime, timedelta


from sklearn import preprocessing
from sklearn.decomposition import PCA

import xarray as xr

from metdig.cal.lib.utility import unifydim_stda, check_stda

try:
    from sklearn.cluster import KMeans
except:
    pass


__all__ = [
    'kmeans',
]

@check_stda(['stda'])
def kmeans(stda, axes, n_components,
           n_clusters=8, init='k-means++', n_init='warn', max_iter=300, 
           tol=1e-4, verbose=0, random_state=None, copy_x=True, algorithm='lloyd'):
    """
    stda 沿着 axes 进行聚类，并返回聚类结果。
    """

    loop_axes = ['member', 'level', 'time', 'dtime']
    loop_axes.remove(axes)
    for d in loop_axes:
        if stda[d].size != 1:
            raise Exception(f'{d} dimension size must be equal to 1')
    if stda[axes].size == 1:
        raise Exception(f'{axes} dimension size must be greater than 1')

    # 把要沿着的轴转移到第一维
    transpose_axes = ['member', 'level', 'time', 'dtime', 'lat', 'lon']
    transpose_axes.remove(axes)
    transpose_axes.insert(0, axes)
    X = stda.transpose(*transpose_axes)
    
    # 6维变成2维(行是样本，列是特征)
    X = X.values
    X = X.reshape((X.shape[0], -1))

    # 标准化
    X_scaled = preprocessing.scale(X, axis=1) # 这里应该按行标准化还是按列？

    # pca降维
    pca = PCA(n_components=n_components)  # 降至2维
    X_pca = pca.fit_transform(X_scaled)

    ret = KMeans(n_clusters=n_clusters, init=init, n_init=n_init, 
                 max_iter=max_iter, tol=tol, verbose=verbose, 
                 random_state=random_state, copy_x=copy_x, algorithm=algorithm).fit(X_pca)
    return ret
    
    # print(ret.inertia_)
    # print(values.shape)
    # for 
    # print(loop_axes)
    pass