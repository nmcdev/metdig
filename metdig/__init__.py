__author__ = "The R & D Center for Weather Forecasting Technology in NMC, CMA"
__version__ = '1.0.7.1'

from . import cal
from . import graphics
from . import hub
from . import io
from . import onestep
from . import products
from . import utl
from . import package_tools

import logging
_log = logging.getLogger(__name__)


def _ensure_handler():
    """
    The first time this function is called, attach a `StreamHandler` using the
    same format as `logging.basicConfig` to the Matplotlib root logger.

    Return this handler every time this function is called.
    """
    # BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"
    BASIC_FORMAT = "%(levelname)s:%(name)s:%(lineno)d:%(message)s"

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(BASIC_FORMAT))
    _log.addHandler(handler)
    return handler


def set_loglevel(level):
    """
    Sets the Matplotlib's root logger and root logger handler level, creating
    the handler if it does not exist yet.

    Typically, one should call ``set_loglevel("info")`` or
    ``set_loglevel("debug")`` to get additional debugging information.

    Parameters
    ----------
    level : {"notset", "debug", "info", "warning", "error", "critical"}
        The log level of the handler.

    Notes
    -----
    The first time this function is called, an additional handler is attached
    to Matplotlib's root handler; this handler is reused every time and this
    function simply manipulates the logger and handler's level.
    """
    _log.setLevel(level.upper())
    _ensure_handler().setLevel(level.upper())
