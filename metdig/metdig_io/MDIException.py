# -*- coding: utf-8 -*-

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class CFGError(Error):
    """数据配置异常，包括Cassandra要素路径配置异常"""

    def __init__(self, message):
        self.message = message


class NMCMetIOError(Error):
    """调用nmc_met_io获取数据异常"""

    def __init__(self, message):
        self.message = message
