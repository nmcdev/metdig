'''

nmc_met_io.retrieve_micaps_server的拓展方法，后续若nmc_met_io有相同功能的方法，可去除此处方法

'''

import json
import numpy as np
import xarray as xr
import pandas as pd
import pickle

import nmc_met_io.config as CONFIG
from nmc_met_io import DataBlock_pb2
from nmc_met_io.retrieve_micaps_server import GDSDataService

def get_wind_profiler(directory, filename=None, suffix="*.JSON", dropna=True, cache=True, cache_clear=True):

    """
    该程序用于读取micaps服务器上WIND_PROFILER的风廓线雷达数据.

    :param directory: the data directory on the service
    :param filename: the data filename, if none, will be the latest file.
    :param suffix: the filename filter pattern which will be used to
    :param dropna: the column which values is all na will be dropped.
    :param cache: cache retrieved data to local directory, default is True.
    :return: pandas DataFrame.

    >>> data = get_wind_profiler('WIND_PROFILER/RAD/54304/')
    >>> data = get_wind_profiler('WIND_PROFILER/RAD/54304/', filename='20210603130334.JSON')
    """
    # get data file name
    if filename is None:
        try:
            # connect to data service
            service = GDSDataService()
            status, response = service.getLatestDataName(directory, suffix)
        except ValueError:
            print('Can not retrieve data from ' + directory)
            return None
        StringResult = DataBlock_pb2.StringResult()
        if status == 200:
            StringResult.ParseFromString(response)
            if StringResult is not None:
                filename = StringResult.name
                if filename == '':
                    return None
            else:
                return None

    # retrieve data from cached file
    if cache:
        cache_file = CONFIG.get_cache_file(directory, filename, name="MICAPS_DATA", cache_clear=cache_clear)
        if cache_file.is_file():
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                return data

    # get data contents
    try:
        service = GDSDataService()
        status, response = service.getData(directory, filename)
    except ValueError:
        print('Can not retrieve data' + filename + ' from ' + directory)
        return None
    ByteArrayResult = DataBlock_pb2.ByteArrayResult()
    if status == 200:
        ByteArrayResult.ParseFromString(response)
        if ByteArrayResult is not None:
            byteArray = ByteArrayResult.byteArray

            data_dic = json.loads(byteArray)

            records = pd.DataFrame(data_dic['data'])
            col1 = list(records.columns)
            col2 = []
            for k,v in data_dic.items():
                if k != 'data':
                    records[k] = v
                    col2.append(k)
            records = records[col2 + col1]
            
            # drop all NaN columns
            if dropna:
                records = records.dropna(axis=1, how='all')
            
            # type format
            for col in records.columns:
                if col == 'observationTime':
                    records[col] = pd.to_datetime(records[col], format='%Y%m%d%H%M%S')
                else:
                    records[col] = pd.to_numeric(records[col], errors='ignore')

            # cache records
            if cache:
                with open(cache_file, 'wb') as f:
                    pickle.dump(records, f, protocol=pickle.HIGHEST_PROTOCOL)

            # return
            return records
        else:
            return None
    else:
        return None
if __name__ == '__main__':
    df = get_wind_profiler('WIND_PROFILER/RAD/54304/', filename='20210603130334.JSON', cache=True)
    # print(df)
    print(df.columns)

    df = get_wind_profiler('WIND_PROFILER/ROBS/52889/', filename='20210603135400.JSON', cache=True)
    print(df.columns)
    exit()
