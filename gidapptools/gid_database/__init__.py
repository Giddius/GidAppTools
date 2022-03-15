import os
import sys

try:
    from ._compiled_apsw import apsw
    os.environ["_APSW_AVAILABLE"] = "1"
    sys.modules["apsw"] = apsw
except ImportError:
    os.environ["_APSW_AVAILABLE"] = "0"
