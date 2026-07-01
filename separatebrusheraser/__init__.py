import os, sys

_here = os.path.dirname(__file__)
_qtpy_outer = os.path.join(_here, "qtpy")  # this should contain the inner qtpy package directory
if _qtpy_outer not in sys.path:
    sys.path.insert(0, _qtpy_outer)

from .separatebrusheraser import *
