import numpy as np
import pandas as pd
import xarray as xr
from scipy.interpolate import LinearNDInterpolator
import metdig.utl as mdgstda
from metdig.io.lib import utility as utl
from metdig.onestep.lib.utility import mask_terrian
import metdig
from datetime import datetime,timedelta
import math 
import numpy as np 
import xarray as xr

__all__ = [
    'interpolate_3d',
    'interpolate_3d_whole_area',
    'trajectory_on_pressure_level',
]


def trajectory_on_pressure_level(u,v,vvel,var_diag=None,
    s_point={'lon':[119.3,119.31],'lat':[32.4,32.41],'level':[925,900],'id':[1,2]},
    t_s=None,t_e=None,dt=None):

    #气压坐标下的空气质点追踪算法，输入垂直运动速度为气压速度
    #stda标准u 东西风 v 南北风 vvel气压垂直速度
    #var_diag 为任意stda标准格式的诊断两，如spfh、rh等
    #s_points 为字典型，质点起始位置，如{'lon':[100,101.1],'lat':[30,30.1],'level':[875,875.5],'id':[1,2]}，如果用户没有给定id，则自动生成从1开始的连续数字
    #t_s 起始时间，t_e终止时间，datetime格式，如未给定，则为u的预报时间的起止时间
    #dt追踪时间步长 单位为s，如果未给定则为1800
    if('id' not in list(s_point.keys())):
        s_point['id']=list(range(1,len(s_point['lon'])+1))
    if dt is None:
        dt = 1800

    if(len(u['time'])>1):
        trans_dim='time'
    else:
        trans_dim='dtime'
    
    u_trans=u.assign_coords({'fcst_time':(trans_dim,u.stda.fcst_time)}).swap_dims({trans_dim:'fcst_time'})
    v_trans=v.assign_coords({'fcst_time':(trans_dim,v.stda.fcst_time)}).swap_dims({trans_dim:'fcst_time'})
    vvel_trans=vvel.assign_coords({'fcst_time':(trans_dim,vvel.stda.fcst_time)}).swap_dims({trans_dim:'fcst_time'})
    if(t_s is None):
        if(dt > 0):
            t_s=pd.to_datetime(u_trans.fcst_time.values[0])
        else:
            t_s=pd.to_datetime(u_trans.fcst_time.values[-1])
    t_now=t_s
    if(t_e is None):
        if(dt > 0):
            t_e=pd.to_datetime(u_trans.fcst_time.values[-1])
        else:
            t_e=pd.to_datetime(u_trans.fcst_time.values[0])
            
    if(var_diag is None):
        var_diag=vvel.copy()
    var_diag_trans=var_diag.assign_coords({'fcst_time':(trans_dim,var_diag.stda.fcst_time)}).swap_dims({trans_dim:'fcst_time'})
    u_s=u_trans.interp({'lon':('id',s_point['lon']),'lat':('id',s_point['lat']),'level':('id',s_point['level']),'fcst_time':[t_s]}).assign_coords({'id':('id',s_point['id'])})
    v_s=v_trans.interp({'lon':('id',s_point['lon']),'lat':('id',s_point['lat']),'level':('id',s_point['level']),'fcst_time':[t_s]}).assign_coords({'id':('id',s_point['id'])})
    vvel_s=vvel_trans.interp({'lon':('id',s_point['lon']),'lat':('id',s_point['lat']),'level':('id',s_point['level']),'fcst_time':[t_s]}).assign_coords({'id':('id',s_point['id'])})
    var_s=var_diag_trans.interp({'lon':('id',s_point['lon']),'lat':('id',s_point['lat']),'level':('id',s_point['level']),'fcst_time':[t_s]}).assign_coords({'id':('id',s_point['id'])})

    r_earth=6371000 
    dis2lat=180/(math.pi*r_earth) #Distance to Latitude 
    const={'a':r_earth,'dis2lat':dis2lat} 

    while ((t_now <= max((t_s,t_e))) and (t_now >= min((t_s,t_e)))):
        # print(t_now)
        dx=u_s*dt 
        dlon=dx*180/(const['a']*math.sin(math.pi/2-math.radians(s_point['lat'][-1]))*math.pi) 
        dy=v_s*dt
        dlat=dy*const['dis2lat'] 
        dvvel=vvel_s*dt/100 # to hPa 
        temp=var_s.isel(fcst_time=[-1]).copy()
        temp.coords['lon']=temp.coords['lon']+dlon.squeeze().values
        temp.coords['lat']=temp.coords['lat']+dlat.squeeze().values
        temp.coords['level']=temp.coords['level']+dvvel.squeeze().values
        temp.coords['fcst_time']=[t_now]
        u_s=u_trans.interp({'lon':('id',temp['lon'].values.flatten().tolist()),'lat':('id',temp['lat'].values.flatten().tolist()),'level':('id',temp['level'].values.flatten().tolist()),'fcst_time':[t_now]}).assign_coords({'id':('id',temp['id'].values.flatten().tolist())})
        v_s=v_trans.interp({'lon':('id',temp['lon'].values.flatten().tolist()),'lat':('id',temp['lat'].values.flatten().tolist()),'level':('id',temp['level'].values.flatten().tolist()),'fcst_time':[t_now]}).assign_coords({'id':('id',temp['id'].values.flatten().tolist())})
        vvel_s=vvel_trans.interp({'lon':('id',temp['lon'].values.flatten().tolist()),'lat':('id',temp['lat'].values.flatten().tolist()),'level':('id',temp['level'].values.flatten().tolist()),'fcst_time':[t_now]}).assign_coords({'id':('id',temp['id'].values.flatten().tolist())})
        temp.values=var_diag_trans.interp({'lon':('id',temp['lon'].values.flatten().tolist()),'lat':('id',temp['lat'].values.flatten().tolist()),'level':('id',temp['level'].values.flatten().tolist()),'fcst_time':[t_now]}).assign_coords({'id':('id',temp['id'].values.flatten().tolist())})
        var_s=xr.concat([var_s,temp],dim='fcst_time')    
        t_now = t_now+timedelta(seconds=dt)

    # modify by wzj 2024.5.24 尝试解决当输入为模式数据dtime有多个时，程序错误的bug
    if trans_dim == 'time':
        # time多个
        var_stda=var_s.rename({'fcst_time':trans_dim}).squeeze().to_dataframe(var_s.member.values[0]).reset_index().drop('member',axis=1)
    else:
        # dtime多个
        if 'dtime' not in var_s.dims and 'dtime' in var_s.coords:
            var_s = var_s.drop(['dtime']) # delete 冗余维度
        var_stda=var_s.rename({'fcst_time':trans_dim}).squeeze().to_dataframe(var_s.member.values[0]).reset_index().drop('member',axis=1)   
        var_stda[['dtime', 'time']] = var_stda[['time', 'dtime']]
        var_stda['dtime'] = 0
    var_stda.attrs=var_s.attrs
    var_stda.attrs['data_start_columns'] = 6
    return var_stda

if __name__ == '__main__' :
    levels=[925,850,700,500,200]
    init_times=pd.date_range('2022-07-20-08','2022-07-21-08',freq='1h')

    u=metdig.io.get_model_3D_grids(data_source='cds',data_name='era5',levels=levels,fhours=0,init_time=init_times,var_name='u')
    v=metdig.io.get_model_3D_grids(data_source='cds',data_name='era5',levels=levels,fhours=0,init_time=init_times,var_name='v')
    vvel=metdig.io.get_model_3D_grids(data_source='cds',data_name='era5',levels=levels,fhours=0,init_time=init_times,var_name='vvel')
    spfh=metdig.io.get_model_3D_grids(data_source='cds',data_name='era5',levels=levels,fhours=0,init_time=init_times,var_name='spfh')
    trajectoies=trajectory_on_pressure_level(u,v,vvel,var_diag=spfh,dt=-1800,t_s=datetime(2022,7,21,8))
    print(trajectoies)


def interpolate_3d(stda, hgt, points, stda_sfc=None, psfc=None,if_split=None):
    '''

    [利用位势高度，站点高度，和各层模式数据进行三维不规则点插值，获取初步订正的山地地形站点预报，
    对输入点的范围进行自动切割循环，以控制输入三维插值方法的数据范围，达到加速的效果]

    Arguments:
        stda {[stda]} -- [被插值的要素]
        hgt {[stda]} -- [模式位势高度]
        points {[{'lon':[110],'lat':[30],'alt':[1000]}]} -- [{被插值站点的经度，维度，高度}]
        stda_sfc {[stda]} -- [可选量,stda的对应地面量，当站点高度低于hgt中对应位置高度最小值，则直接用stda_sfc中的线性插值结果]
        psfc {[stda]} -- [当psfc<stda的等压面，则为模式地下部分，赋值nan，如果此时stda_sfc不为None,则为其线性插值结果]
        if_split  {None or int} -- [是否采用站点数据范围拆分方法加速多维插值]
    Returns:
        [stda] -- [被插值后的站点数据,超出给定范围复制nan]
    '''
    pnt_extent=[math.floor(min(points['lon'])),math.ceil(max(points['lon'])),math.floor(min(points['lat'])),math.ceil(max(points['lat']))]

    if if_split is None:
        stda_sta=interpolate_3d_whole_area(stda=stda,hgt=hgt,points=points,stda_sfc=stda_sfc,psfc=psfc)
    else:
        sta_lons=np.array(points['lon'])
        sta_lats=np.array(points['lat'])
        sta_alts=np.array(points['lat'])
        sta_ids=np.array(points['id'])
        stda_sta=[]
        lon_s=pnt_extent[0]
        while(lon_s < pnt_extent[1]+if_split):
            lon_e=lon_s+if_split
            lat_s=pnt_extent[2]
            while(lat_s < pnt_extent[3]+if_split):
                lat_e=lat_s+if_split
                idx_in=np.where((sta_lons>=lon_s) & (sta_lats>=lat_s) & (sta_lons<lon_e) & (sta_lats<lat_e))
                if(idx_in[0].size > 0):
                    points_split={'lon':sta_lons[idx_in],'lat':sta_lats[idx_in],'alt':sta_alts[idx_in],'id':sta_ids[idx_in]}
                    stda_cut=utl.area_cut(stda,extent=[lon_s,lon_e,lat_s,lat_e])
                    hgt_cut=utl.area_cut(hgt,extent=[lon_s,lon_e,lat_s,lat_e])
                    stda_sta.append(interpolate_3d_whole_area(stda=stda_cut,hgt=hgt_cut,points=points_split,stda_sfc=stda_sfc,psfc=psfc))
                lat_s=lat_e
            lon_s=lon_e
        stda_sta=pd.concat(stda_sta)
    return stda_sta

def interpolate_3d_whole_area(stda, hgt, points, stda_sfc=None, psfc=None):
    '''

    [利用位势高度，站点高度，和各层模式数据进行三维不规则点插值，获取初步订正的山地地形站点预报,该方法对全区域进行直接三维插值，对于范围较大的数据运行效率会很慢]

    Arguments:
        stda {[stda]} -- [被插值的要素]
        hgt {[stda]} -- [模式位势高度]
        points {'lon':[110],'lat':[30],'alt':[1000]} -- [{被插值站点的经度，维度，高度}]
        stda_sfc {[stda]} -- [可选量,stda的对应地面量，当站点高度低于hgt中对应位置高度最小值，则直接用stda_sfc中的线性插值结果]
        psfc {[stda]} -- [当psfc<stda的等压面，则为模式地下部分，赋值nan，如果此时stda_sfc不为None,则为其线性插值结果]
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

    if(psfc is not None):
        stda = mask_terrian(psfc, stda) 
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
        hgt_sta_level = list(hgt_sta['level'].values) # add by wzj 增加离地最近层次查找
        hgt_sta_level_max_index = hgt_sta_level.index(max(hgt_sta_level))
        for idx_member,imember in enumerate(stda.member.values):
            for idx_time,itime in enumerate(stda.time.values):
                for idx_dtime,idtime in enumerate(stda.dtime.values):
                    try:#防止某一数据不全
                        for idx,iid in enumerate(ids):
                            if((hgt_sta.sel(dtime=idtime,time=itime,member=imember,id=iid).isel(level=hgt_sta_level_max_index).values > points['alt'][idx]) or (stda_sta[imember].loc[(stda_sta['dtime']==idtime)&(stda_sta['dtime']==idtime)&(stda_sta['time']==itime)&(stda_sta['id']==iid)].values[0] == np.nan)): #psfc参数所用
                                stda_sta[imember].loc[(stda_sta['dtime']==idtime)&(stda_sta['dtime']==idtime)&(stda_sta['time']==itime)&(stda_sta['id']==iid)]=stda_sfc_sta.sel(dtime=idtime,time=itime,member=imember,id=iid).values[0]
                            else:
                                continue
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
    id_selected=54511
    init_time=datetime(2022,5,31,8)
    levels=[1000,850,700,500,200,100]
    fhour=36
    data_source='cassandra'
    data_name='ecmwf_ens'

    sta_info=pd.read_csv(r'L:\RoutineJob\FISU\obs/sta_info_national.csv',encoding='gbk')
    points={'lon':sta_info['lon'].to_list(),'lat':sta_info['lat'].to_list(),'alt':sta_info['alt'].to_list(),'id':sta_info['id'].to_list()}

    # get data
    extent=[min(points['lon'])-1,max(points['lon'])+1,min(points['lat'])-1,max(points['lat'])+1]
    u=metdig.io.get_model_3D_grid(init_time=init_time,fhour=fhour,levels=levels,
                                data_source=data_source,data_name=data_name,var_name='u',extent=extent)
    v=metdig.io.get_model_3D_grid(init_time=init_time,fhour=fhour,levels=levels,
                                data_source=data_source,data_name=data_name,var_name='v',extent=extent)
    tmp=metdig.io.get_model_3D_grid(init_time=init_time,fhour=fhour,levels=levels,
                                data_source=data_source,data_name=data_name,var_name='tmp',extent=extent)
    u10m=metdig.io.get_model_grid(init_time=init_time,fhour=fhour,
                                    data_source=data_source,data_name=data_name,var_name='u10m',extent=extent)        
    v10m=metdig.io.get_model_grid(init_time=init_time,fhour=fhour,
                                    data_source=data_source,data_name=data_name,var_name='v10m',extent=extent)        
    t2m=metdig.io.get_model_grid(init_time=init_time,fhour=fhour,
                                    data_source=data_source,data_name=data_name,var_name='t2m',extent=extent)

    hgt=metdig.io.get_model_3D_grid(init_time=init_time,fhour=fhour,levels=levels,
                                data_source=data_source,data_name=data_name,var_name='hgt',extent=extent)

    s=datetime.now()
    u10m_md=metdig.cal.interpolate.interpolate_3d(u, hgt, points, stda_sfc=u10m,if_split=None)
    e=datetime.now()
    print((e-s).total_seconds())
    # v10m_md=metdig.cal.interpolate.interpolate_3d(v, hgt, points, stda_sfc=v10m)
    # t2m_md=metdig.cal.interpolate.interpolate_3d(tmp, hgt, points, stda_sfc=t2m)
