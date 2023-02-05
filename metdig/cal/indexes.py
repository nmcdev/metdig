# -*- coding: utf-8 -*-

'''

'''

import numpy as np
import pandas as pd
__all__ = [
    'westerly_index',
    'area_index_of_subtropical_high',
    'west_end_of_wpsh',
    'ridge_latitude_of_wpsh'
]

def westerly_index(hgt):
    hgt1=hgt.sel(lon=slice(65,155),lat=65).drop('lat')
    hgt2=hgt.sel(lon=slice(65,155),lat=45).drop('lat')
    widx=(hgt2-hgt1).mean('lon').expand_dims({'lon':['mean_from_65_to_155'],'lat':['65-45']})
    widx.attrs=hgt.attrs.copy()
    widx.attrs['var_name']='westerly_index'
    widx.attrs['var_cn_name']='西风指数'
    return widx

# if __name__=='__main__':
#     import metdig
#     import pandas as pd
#     init_times=pd.date_range('2021-07-19-08','2021-07-21-08',freq='6h').to_pydatetime()
#     hgt500=metdig.io.era5.get_model_grids(init_times=init_times,var_name='hgt',level=500)
#     widx=westerly_index(hgt500)
#     print(widx)

def area_index_of_subtropical_high(hgt):
    # hgt.stda.hor
    aish=(hgt.sel(lon=slice(110,180,int(10/hgt.stda.horizontal_resolution)),lat=slice(10,90,int(5/hgt.stda.horizontal_resolution)))>588).sum(['lon','lat'])
    aish=aish.expand_dims({'lon':['110_to_180'],'lat':['10_to_90']})
    aish.attrs=hgt.attrs.copy()
    aish.attrs['var_name']='area_index_of_subtropical_high'
    aish.attrs['var_cn_name']='副高面积指数'
    return aish

# if __name__=='__main__':
#     import metdig
#     import pandas as pd
#     init_times=pd.date_range('2021-07-19-08','2021-07-21-08',freq='6h').to_pydatetime()
#     hgt500=metdig.io.era5.get_model_grids(init_times=init_times,var_name='hgt',level=500)
#     widx=area_index_of_subtropical_high(hgt500)
#     print(widx)

def west_end_of_wpsh(hgt):
    hgt1=hgt.sel(lon=slice(90,180),lat=slice(10,90))
    wsph=hgt1.where(hgt1>=588,drop=True)
    we_wsph=None
    for imdl in wsph['member'].values:
        temp3=[]
        for it in wsph['time'].values:
            for idt in wsph['dtime'].values:
                temp1=hgt1.sel(time=[it],dtime=[idt],member=[imdl])
                if(temp1.where(temp1>588,drop=True).size > 0):
                    temp2=temp1.where(temp1>588,drop=True).isel(lon=[0]).dropna(dim='lat')
                    temp3.append(pd.DataFrame({'id':1,'time':it,'dtime':idt,'lon':temp2.lon.values[0],'lat':temp2.lat.values[0],imdl:[temp2.lon.values[0]]}))
        if(we_wsph is None):
            we_wsph=pd.concat(temp3).reset_index(drop=True)
        else:
            pd.merge(we_wsph,pd.concat(temp3)).reset_index(drop=True)
    we_wsph.attrs=hgt.attrs.copy()
    we_wsph.attrs['var_name']='west_end_of_wpsh'
    we_wsph.attrs['var_cn_name']='副高西脊点经度'
    we_wsph.attrs['var_units']='degree'
    we_wsph.attrs['data_start_columns']=6
    return we_wsph

# if __name__=='__main__':
#     import metdig
#     import pandas as pd
#     init_times=pd.date_range('2021-07-19-08','2021-07-21-08',freq='6h').to_pydatetime()
#     hgt500=metdig.io.era5.get_model_grids(init_times=init_times,var_name='hgt',level=500)
#     we_wsph=west_end_of_wpsh(hgt500)
#     print(we_wsph)

def ridge_latitude_of_wpsh(hgt,u):
    temp1=hgt.sel(lon=[110,120,130],lat=slice(0,90)).where(hgt>586,drop=True)
    u_slt=u.where(temp1.isnull())
    # v_slt=v.where(temp1.isnull())
    # v_slt2=v_slt.where(v_slt>0,drop=True)
    u_slt2=u_slt.where(u_slt)

    u_slt3=u_slt2.isel(lat=slice(0,-2))
    u_slt4=u_slt2.isel(lat=slice(1,-1)).drop('lat').assign_coords({'lat':u_slt3.lat.values})

    temp2=u_slt3.where(((u_slt3<0)&(u_slt4>0)),drop=True)

    rp_wsph=None
    for imdl in temp2['member'].values:
        temp5=[]
        for it in temp2['time'].values:
            for idt in temp2['dtime'].values:
                temp4=[]
                for ilon in temp2['lon'].values:
                    if(temp2.sel(member=imdl,time=it,dtime=idt,lon=ilon).dropna(dim='lat',how='all').size > 0):
                        temp3=temp2.sel(member=imdl,time=it,dtime=idt,lon=ilon).dropna(dim='lat',how='all').lat.values[0]
                        temp4.append(temp3)
                temp5.append(pd.DataFrame({'id':1,'time':it,'dtime':idt,'lon':['110,120,130'],'lat':np.nanmean(temp4),imdl:np.nanmean(temp4)}))
        if(rp_wsph is None):
            rp_wsph=pd.concat(temp5).reset_index(drop=True)
        else:
            pd.merge(rp_wsph,pd.concat(temp5)).reset_index(drop=True)

    rp_wsph.attrs=hgt.attrs.copy()
    rp_wsph.attrs['var_name']='ridge_latitude_of_wpsh'
    rp_wsph.attrs['var_cn_name']='副高西脊点纬度'
    rp_wsph.attrs['var_units']='degree'
    rp_wsph.attrs['data_start_columns']=6

    return rp_wsph

if __name__=='__main__':
    import metdig
    import pandas as pd
    init_times=pd.date_range('2021-07-19-08','2021-07-21-08',freq='6h').to_pydatetime()
    hgt500=metdig.io.era5.get_model_grids(init_times=init_times,var_name='hgt',level=500)
    u500=metdig.io.era5.get_model_grids(init_times=init_times,var_name='u',level=500)
    rp_wsph=ridge_latitude_of_wpsh(hgt500,u500)
    print(rp_wsph)