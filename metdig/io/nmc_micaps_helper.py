'''

nmc_met_io.retrieve_micaps_server的拓展方法，后续若nmc_met_io有相同功能的方法，可去除此处方法

'''

import json
import time
import datetime
import numpy as np
import xarray as xr
import pandas as pd
import pickle

import nmc_met_io.retrieve_micaps_server as nmc_micaps_io

import nmc_met_io.config as CONFIG
from nmc_met_io import DataBlock_pb2
from nmc_met_io.retrieve_micaps_server import GDSDataService


def get_obs_filename(directory, filename_format, obs_time=None, isnearesttime=False):
    """[获取实况数据文件名以及日期]

    Args:
        directory ([str]): [cassandra中的目录，如：RADARMOSAIC/CREF/]
        filename_format ([str]): [cassandra中的文件名，必须带日期格式化的字符串，能用strftime正常格式化的字符串，如：ACHN_CREF_%Y%m%d_%H%M%S.BIN]
        obs_time ([dateime], optional): [需要读取的实况时间]. Defaults to None.
        isnearesttime (bool, optional): [如果obs_time非空，是否需要读取离obs_time最近的实况]. Defaults to False.
    """
    if obs_time is None:
        fnames = nmc_micaps_io.get_file_list(directory, latest=1) # 此方法如果遇到文件量多的情况会有点慢，后续看是否能优化
        if len(fnames) == 0:
            raise Exception('Can not retrieve data from ' + directory)
        filename = fnames[0]  # obs_time为空，获取第一个就是最新的
    else:
        if isnearesttime:
            fnames = nmc_micaps_io.get_file_list(directory)  # 目录下所有文件名， 此方法如果遇到文件量多的情况会有点慢，后续看是否能优化
            if len(fnames) == 0:
                raise Exception('Can not retrieve data from ' + directory)
            fnames.sort(reverse=True)  # 按照日期从大到小排序
            times = list(map(lambda x: datetime.datetime.strptime(x, filename_format), fnames))  # 目录下所有文件名的日期
            timestamps = list(map(lambda x: time.mktime(x.timetuple()), times))  # 目录下所有文件名的日期时间戳
            idx = idx = np.argmin(np.abs(np.array(timestamps) - time.mktime(obs_time.timetuple())))  # 离obs_time最近的一个idx
            nearesttime = times[idx]  # 离obs_time最近的一个日期
            filename = datetime.datetime.strftime(nearesttime, filename_format)
        else:
            filename = datetime.datetime.strftime(obs_time, filename_format)
    filetime = datetime.datetime.strptime(filename, filename_format)  # 文件名的日期
    return filename, filetime


def get_obs_filenames(directory, filename_format, obs_st_time=None, obs_ed_time=None):
    """[获取日期范围之内实况数据文件名以及日期]

    Args:
        directory ([str]): [cassandra中的目录，如：RADARMOSAIC/CREF/]
        filename_format ([str]): [cassandra中的文件名，必须带日期格式化的字符串，能用strftime正常格式化的字符串，如：ACHN_CREF_%Y%m%d_%H%M%S.BIN]
        obs_st_time ([dateime], optional): [description]. Defaults to None.
        obs_ed_time ([dateime], optional): [description]. Defaults to None.
    """
    fnames = nmc_micaps_io.get_file_list(directory)  # 目录下所有文件名， 此方法如果遇到文件量多的情况会有点慢，后续看是否能优化
    if len(fnames) == 0:
        raise Exception('Can not retrieve data from ' + directory)
    fnames.sort(reverse=True)  # 按照日期从大到小排序
    fnames = np.array(fnames)
    times = np.vectorize(lambda x: datetime.datetime.strptime(x, filename_format))(fnames)  # 目录下所有文件名的日期
    fnames = fnames[(times >= obs_st_time) & (times <= obs_ed_time)]  # 日期范围内的文件名
    ftimes = list(map(lambda x: datetime.datetime.strptime(x, filename_format), fnames))  # 日期范围内的时间
    return list(fnames), ftimes


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
            if byteArray == '' or byteArray == b'':
                print('There is no data ' + filename + ' in ' + directory)
                return None

            data_dic = json.loads(byteArray)

            records = pd.DataFrame(data_dic['data'])
            col1 = list(records.columns)
            col2 = []
            for k, v in data_dic.items():
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
