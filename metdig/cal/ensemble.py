from datetime import datetime,timedelta
import xarray as xr
import numpy as np
from scipy.stats import t

__all__ = [
    'ensemble_sensitive',
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

