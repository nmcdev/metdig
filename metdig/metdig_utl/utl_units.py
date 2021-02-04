
from metpy.units import units
import numpy as np

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
