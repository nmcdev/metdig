# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import xarray as xr
import numpy as np
import pandas as pd


def model_filename(initTime, fhour, UTC=False):
    """
        Construct model file name.

    Arguments:
        initTime {string or datetime object} -- model initial time,
            like 18042008' or datetime(2018, 4, 20, 8).
        fhour {int} -- model forecast hours.
    """

    if(UTC is False):
        if isinstance(initTime, datetime):
            return initTime.strftime('%y%m%d%H') + ".{:03d}".format(fhour)
        else:
            return initTime.strip() + ".{:03d}".format(fhour)
    else:
        if isinstance(initTime, datetime):
            return (initTime - timedelta(hours=8)).strftime('%y%m%d%H') + ".{:03d}".format(fhour)
        else:
            time_rel = (datetime.strptime('20' + initTime, '%Y%m%d%H') - timedelta(hours=8)).strftime('%y%m%d%H')
            return time_rel.strip() + ".{:03d}".format(fhour)


def obs_filename(obsTime, UTC=False):
    if(UTC is False):
        if isinstance(obsTime, datetime):
            return obsTime.strftime('%Y%m%d%H%M%S') + ".000"
        else:
            return obsTime.strip() + ".000"
    else:
        if isinstance(obsTime, datetime):
            return (obsTime - timedelta(hours=8)).strftime('%Y%m%d%H%M%S') + ".000"
        else:
            time_rel = (datetime.strptime(obsTime, '%Y%m%d%H%M%S') - timedelta(hours=8)).strftime('%Y%m%d%H%M%S')
            return time_rel.strip() + ".000"


def reset_id_back(sta):
    '''
    输入的sta的站号中可能有些站号包含a-z,A-Z的字母，对此将这些字母转换为对应的ASCII数字，再将整个字符串格式的站号转换为数值形式
    返回sta站号为整型
    '''
    # print(sta)
    values = sta['id'].values
    if type(values[0]) != str:
        values = values.astype(str)
        int_id = np.zeros(len(values)).astype(str)
        for i in range(len(values)):
            strs = values[i]
            if len(strs) > 5:
                int_id[i] = chr(int(strs[0:2])) + strs[2:]
        sta['id'] = int_id
    if isinstance(values[0], float):
        int_id = values.astype(np.int32)
        sta["id"] = int_id


def area_cut(data, extent, x_percent, y_percent):
    '''
    区域裁剪 
    '''
    if extent is None:
        return data

    delt_x = (extent[1] - extent[0]) * x_percent
    delt_y = (extent[3] - extent[2]) * y_percent
    cut_extent = (extent[0] - delt_x, extent[1] + delt_x, extent[2] - delt_y, extent[3] + delt_y)

    if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset) :
        return data.where((data['lon'] >= cut_extent[0]) &
                          (data['lon'] <= cut_extent[1]) &
                          (data['lat'] >= cut_extent[2]) &
                          (data['lat'] <= cut_extent[3]), drop=True)

    elif isinstance(data, pd.DataFrame):
        return data[(data['lon'] > cut_extent[0]) &
                    (data['lon'] < cut_extent[1]) &
                    (data['lat'] > cut_extent[2]) &
                    (data['lat'] < cut_extent[3])]


def sta_select_id(df, id_selected):
    '''
    从df.index中筛选id_selected
    '''
    if len(df) == 0:
        return df
    if id_selected is None:
        return df

    if not isinstance(id_selected, list) and not isinstance(id_selected, np.ndarray):
        id_selected = [id_selected]

    id_selected = np.array(id_selected).astype(df.index.dtype)

    try:
        data = df.loc[id_selected]
    except Exception as e:
        # print(str(e) + '|| PAMR:obs_time={}, data_name={}, var_name={}, level={}'.format(obs_time, data_name, var_name, level))
        data = df.drop(index=df.index)
    return data
