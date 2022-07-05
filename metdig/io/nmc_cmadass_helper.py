import os
import warnings
import json
import pickle
import hashlib
import uuid
from datetime import datetime, timedelta
import urllib3
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm
import nmc_met_io.config as CONFIG
from nmc_met_io.retrieve_cmadaas import get_rest_result, _load_contents

def cmadaas_ens_model_grid(data_code, init_time, valid_time, fcst_ele, fcst_level, level_type, fcst_member, limit=None,
                       varname='data', units=None, scale_off=None, cache=True, cache_clear=True,
                       levattrs={'long_name':'height_above_ground', 'units':'m', '_CoordinateAxisType':'Height'}):
    """
    Retrieve model grid data from CMADaaS service.
    refer to: http://10.20.76.55/cimissapiweb/apidataclassdefine_list.action

    :param data_code: MUSIC data code, 
                      "NAFP_FOR_FTM_LOW_C3E_EHE": 欧洲中心大气模式集合预报产品(高空)
                      "NAFP_C3E_FOR_FTM_LOW_ASI": 欧洲中心大气模式集合预报产品(地面)
                      ......
    :param init_time: model run time, like "2016081712", or datetime object.
    :param valid_time: forecast hour, like 0 or 6
    :param fcst_ele: forecast element, like 2m temperature "TEM"
    :param fcst_level: vertical level, like 0
    :param level_type: forecast level type, 表示Grib数据中的层次类型, 可在云平台上查询.
    :param fcst_level: forecast member, like 0-50
    :param limit: [min_lat, min_lon, max_lat, max_lon]
    :param varname: set variable name, default is 'data'
    :param units: forecast element's units, defaults to retrieved units.
    :param scale_off: [scale, offset], return values = values*scale + offset.
    :param cache: cache retrieved data to local directory, default is True.
    :param levattrs: level attributes, like:
                     {'long_name':'height_above_ground', 'units':'m', '_CoordinateAxisType':'Height'}, default
                     {'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'Pressure'}
                     {'long_name':'geopotential_height', 'units':'gpm', '_CoordinateAxisType':'GeoZ'}
                     refer to https://www.unidata.ucar.edu/software/netcdf-java/current/reference/CoordinateAttributes.html
    :return: xarray dataset.

    Examples:
    >>> data = cmadaas_model_grid("NAFP_FOR_FTM_HIGH_EC_ANEA", "2021010512", 24, 'TEM', 850, 100, units="C", scale_off=[1.0, -273.15], limit=[10.,100,30,120.],
                                  levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'Pressure'}, cache=True)
    """

    # check initial time
    if isinstance(init_time, datetime):
        init_time_str = init_time.strftime("%Y%m%d%H")
    else:
        init_time_str = init_time

    # retrieve data from cached file
    if cache:
        directory = os.path.join(data_code, fcst_ele, str(fcst_level))
        filename = init_time_str + '_' +str(fcst_member) + '.' + str(valid_time).zfill(3)
        if limit is not None:
            filename = init_time_str + '_' + str(fcst_member) + '_' +str(limit) +'.' + str(valid_time).zfill(3)
        cache_file = CONFIG.get_cache_file(directory, filename, name="CMADaaS", cache_clear=cache_clear)
        if cache_file.is_file():
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                return data
    # set retrieve parameters
    if limit is None:
        params = {'dataCode': data_code,
                  'time': init_time_str + '0000',
                  'fcstLevel': '{:d}'.format(fcst_level),
                  'levelType': level_type if type(level_type) == str else '{:d}'.format(level_type),
                  'validTime': '{:d}'.format(valid_time),
                  'fcstEle': fcst_ele,
                  'fcstMember': fcst_member if type(fcst_member) == str else '{:d}'.format(fcst_member)}
        interface_id = 'getNafpEleGridByTimeAndLevelAndValidtimeAndFcstMember'
    else:
        params = {'dataCode': data_code,
                  'time': init_time_str + '0000',
                  'minLat': '{:.10f}'.format(limit[0]),
                  "minLon": '{:.10f}'.format(limit[1]),
                  "maxLat": '{:.10f}'.format(limit[2]),
                  "maxLon": '{:.10f}'.format(limit[3]),
                  'fcstLevel': '{:d}'.format(fcst_level),
                  'levelType': level_type if type(level_type) == str else '{:d}'.format(level_type),
                  'validTime': '{:d}'.format(valid_time),
                  'fcstEle': fcst_ele,
                  'fcstMember': fcst_member if type(fcst_member) == str else '{:d}'.format(fcst_member)}
        interface_id = 'getNafpEleGridInRectByTimeAndLevelAndValidtimeAndFcstMember'

    # retrieve data contents
    contents = get_rest_result(interface_id, params)
    contents = _load_contents(contents)

    if contents is None:
        return None

    # get time information
    init_time = datetime.strptime(init_time_str, '%Y%m%d%H')
    fhour = np.array([valid_time], dtype=np.float)
    time = init_time + timedelta(hours=fhour[0])
    init_time = np.array([init_time], dtype='datetime64[ms]')
    time = np.array([time], dtype='datetime64[ms]')

    # extract coordinates and data
    start_lat = float(contents['startLat'])
    start_lon = float(contents['startLon'])
    nlon = int(contents['lonCount'])
    nlat = int(contents['latCount'])
    dlon = float(contents['lonStep'])
    dlat = float(contents['latStep'])
    lon = start_lon + np.arange(nlon)*dlon
    lat = start_lat + np.arange(nlat)*dlat
    name = contents['fieldNames']
    if units is None:
        units = contents['fieldUnits']

    # define coordinates and variables
    time_coord = ('time', time)
    lon_coord = ('lon', lon, {
        'long_name':'longitude', 'units':'degrees_east', '_CoordinateAxisType':'Lon'})
    lat_coord = ('lat', lat, {
        'long_name':'latitude', 'units':'degrees_north', '_CoordinateAxisType':'Lat'})
    if fcst_level != 0:
        level_coord = ('level', np.array([fcst_level]), levattrs)
    mem_coord = ('number', [fcst_member])
    varattrs = {'short_name': fcst_ele, 'long_name': name, 'units': units}

    # construct xarray
    data = np.array(contents['DS'], dtype=np.float32)
    if scale_off is not None:
        data = data * scale_off[0] + scale_off[1]
    if fcst_level == 0:
        data = data[np.newaxis, np.newaxis, ...]
        data = xr.Dataset({
            varname:(['number', 'time', 'lat', 'lon'], data, varattrs)},
            coords={'number': mem_coord, 'time':time_coord, 'lat':lat_coord, 'lon':lon_coord})
    else:
        data = data[np.newaxis, np.newaxis, np.newaxis, ...]
        data = xr.Dataset({
            varname:(['number', 'time', 'level', 'lat', 'lon'], data, varattrs)},
            coords={'number': mem_coord, 'time':time_coord, 'level':level_coord, 'lat':lat_coord, 'lon':lon_coord})

    # add time coordinates
    data.coords['forecast_reference_time'] = init_time[0]
    data.coords['forecast_period'] = ('time', fhour, {
        'long_name':'forecast_period', 'units':'hour'})

    # add attributes
    data.attrs['Conventions'] = "CF-1.6"
    data.attrs['Origin'] = 'CIMISS Server by MUSIC API'

    # cache data
    if cache:
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    return data