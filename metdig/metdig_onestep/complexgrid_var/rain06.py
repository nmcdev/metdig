# -*- coding: utf-8 -*


import numpy as np

from metdig.metdig_io import get_model_grid

import metdig.metdig_utl as mdgstda


def _by_self(data_source=None, init_time=None, fhour=None, data_name=None, extent=(50, 150, 0, 65)):
    rain06 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                            var_name='rain06', extent=extent, x_percent=0, y_percent=0, throwexp=False)
    return rain06


def _by_tpe(data_source=None, init_time=None, fhour=None, data_name=None, level=500, extent=(50, 150, 0, 65)):
    tpe1 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name,
                          var_name='tpe', extent=extent, x_percent=0, y_percent=0, throwexp=False)
    tpe2 = get_model_grid(data_source=data_source, init_time=init_time, fhour=fhour - 6, data_name=data_name,
                          var_name='tpe', extent=extent, x_percent=0, y_percent=0, throwexp=False)

    if tpe1 is None or tpe2 is None:
        return None

    rain06 = tpe1.copy(deep=True)
    rain06.values = tpe1.values - tpe2.values

    attrs = mdgstda.get_stda_attrs(var_name='rain06')
    attrs = {k: v for k, v in attrs.items() if v}  # 去除空项
    rain06.attrs.update(attrs)

    return rain06


def read_rain06(data_source=None, init_time=None, fhour=None, data_name=None, extent=(50, 150, 0, 65)):
    rain06 = _by_self(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=extent)
    if rain06 is not None:
        return rain06

    print('cal _by_tpe')
    rain06 = _by_tpe(data_source=data_source, init_time=init_time, fhour=fhour, data_name=data_name, extent=extent)
    if rain06 is not None:
        return rain06

    raise Exception('Can not get any data!')
