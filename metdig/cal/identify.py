'''
天气学系统识别算法

author: 刘凑华
date: 2023-5-25

'''

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pkg_resources
import meteva.base as meb

from metdig.cal.lib import utility as utl
from metdig.cal.lib.utility import unifydim_stda, check_stda

from metdig.io.lib import config as CONFIG

__all__ = [
    'high_low_center',
    'vortex',
    'vortex_trace_from_vortex',
    'vortex_trace',
    'trough',
    'reverse_trough',
    'convergence_line',
    'shear',
    'jet',
    'subtropical_high',
    'south_asia_high',
    'tran_graphy_to_df',
]


pkg_name = 'metdig.cal'

ws_jar_path = pkg_resources.resource_filename(pkg_name, "resources/sysIdentify2024.jar")
height_oy = pkg_resources.resource_filename(pkg_name, "resources/height_oy.nc")

output_dir_root = os.path.join(CONFIG.get_cache_dir(), 'cal_identify')

def java_class_func(jar_path, class_name, func_name, jvm_path=None, *args):
    try:
        import jpype
    except:
        raise Exception("jpype not exists, please install jpype first, such as: pip install jpype1")
    """
    调用jar包中class下的方法
    :return:
    """
    # jar包路径的配置
    if jar_path is None or not os.path.exists(jar_path):
        raise Exception("jar not exists")
    # 这里指定了jvm
    if jvm_path:
        jvmpath = jvm_path
    else:
        try:
            jvmpath = jpype.getDefaultJVMPath()
        except Exception as e:
            msg = str(e)
            msg += "\n"
            msg += "jre not found, please install jre first, you can download jre installation package from https://www.java.com/zh-CN/download\n"
            raise Exception("jvm path error")

    try:
        jpype.startJVM(jvmpath, "-ea", "-Djava.class.path=%s" % jar_path)
    except Exception as e:
        pass

    java_class = jpype.JClass(class_name)
    ru_param = ','.join(list(map(lambda x: json.dumps(x), args)))
    # f1 = open(r"d:/para.txt","w")
    # f1.write(ru_param)
    # f1.close()
    res = str(eval("java_class.%s(%s)" % (func_name, ru_param)))
    # jpype.shutdownJVM()
    return res


@check_stda(['hgt'])
def high_low_center(hgt, resolution="low", smooth_times=0, min_size=100, grade_interval=5):
    r"""高低压中心识别
    从输入的气压场或位势高度场中识别出高压和低压的范围、中心位置，并计算出面积和强度
    By 刘凑华

    Parameters
    ----------
    hgt : `stda`
        气压或位势高度场网格数据，暂时只支持包含一个平面场
    
    resolution : `str`, optional
        系统识别算法涉及较多参数，而这些参数的最有值和网格分辨率有关，为了简化系统识别算法的使用，
        默认会将网格数据转化成两种固定的分辨率（0.5°或0.1°）的数据，当resolution ="low"时，会转化成0.5°分辨率，当resolution = "high"时，会转化成0.1°，
        算法内置了相关的最优参数
        defaults to "low"
    
    smooth_times : `int`, optional
        调用系统识别算法可以根据需求对输入的气压场或位势高度场进行平滑，以过滤较小尺度的噪音
        default to 0
    
    min_size : `int`, optional
        调用系统识别算法后，可以根据高低压系统的尺度过滤掉一些尺度较小系统，其中系统尺度是以高（低）压中心到最近的鞍点的距离来代表
        default to 100
    
    grade_interval : `int`, optional
        调用系统识别算法后，可以根据高低压中心是否有闭合等值线来决定是否保留该中心，grade_interval是闭合等值线的等级值
        default to 5

    Returns
    -------
    `dict`
        系统识别的结果，以字典形式返回
    """
    try:
        output_dir = os.path.join(output_dir_root, hgt.attrs['data_source'], hgt['member'].values[0])
    except:
        output_dir = os.path.join(output_dir_root, 'default')

    data = utl.stda_to_quantity(hgt).to('gpm')
    data = np.array(data)
    data = data.flatten().tolist()
    
    height_oy_data = meb.read_griddata_from_nc(height_oy)
    grid_h = meb.get_grid_of_data(height_oy_data)
    h_data = height_oy_data.values.flatten().tolist()

    para = {"type": "high_low_center",
            "smooth_times": smooth_times, "min_size": min_size, "resolution": resolution, "grade_interval": grade_interval,
            "level": int(hgt.stda.level[0]), "time": hgt.stda.time[0].strftime("%Y%m%d%H"), "dtime": int(hgt.stda.dtime[0]),
            "nlon": hgt['lon'].size, "nlat": hgt['lat'].size, "startlon": float(hgt['lon'].values[0]), "startlat": float(hgt['lat'].values[0]),
            "dlon": float(hgt.stda.horizontal_resolution.round(5)), "dlat": float(hgt.stda.vertical_resolution.round(5)),
            "data": data, "output_dir_root": output_dir,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(ws_jar_path, "Jpype", "ws", None, para_json)
    if str_json and str_json != "null":
        graphy = json.loads(str_json)
        ids = meb.read_griddata_from_micaps4(output_dir + f"/high_low_center/{int(hgt.stda.level[0])}/id/{hgt.stda.time[0]:%y%m%d%H}.{int(hgt.stda.dtime[0]):03d}")
        ids = ids.assign_coords({'level': hgt.level.values})
        ids.attrs = hgt.attrs
        ids.attrs['var_name'] = 'ids'
        ids.attrs['var_cn_name'] = '高低压编号'
        ids.attrs['var_units'] = ''
        return {'graphy': graphy, 'ids': ids}
    else:
        return None


@check_stda(['u', 'v'])
def vortex(u, v, resolution="low", smooth_times=0, min_size=100):
    r"""涡旋识别
    从输入的风场中识别出涡旋中心位置，以涡旋中心为中心，以涡旋中心到最近的一个鞍点的距离为半径，画一个圆作为涡旋的范围，
    以围绕圆形上的环流作为涡旋的强度。算法会返回涡旋的中心位置、面积和强度
    By 刘凑华

    Parameters
    ----------
    u : `stda`
        u分量风场数据，暂时只支持数据只包含单个平面的情景
    v : `stda`
        v分量风场数据，暂时只支持数据只包含单个平面的情景

    resolution : `str`, optional
        系统识别算法涉及较多参数，而这些参数的最有值和网格分辨率有关，为了简化系统识别算法的使用，
        默认会将网格数据转化成两种固定的分辨率（0.5°或0.1°）的数据，当resolution ="low"时，会转化成0.5°分辨率，当resolution = "high"时，会转化成0.1°，
        算法内置了相关的最优参数
        default to "low"
    
    smooth_times : `int`, optional
        调用系统识别算法可以根据需求对输入的风场场进行平滑，以过滤较小尺度的噪音
        default to 0
    
    min_size : `int`, optional
        调用系统识别算法后，可以根据高低压系统的尺度过滤掉一些尺度较小系统，其中系统尺度是以高（低）压中心到最近的鞍点的距离来代表
        default to 100


    Returns
    -------
    `dict`
        系统识别的结果，以字典形式返回
    """
    try:
        output_dir = os.path.join(output_dir_root, u.attrs['data_source'], u['member'].values[0])
    except:
        output_dir = os.path.join(output_dir_root, 'default')

    data = np.append(u.values.flatten(), v.values.flatten())
    data = data.flatten().tolist()
    
    height_oy_data = meb.read_griddata_from_nc(height_oy)
    grid_h = meb.get_grid_of_data(height_oy_data)
    h_data = height_oy_data.values.flatten().tolist()

    para = {"type": "vortex",
            "smooth_times": smooth_times, "min_size": min_size, "resolution": resolution,
            "level": int(u.stda.level[0]), "time": u.stda.time[0].strftime("%Y%m%d%H"), "dtime": int(u.stda.dtime[0]),
            "nlon": u['lon'].size, "nlat": u['lat'].size, "startlon": float(u['lon'].values[0]), "startlat": float(u['lat'].values[0]),
            "dlon": float(u.stda.horizontal_resolution.round(5)), "dlat": float(u.stda.vertical_resolution.round(5)),
            "data": data, "output_dir_root": output_dir,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(ws_jar_path, "Jpype", "ws", None, para_json)
    if str_json and str_json != "null":
        graphy = json.loads(str_json)
        ids = meb.read_griddata_from_micaps4(output_dir + f"/vortex/{int(u.stda.level[0])}/id/{u.stda.time[0]:%y%m%d%H}.{int(u.stda.dtime[0]):03d}")
        ids = ids.assign_coords({'level': u.level.values})
        ids.attrs = u.attrs
        ids.attrs['var_name'] = 'ids'
        ids.attrs['var_cn_name'] = '涡旋编号'
        ids.attrs['var_units'] = ''
        return {'graphy': graphy, 'ids': ids}
    else:
        return None

def vortex_trace_from_vortex(vortexs):
    """基于涡旋，识别涡旋轨迹

    Args:
        vortexs (pd.DataFrame): ['time', 'dtime', 'lon', 'lat', 'area']

    Returns:
        pd.DataFrame: ["time","dtime","id","lon","lat","ob_time","area"]
    """

    trace_list = []
    id = 0
    last_ob_time = None
    for fo_time in vortexs['time'].drop_duplicates().sort_values():
        for dtime in vortexs['dtime'].drop_duplicates().sort_values():
            ob_time = fo_time + timedelta(hours=dtime)
            graphy = vortexs[(vortexs['time']==fo_time) & (vortexs['dtime']==dtime)]
            if len(graphy) == 0:
                continuecontinue
            # print(graphy)

            cent_list = []
            for index, row in graphy.iterrows():
                cent = {}   
                cent["time"] = fo_time
                cent["dtime"] = dtime
                cent["lon"] = row['lon']
                cent["lat"] = row['lat']
                cent["area"] = row['area']
                cent["ob_time"] = ob_time
                cent_list.append(cent)

            if len(cent_list)>0:
                used_list = np.zeros(len(cent_list))

                if len(trace_list)>0:
                    dis_array = np.zeros((len(cent_list),len(trace_list))) + 999999
                    for k in range(len(cent_list)):
                        cent = cent_list[k]
                        for t in range(len(trace_list)):
                            trace = trace_list[t]
                            if trace[-1]["ob_time"] == last_ob_time: #轨迹的最后一个时刻在前一刻还存在
                                if len(trace) ==1:
                                    next_lon = trace[0]["lon"]
                                    next_lat = trace[0]["lat"]
                                else:
                                    dh0 = (trace[-1]["ob_time"] - trace[-2]["ob_time"]).total_seconds()/3600
                                    dlon = trace[-1]["lon"] - trace[-2]["lon"]
                                    dlat = trace[-1]["lat"] - trace[-2]["lat"]
                                    dh1 = (ob_time - trace[-1]["ob_time"]).total_seconds()/3600
                                    next_lon = trace[-1]["lon"] + dh1 * dlon / dh0
                                    next_lat = trace[-1]["lat"] + dh1 * dlat / dh0

                                dis = meb.tool.math_tools.distance_on_earth_surface(next_lon,next_lat,cent["lon"],cent["lat"])
                                dis_array[k,t] = dis
                    mindis = np.min(dis_array)
                    while mindis <500:
                        index = np.where(dis_array == mindis)
                        km = index[0][0]
                        tm = index[1][0]
                        cent = cent_list[km]
                        cent["id"] = tm
                        trace_list[tm].append(cent)
                        dis_array[km,:] = 999999
                        dis_array[:,tm] = 999999
                        mindis = np.min(dis_array)
                        used_list[km] = 1


                for k in range(len(used_list)):
                    if used_list[k]==0:
                        cent = cent_list[k]
                        cent["id"] = id
                        trace = [cent]
                        trace_list.append(trace)
                        id += 1
            last_ob_time = ob_time  #记录上一个场的时间

    trace_all = []
    for trace in trace_list:
        trace_all.extend(trace)
    df = pd.DataFrame(trace_all)
    df1 = df[["time","dtime","id","lon","lat","ob_time","area"]]
    df1.sort_values(by=["id","time","dtime"],inplace=True)
    return df1

@check_stda(['u', 'v'])
@unifydim_stda(['u', 'v'])
def vortex_trace(u, v):
    """基于uv风场，识别涡旋轨迹

    Args:
        u (stda): u分量风场数据
        v (stda): v分量风场数据

    Returns:
        pd.DataFrame: ["time","dtime","id","lon","lat","ob_time","area"]
    """

    vortexs = []

    for fo_time in u.stda.time:
        for dtime in u.stda.dtime:
            ob_time = fo_time + timedelta(hours=dtime)
            # print(fo_time, dtime, ob_time)
            ret = vortex(u.sel(time=[fo_time],dtime=[dtime]), 
                         v.sel(time=[fo_time],dtime=[dtime]))
            if ret is None:
                continue
            graphy = ret["graphy"]

            cent_list = []
            for key in graphy["features"].keys():
                cent = graphy["features"][key]["center"]
                cent["time"] = fo_time
                cent["dtime"] = dtime
                cent["area"] = graphy["features"][key]["region"]["area"]
                cent["ob_time"] = ob_time
                cent_list.append(cent)
            vortexs.extend(cent_list)
            continue
    
    if len(vortexs) == 0:
        return
    
    vortexs = pd.DataFrame(vortexs)
    vortexs = vortexs[['time', 'dtime', 'lon', 'lat', 'area']]
    
    return vortex_trace_from_vortex(vortexs)


@check_stda(['hgt'])
def trough(hgt, resolution="low", smooth_times=0, min_size=100):
    r"""槽线识别
    从输入的500hPa位势高度场中识别出槽线，并计算出面积和强度
    By 刘凑华

    Parameters
    ----------
    hgt : `stda`
        气压或位势高度场网格数据，暂时只支持包含一个平面

    resolution : `str`, optional
        系统识别算法涉及较多参数，而这些参数的最有值和网格分辨率有关，为了简化系统识别算法的使用，
        默认会将网格数据转化成两种固定的分辨率（0.5°或0.1°）的数据，当resolution ="low"时，会转化成0.5°分辨率，当resolution = "high"时，会转化成0.1°，
        算法内置了相关的最优参数
        default to "low"
    
    smooth_times : `int`, optional
        调用系统识别算法可以根据需求对输入的气压场或位势高度场进行平滑，以过滤较小尺度的噪音
        default to 0
    
    min_size : `int`, optional
        调用系统识别算法后，可以根据槽线的长度（单位km）过滤掉一些尺度较小系统
        default to 100


    Returns
    -------
    `dict`
        系统识别的结果，以字典形式返回
    """
    try:
        output_dir = os.path.join(output_dir_root, hgt.attrs['data_source'], hgt['member'].values[0])
    except:
        output_dir = os.path.join(output_dir_root, 'default')

    data = utl.stda_to_quantity(hgt).to('gpm')
    data = np.array(data)
    data = data.flatten().tolist()
    
    height_oy_data = meb.read_griddata_from_nc(height_oy)
    grid_h = meb.get_grid_of_data(height_oy_data)
    h_data = height_oy_data.values.flatten().tolist()

    para = {"type": "trough",
            "smooth_times": smooth_times, "min_size": min_size, "resolution": resolution,
            "level": int(hgt.stda.level[0]), "time": hgt.stda.time[0].strftime("%Y%m%d%H"), "dtime": int(hgt.stda.dtime[0]),
            "nlon": hgt['lon'].size, "nlat": hgt['lat'].size, "startlon": float(hgt['lon'].values[0]), "startlat": float(hgt['lat'].values[0]),
            "dlon": float(hgt.stda.horizontal_resolution.round(5)), "dlat": float(hgt.stda.vertical_resolution.round(5)),
            "data": data, "output_dir_root": output_dir,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(ws_jar_path, "Jpype", "ws", None, para_json)
    if str_json and str_json != "null":
        graphy = json.loads(str_json)
        return {'graphy': graphy}
    else:
        return None


@check_stda(['hgt'])
def reverse_trough(hgt, resolution="low", smooth_times=0, min_size=100):
    r"""倒槽识别
    从输入的气压场或位势高度场中识别出倒槽，并计算出面积和强度。倒槽的识别方法和槽线类似，只不过增加了对槽线起止点相对位置的判断。
    By 刘凑华

    Parameters
    ----------
    hgt : `stda`
        气压或位势高度场网格数据，暂时只支持包含一个平面场

    resolution : `str`, optional
        系统识别算法涉及较多参数，而这些参数的最有值和网格分辨率有关，为了简化系统识别算法的使用，
        默认会将网格数据转化成两种固定的分辨率（0.5°或0.1°）的数据，当resolution ="low"时，会转化成0.5°分辨率，当resolution = "high"时，会转化成0.1°，
        算法内置了相关的最优参数
        default to "low"
    
    smooth_times : `int`, optional
        调用系统识别算法可以根据需求对输入的气压场或位势高度场进行平滑，以过滤较小尺度的噪音
        default to 0
    
    min_size : `int`, optional
        调用系统识别算法后，可以根据倒槽的槽线长度（单位km）过滤掉一些尺度较小系统
        default to 100

    Returns
    -------
    `dict`
        系统识别的结果，以字典形式返回
    """
    try:
        output_dir = os.path.join(output_dir_root, hgt.attrs['data_source'], hgt['member'].values[0])
    except:
        output_dir = os.path.join(output_dir_root, 'default')

    data = utl.stda_to_quantity(hgt).to('gpm')
    data = np.array(data)
    data = data.flatten().tolist()
    
    height_oy_data = meb.read_griddata_from_nc(height_oy)
    grid_h = meb.get_grid_of_data(height_oy_data)
    h_data = height_oy_data.values.flatten().tolist()

    para = {"type": "reverse_trough",
            "smooth_times": smooth_times, "min_size": min_size, "resolution": resolution,
            "level": int(hgt.stda.level[0]), "time": hgt.stda.time[0].strftime("%Y%m%d%H"), "dtime": int(hgt.stda.dtime[0]),
            "nlon": hgt['lon'].size, "nlat": hgt['lat'].size, "startlon": float(hgt['lon'].values[0]), "startlat": float(hgt['lat'].values[0]),
            "dlon": float(hgt.stda.horizontal_resolution.round(5)), "dlat": float(hgt.stda.vertical_resolution.round(5)),
            "data": data, "output_dir_root": output_dir,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)
    str_json = java_class_func(ws_jar_path, "Jpype", "ws", None, para_json)
    if str_json and str_json != "null":
        graphy = json.loads(str_json)
        return {'graphy': graphy}
    else:
        return None


@check_stda(['u', 'v'])
@unifydim_stda(['u', 'v'])
def convergence_line(u, v, resolution="low", smooth_times=0, min_size=100):
    r"""辐合线识别
    从输入的风场中识别出辐合线，并计算出面积和强度。
    By 刘凑华

    Parameters
    ----------
    u : `stda`
        u分量风场数据，暂时只支持数据只包含单个平面的情景
    v : `stda`
        v分量风场数据，暂时只支持数据只包含单个平面的情景

    resolution : `str`, optional
        系统识别算法涉及较多参数，而这些参数的最有值和网格分辨率有关，为了简化系统识别算法的使用，
        默认会将网格数据转化成两种固定的分辨率（0.5°或0.1°）的数据，当resolution ="low"时，会转化成0.5°分辨率，当resolution = "high"时，会转化成0.1°，
        算法内置了相关的最优参数
        default to "low"
    
    smooth_times : `int`, optional
        调用系统识别算法可以根据需求对输入的风场进行平滑，以过滤较小尺度的噪音
        default to 0
    
    min_size : `int`, optional
        调用系统识别算法后，可以根据辐合线的长度（单位km）过滤掉一些尺度较小系统
        default to 100

    Returns
    -------
    `dict`
        系统识别的结果，以字典形式返回
    """
    try:
        output_dir = os.path.join(output_dir_root, u.attrs['data_source'], u['member'].values[0])
    except:
        output_dir = os.path.join(output_dir_root, 'default')

    data = np.append(u.values.flatten(), v.values.flatten())
    data = data.flatten().tolist()
    
    height_oy_data = meb.read_griddata_from_nc(height_oy)
    grid_h = meb.get_grid_of_data(height_oy_data)
    h_data = height_oy_data.values.flatten().tolist()

    para = {"type": "convergence_line",
            "smooth_times": smooth_times, "min_size": min_size, "resolution": resolution,
            "level": int(u.stda.level[0]), "time": u.stda.time[0].strftime("%Y%m%d%H"), "dtime": int(u.stda.dtime[0]),
            "nlon": u['lon'].size, "nlat": u['lat'].size, "startlon": float(u['lon'].values[0]), "startlat": float(u['lat'].values[0]),
            "dlon": float(u.stda.horizontal_resolution.round(5)), "dlat": float(u.stda.vertical_resolution.round(5)),
            "data": data, "output_dir_root": output_dir,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(ws_jar_path, "Jpype", "ws", None, para_json)
    if str_json and str_json != "null":
        graphy = json.loads(str_json)
        return {'graphy': graphy}
    else:
        return None


@check_stda(['u', 'v'])
@unifydim_stda(['u', 'v'])
def shear(u, v, resolution="low", smooth_times=0, min_size=100):
    r"""切变线识别
    从输入的风场中识别出切变线，并计算出面积和强度。
    By 刘凑华

    Parameters
    ----------
    stda : `stda`
    u : `stda`
        u分量风场数据，暂时只支持数据只包含单个平面的情景
    v : `stda`
        v分量风场数据，暂时只支持数据只包含单个平面的情景

    resolution : `str`, optional
        系统识别算法涉及较多参数，而这些参数的最有值和网格分辨率有关，为了简化系统识别算法的使用，
        默认会将网格数据转化成两种固定的分辨率（0.5°或0.1°）的数据，当resolution ="low"时，会转化成0.5°分辨率，当resolution = "high"时，会转化成0.1°，
        算法内置了相关的最优参数
        default to "low"
    
    smooth_times : `int`, optional
        调用系统识别算法可以根据需求对输入的风场进行平滑，以过滤较小尺度的噪音
        default to 0
    
    min_size : `int`, optional
        调用系统识别算法后，可以根据切变线的长度（单位km）过滤掉一些尺度较小系统
        default to 100

    Returns
    -------
    `dict`
        系统识别的结果，以字典形式返回
    """
    try:
        output_dir = os.path.join(output_dir_root, u.attrs['data_source'], u['member'].values[0])
    except:
        output_dir = os.path.join(output_dir_root, 'default')

    data = np.append(u.values.flatten(), v.values.flatten())
    data = data.flatten().tolist()
    
    height_oy_data = meb.read_griddata_from_nc(height_oy)
    grid_h = meb.get_grid_of_data(height_oy_data)
    h_data = height_oy_data.values.flatten().tolist()

    para = {"type": "shear",
            "smooth_times": smooth_times, "min_size": min_size, "resolution": resolution,
            "level": int(u.stda.level[0]), "time": u.stda.time[0].strftime("%Y%m%d%H"), "dtime": int(u.stda.dtime[0]),
            "nlon": u['lon'].size, "nlat": u['lat'].size, "startlon": float(u['lon'].values[0]), "startlat": float(u['lat'].values[0]),
            "dlon": float(u.stda.horizontal_resolution.round(5)), "dlat": float(u.stda.vertical_resolution.round(5)),
            "data": data, "output_dir_root": output_dir,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(ws_jar_path, "Jpype", "ws", None, para_json)
    if str_json and str_json != "null":
        graphy = json.loads(str_json)
        return {'graphy': graphy}
    else:
        return None


@check_stda(['u', 'v'])
@unifydim_stda(['u', 'v'])
def jet(u, v, resolution="low", smooth_times=0, min_size=100, jet_min_speed=12, only_south_jet=False):
    r"""急流识别
    从输入的风场中识别出急流区、急流轴线，并计算出面积和强度。
    By 刘凑华

    Parameters
    ----------
    stda : `stda`
    u : `stda`
        u分量风场数据，暂时只支持数据只包含单个平面的情景
    v : `stda`
        v分量风场数据，暂时只支持数据只包含单个平面的情景

    resolution : `str`, optional
        系统识别算法涉及较多参数，而这些参数的最有值和网格分辨率有关，为了简化系统识别算法的使用，
        默认会将网格数据转化成两种固定的分辨率（0.5°或0.1°）的数据，当resolution ="low"时，会转化成0.5°分辨率，当resolution = "high"时，会转化成0.1°，
        算法内置了相关的最优参数
        default to "low"
    
    smooth_times : `int`, optional
        调用系统识别算法可以根据需求对输入的风场进行平滑，以过滤较小尺度的噪音
        default to 0
    
    min_size : `int`, optional
        调用系统识别算法后，可以根据切变线的长度（单位km）过滤掉一些尺度较小系统
        default to 100

    jet_min_speed : `int`, optional
        判断为急流的速度阈值，缺省值是850hPa高度的默认风速阈值12m/s
        default to 12
    
    only_south_jet : `bool`, optional
        是否仅保留南风急流，在中低层急流识别中常常仅保留南风急流，此时可设置该参数为True，对于200hPa高度的急流识别则一般设置为False
        default to False

    Returns
    -------
    `dict`
        系统识别的结果，以字典形式返回
    """
    try:
        output_dir = os.path.join(output_dir_root, u.attrs['data_source'], u['member'].values[0])
    except:
        output_dir = os.path.join(output_dir_root, 'default')

    data = np.append(u.values.flatten(), v.values.flatten())
    data = data.flatten().tolist()
    
    height_oy_data = meb.read_griddata_from_nc(height_oy)
    grid_h = meb.get_grid_of_data(height_oy_data)
    h_data = height_oy_data.values.flatten().tolist()

    para = {"type": "jet",
            "smooth_times": smooth_times, "min_size": min_size, "resolution": resolution, "jet_min_speed": jet_min_speed, "only_south_jet": str(only_south_jet),
            "level": int(u.stda.level[0]), "time": u.stda.time[0].strftime("%Y%m%d%H"), "dtime": int(u.stda.dtime[0]),
            "nlon": u['lon'].size, "nlat": u['lat'].size, "startlon": float(u['lon'].values[0]), "startlat": float(u['lat'].values[0]),
            "dlon": float(u.stda.horizontal_resolution.round(5)), "dlat": float(u.stda.vertical_resolution.round(5)),
            "data": data, "output_dir_root": output_dir,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(ws_jar_path, "Jpype", "ws", None, para_json)
    if str_json and str_json != "null":
        graphy = json.loads(str_json)
        return {'graphy': graphy}
    else:
        return None


@check_stda(['hgt'])
def subtropical_high(hgt, smooth_times=0, min_size=500, necessary_height=5840, sufficient_height=5880):
    r"""副高识别
    从输入的500hPa高度场中识别出副高、副高轴线，并计算出面积和强度。
    By 刘凑华

    Parameters
    ----------
    hgt : `stda`
        500hPa位势高度场网格数据，暂时只支持包含一个平面场

    resolution : `str`, optional
        系统识别算法涉及较多参数，而这些参数的最有值和网格分辨率有关，为了简化系统识别算法的使用，
        默认会将网格数据转化成两种固定的分辨率（0.5°或0.1°）的数据，当resolution ="low"时，会转化成0.5°分辨率，当resolution = "high"时，会转化成0.1°，
        算法内置了相关的最优参数
        default to "low"
    
    smooth_times : `int`, optional
        调用系统识别算法可以根据需求对输入的高度场进行平滑，以过滤较小尺度的噪音
        default to 0
    
    min_size : `int`, optional
        调用系统识别算法后，可以根据切变线的长度（单位km）过滤掉一些尺度较小系统
        default to 100

    necessary_height : `int`, optional
        通常人们判断副高的范围为5880线围绕的高压区域，但有些情况下也以5840线作为副高范围，因此副高的阈值并非是一个固定的值，
        而是一个介于某个区间的值。如果人为设置这个区间的范围，necessary_height 就是副高阈值的取值区间的下界
        default to 5840
    
    sufficient_height : `int`, optional
        sufficient_height是副高阈值的取值区间的上界
        default to 5880

    Returns
    -------
    `dict`
        系统识别的结果，以字典形式返回
    """
    try:
        output_dir = os.path.join(output_dir_root, hgt.attrs['data_source'], hgt['member'].values[0])
    except:
        output_dir = os.path.join(output_dir_root, 'default')

    data = utl.stda_to_quantity(hgt).to('gpm')
    data = np.array(data)
    data = data.flatten().tolist()
    
    height_oy_data = meb.read_griddata_from_nc(height_oy)
    grid_h = meb.get_grid_of_data(height_oy_data)
    h_data = height_oy_data.values.flatten().tolist()

    para = {"type": "subtropical_high",
            "smooth_times": smooth_times, "min_size": min_size, "necessary_height": necessary_height, "sufficient_height": sufficient_height,
            "level": int(hgt.stda.level[0]), "time": hgt.stda.time[0].strftime("%Y%m%d%H"), "dtime": int(hgt.stda.dtime[0]),
            "nlon": hgt['lon'].size, "nlat": hgt['lat'].size, "startlon": float(hgt['lon'].values[0]), "startlat": float(hgt['lat'].values[0]),
            "dlon": float(hgt.stda.horizontal_resolution.round(5)), "dlat": float(hgt.stda.vertical_resolution.round(5)),
            "data": data, "output_dir_root": output_dir,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(ws_jar_path, "Jpype", "ws", None, para_json)
    if str_json and str_json != "null":
        graphy = json.loads(str_json)
        return {'graphy': graphy}
    else:
        return None


@check_stda(['hgt'])
def south_asia_high(hgt, smooth_times=0, min_size=800, sn_height=16680):
    r"""南亚高压识别
    从输入的100hPa或200hPa高度场中识别出南亚高压、南亚高压轴线，并计算出面积和强度。
    By 刘凑华

    Parameters
    ----------
    stda : `stda`
        100hPa或200hPa位势高度场网格数据，暂时只支持包含一个平面场

    resolution : `str`, optional
        系统识别算法涉及较多参数，而这些参数的最有值和网格分辨率有关，为了简化系统识别算法的使用，
        默认会将网格数据转化成两种固定的分辨率（0.5°或0.1°）的数据，当resolution ="low"时，会转化成0.5°分辨率，当resolution = "high"时，会转化成0.1°，
        算法内置了相关的最优参数
        default to "low"
    
    smooth_times : `int`, optional
        调用系统识别算法可以根据需求对输入的高度进行平滑，以过滤较小尺度的噪音
        default to 0
    
    min_size : `int`, optional
        调用系统识别算法后，可以根据切变线的长度（单位km）过滤掉一些尺度较小系统
        default to 100

    sn_height : `int`, optional
        南亚高压的范围特征线对应的高度值，对100hPa来说通常设置为16680
        default to 16680

    Returns
    -------
    `dict`
        系统识别的结果，以字典形式返回
    """
    try:
        output_dir = os.path.join(output_dir_root, hgt.attrs['data_source'], hgt['member'].values[0])
    except:
        output_dir = os.path.join(output_dir_root, 'default')

    data = utl.stda_to_quantity(hgt).to('gpm')
    data = np.array(data)
    data = data.flatten().tolist()
    
    height_oy_data = meb.read_griddata_from_nc(height_oy)
    grid_h = meb.get_grid_of_data(height_oy_data)
    h_data = height_oy_data.values.flatten().tolist()

    para = {"type": "south_asia_high",
            "smooth_times": smooth_times, "min_size": min_size, "sn_height": sn_height,
            "level": int(hgt.stda.level[0]), "time": hgt.stda.time[0].strftime("%Y%m%d%H"), "dtime": int(hgt.stda.dtime[0]),
            "nlon": hgt['lon'].size, "nlat": hgt['lat'].size, "startlon": float(hgt['lon'].values[0]), "startlat": float(hgt['lat'].values[0]),
            "dlon": float(hgt.stda.horizontal_resolution.round(5)), "dlat": float(hgt.stda.vertical_resolution.round(5)),
            "data": data, "output_dir_root": output_dir,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(ws_jar_path, "Jpype", "ws", None, para_json)
    if str_json and str_json != "null":
        graphy = json.loads(str_json)
        return {'graphy': graphy}
    else:
        return None


def tran_graphy_to_df(graphy):
    r"""将识别结果转换DataFrame
    字典形式的识别结果包含的信息是完整的，基于它可以做很多精细的分析，但是有些情况下为了更方便地开展长序列的结果分析和统计，
    需将字典形式结果转换成规整的数据表格。 本函数的功能就是从输入的字典形式的天气系统识别结果中提取天气系统的中心点位置、中心点取值、面积、强度和轴线等属性，
    并将结果转换成dataframe形式
    By 刘凑华

    Parameters
    ----------
    graphy : `dict`
        字典形式的天气系统识别结果，例如上面示例中的高低压系统识别结果

    Returns
    -------
    `tuple`
        元组，
        第0个元素是包含中心点位置、取值、面积和强度的DataFrame数据，
        第1个元素是包含每一条轴线描点坐标的DataFrame数据。
        对于高低压和涡旋系统，不存在轴线，因此第1个元素返回结果为None，
        对于槽线天气和切变线等天气系统来说，轴线就是槽线和切变线的上每一个点的位置。
        对于切变线，暂时没有定义系统中心的位置和强度，因此第0个元素返回结果为None。
    """
    if graphy is None: return None,None

    dtime = int(graphy["dtime"])

    time  = meb.all_type_time_to_time64(graphy["time"])

    level = graphy["level"]

    ids = graphy["features"].keys()

    list1 = []
    center = None
    for id in ids:
        feature = graphy["features"][id]
        lon = feature["center"]["lon"]
        lat = feature["center"]["lat"]
        center_value = round(feature["center"]["value"],2)
        if len(feature["region"].keys())>0:
            area = round(feature["region"]["area"],2)
            strength = round(feature["region"]["strength"])
            dict1 = {"level":level,"time":time,"dtime":dtime,"id" :int(id),"lon":lon,"lat":lat,"value":center_value,"area":area,"strength":strength}
            list1.append(dict1)
    if len(list1)>0:
        center = pd.DataFrame(list1)

    list1 = []
    for id in ids:
        points = graphy["features"][id]["axes"]["point"]
        if len(points)>0:
            array = np.array(points)
            lon = array[:,0]
            lat = array[:,1]
            df = pd.DataFrame({"lon":lon,"lat":lat})
            df["id"] = int(id)
            list1.append(df)
    if len(list1)>0:
        df = pd.concat(list1,axis = 0)
        df["level"] = level
        df["time"] = time
        df["dtime"] = dtime
        df["data0"] = 0
        axes = meb.sta_data(df)
        return center,axes
    else:
        return center,None