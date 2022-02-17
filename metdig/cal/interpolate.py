import datetime
import numpy as np
import pandas as pd
import xarray as xr
from scipy.interpolate import LinearNDInterpolator
import metdig.utl as mdgstda
from metdig.io.lib import utility as utl

__all__ = [
    'interpolate_3d',
]

def interpolate_3d(stda, hgt, points, stda_sfc=None):
    '''

    [利用位势高度，站点高度，和各层模式数据进行三维不规则点插值，获取初步订正的山地地形站点预报]

    Arguments:
        stda {[stda]} -- [被插值的要素]
        hgt {[stda]} -- [模式位势高度]
        points {[{'lon':[110],'lat':[30],'alt':[1000]}]} -- [{被插值站点的经度，维度，高度}]
        stda_sfc {[stda]} -- [可选量,stda的对应地面量，当站点高度低于hgt中对应位置高度最小值，则直接用stda_sfc中的线性插值结果]

    Returns:
        [stda] -- [被插值后的站点数据,超出给定范围复制nan]
    '''
    stda_sta=[]
    nsta=len(points['lon'])
    ntime=stda.time.size
    ndtime=stda.dtime.size
    nmember=stda.member.size
    sta=np.zeros((nsta,stda.member.size,stda.time.size,stda.dtime.size))
    nlines=nsta*stda.time.size*stda.dtime.size
    sta_df=[]
    if('id' not in points.keys()):
        ids=np.arange(0,nsta)
    else:
        ids=points['id']
    for idx_time,itime in enumerate(stda.time.values):
        for idx_dtime,idtime in enumerate(stda.dtime.values):
            temp_df=pd.DataFrame(columns=['level', 'time', 'dtime', 'id', 'lon', 'lat'] + list(stda.member.values))
            for idx_member,imember in enumerate(stda.member.values):
                try: #防止某一数据不全
                    data3d=stda.sel(member=imember,time=itime,dtime=idtime)
                    hgt3d=hgt.sel(member=imember,time=itime,dtime=idtime)
                    data3d_np = np.squeeze(data3d.values).flatten()
                    hgt3d_np = (np.squeeze(hgt3d.values)).flatten()*10

                    coords = np.zeros((data3d['level'].size,data3d['lat'].size,data3d['lon'].size,3))
                    coords[...,1] = data3d['lat'].values.reshape((1,data3d['lat'].size,1))
                    coords[...,2] = data3d['lon'].values.reshape((1,1,data3d['lon'].size))
                    coords = coords.reshape((data3d_np.size,3))
                    coords[:,0]=hgt3d_np
                    interpolator = LinearNDInterpolator(coords,data3d_np,rescale=True)

                    coords2=np.zeros((np.size(points['lon']),3))
                    coords2[:,0]=points['alt']
                    coords2[:,1]=points['lat']
                    coords2[:,2]=points['lon']
                    sta[:,idx_member,idx_time,idx_dtime]=interpolator(coords2)
                    temp_df[imember]=interpolator(coords2)
                except:#防止某一数据不全
                    print('高空数据不全 起报时间'+str(itime)+' 预报时效'+str(idtime)+' 成员'+str(imember))
                    temp_df[imember]=np.nan

            temp_df['level']=points['alt']
            temp_df['time']=itime
            temp_df['dtime']=idtime
            temp_df['id']=points['id']
            temp_df['lon']=points['lon']
            temp_df['lat']=points['lat']
            sta_df.append(temp_df)
    stda_sta=pd.concat(sta_df)
    stda_attrs = mdgstda.get_stda_attrs(var_name=stda.attrs['var_name'])
    stda_sta.attrs=stda_attrs
    stda_sta.attrs['data_start_columns']=6

    if (stda_sfc is not None):
        stda_sfc_sta=stda_sfc.interp({'lon':('id',points['lon']),'lat':('id',points['lat'])}).assign_coords({'id':points['id']})
        hgt_sta=hgt.interp({'lon':('id',points['lon']),'lat':('id',points['lat'])}).assign_coords({'id':ids})*10
        for idx_member,imember in enumerate(stda.member.values):
            for idx_time,itime in enumerate(stda.time.values):
                for idx_dtime,idtime in enumerate(stda.dtime.values):
                    try:#防止某一数据不全
                        for idx,iid in enumerate(ids):
                            if(hgt_sta.sel(dtime=idtime,time=itime,member=imember,id=iid).isel(level=0).values > points['alt'][idx]):
                                stda_sta[imember].loc[(stda_sta['dtime']==idtime)&(stda_sta['dtime']==idtime)&(stda_sta['time']==itime)&(stda_sta['id']==iid)]=stda_sfc_sta.sel(dtime=idtime,time=itime,member=imember,id=iid).values[0]
                    except:#防止某一数据不全
                        stda_sta[imember].loc[(stda_sta['dtime']==idtime)&(stda_sta['dtime']==idtime)&(stda_sta['time']==itime)&(stda_sta['id']==iid)]=np.nan
                        print('地面数据不全 起报时间'+str(itime)+' 预报时效'+str(idtime)+' 成员'+str(imember))
                        continue
    return stda_sta

if __name__ == '__main__':
    import metdig
    from datetime import datetime
    import numpy as np
    import pandas as pd
    fhours=np.arange(24,31,6)
    output_dir=r'G:\realtime_data\ensemble_fcst_sta_data/'
    sta_info=pd.read_csv(r'L:/py_develop/Winter_Olympic/resources/sta_info.csv')
    extent=[sta_info['lon'].min()-1,sta_info['lon'].max()+1,sta_info['lat'].min()-1,sta_info['lat'].max()+1]
    points={'lon':sta_info['lon'].to_list(),'lat':sta_info['lat'].to_list(),
       'alt':sta_info['level'].to_list(),'id':sta_info['ID'].to_list()}

    hgt=metdig.io.get_model_3D_grids(init_time=datetime(2021,12,29,20),fhours=fhours,levels=[1000,925,850,700],
                                data_source='cassandra',data_name='ecmwf_ens',var_name='hgt',extent=extent)
    u=metdig.io.get_model_3D_grids(init_time=datetime(2021,12,29,20),fhours=fhours,levels=[1000,925,850,700],
                                data_source='cassandra',data_name='ecmwf_ens',var_name='u',extent=extent)

    v=metdig.io.get_model_3D_grids(init_time=datetime(2021,12,29,20),fhours=fhours,levels=[1000,925,850,700],
                                data_source='cassandra',data_name='ecmwf_ens',var_name='v',extent=extent)

    tmp=metdig.io.get_model_3D_grids(init_time=datetime(2021,12,29,20),fhours=fhours,levels=[1000,925,850,700],
                                data_source='cassandra',data_name='ecmwf_ens',var_name='tmp',extent=extent)        

    rh=metdig.io.get_model_3D_grids(init_time=datetime(2021,12,29,20),fhours=fhours,levels=[1000,925,850,700],
                                data_source='cassandra',data_name='ecmwf_ens',var_name='rh',extent=extent)        

    u10m=metdig.io.get_model_grids(init_time=datetime(2021,12,29,20),fhours=fhours,
                                    data_source='cassandra',data_name='ecmwf_ens',var_name='u10m',extent=extent)        

    v10m=metdig.io.get_model_grids(init_time=datetime(2021,12,29,20),fhours=fhours,
                                    data_source='cassandra',data_name='ecmwf_ens',var_name='v10m',extent=extent)        

    t2m=metdig.io.get_model_grids(init_time=datetime(2021,12,29,20),fhours=fhours,
                                    data_source='cassandra',data_name='ecmwf_ens',var_name='t2m',extent=extent)        

    td2m=metdig.io.get_model_grids(init_time=datetime(2021,12,29,20),fhours=fhours,
                                    data_source='cassandra',data_name='ecmwf_ens',var_name='td2m',extent=extent)        

    rain12=metdig.io.get_model_points(init_time=datetime(2021,12,29,20),fhours=fhours,points=points.copy(),
                                    data_source='cassandra',data_name='ecmwf_ens',var_name='rain12')

                                    #计算地面相对湿度
    rh2m=metdig.cal.moisture.relative_humidity_from_dewpoint(t2m,td2m)

    tmp_sta=metdig.cal.interpolate.interpolate_3d(tmp, hgt, points, t2m)

    rh2m_sta=metdig.cal.interpolate.interpolate_3d(rh, hgt, points, rh2m)

    t2m_sta=metdig.cal.interpolate.interpolate_3d(tmp, hgt, points, t2m)

    u10m_sta=metdig.cal.interpolate.interpolate_3d(u, hgt, points, u10m)

    v10m_sta=metdig.cal.interpolate.interpolate_3d(v, hgt, points, v10m)

    wsp10m=metdig.cal.other.wind_speed(u10m_sta,v10m_sta)
    wdir10m=metdig.cal.other.wind_direction(u10m_sta,v10m_sta)

    output_filename=tmp_sta.stda.time[0].strftime('%Y%m%d%H.csv')

    wsp10m.to_csv(output_dir+output_filename)