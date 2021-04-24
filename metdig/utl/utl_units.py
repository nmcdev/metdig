
from metpy.units import units
import numpy as np
import pint

def numpy_units_to_stda(np_input, np_input_units, stda_units):
    '''
    
    [numpy数据转换成目标单位，注意，目标单位不能带倍数]
    
    Arguments:
        np_input {[ndarray]} -- [输入numpy数据]
        np_input_units {[str]} -- [输入numpy数据对应的单位]
        stda_units {[str]} -- [stda目标单位, 必须为基本单位且不带倍数，]
    
    Returns:
        [ndarray, units] -- [转换后的数据，转换后的单位]
    
    Raises:
        Exception -- [description]
    '''
    if not isinstance(np_input_units, str):
        raise Exception('error: np_input_units must be str!')
    if not isinstance(stda_units, str):
        raise Exception('error: stda_units must be str!')

    if np_input_units == '' or stda_units == '' or np_input_units == 'undefined stda' or stda_units == 'undefined stda' :
        return np_input, np_input_units # 无法转换，则按原数据返回，同时返回的单位为空

    if np.array(units(stda_units)) != 1:
        raise Exception('error: stda_units={} 单位不能带倍数, '.format(stda_units))

    # 单位转换
    data = (np_input * units(np_input_units)).to(stda_units)
    data = np.array(data)
    return data, stda_units


# 弃用 以下单位转换函数错误，无法正常使用
# def numpy_units_convert(np_input, np_input_units, stda_units):
#     '''
    
#     [numpy数据转换成目标单位，注意，目标单位可以带倍数]
    
#     Arguments:
#         np_input {[ndarray]} -- [输入numpy数据]
#         np_input_units {[str]} -- [输入numpy数据对应的单位]
#         stda_units {[str]} -- [stda目标单位, 必须为基本单位可以带倍数，]
    
#     Returns:
#         [ndarray, units] -- [转换后的数据，转换后的单位]
    
#     Raises:
#         Exception -- [description]
#     '''
#     if not isinstance(np_input_units, str):
#         raise Exception('error: np_input_units must be str!')
#     if not isinstance(stda_units, str):
#         raise Exception('error: stda_units must be str!')
    
#     if np_input_units == stda_units:
#         return np_input, np_input_units # 无需转换

#     if np_input_units == '' or stda_units == '' or np_input_units == 'undefined stda' or stda_units == 'undefined stda' :
#         return np_input, np_input_units # 无法转换，则按原数据返回，同时返回的单位为空

#     # 参考metpy初始化
#     mu = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
#     # For pint 0.6, this is the best way to define a dimensionless unit. See pint #185
#     mu.define(pint.unit.UnitDefinition('percent', '%', (),
#                 pint.converters.ScaleConverter(0.01)))
#     # Define commonly encountered units not defined by pint
#     mu.define('degrees_north = degree = degrees_N = degreesN = degree_north = degree_N '
#                 '= degreeN')
#     mu.define('degrees_east = degree = degrees_E = degreesE = degree_east = degree_E = degreeE')
#     try:
#         mu._units['meter']._aliases = ('metre', 'gpm')
#         mu._units['gpm'] = mu._units['meter']
#     except AttributeError:
#         pass

#     # 单位转换
#     mu.define('undef1=' + np_input_units)
#     mu.define('undef2=' + stda_units)
#     data = (np_input * mu('undef1')).to('undef2')
#     data = np.array(data)

#     # 删除
#     del mu

#     return data, stda_units