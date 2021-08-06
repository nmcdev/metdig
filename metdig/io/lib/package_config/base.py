# _*_ coding: utf-8 _*_

import os
import pandas as pd

import numpy as np
import threading

from metpy.units import units


def check_units(var_units):
    try:
        units(var_units)
    except Exception as e:
        raise e


class SingletonMetaClass(type):
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with cls._lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
        return cls._instance