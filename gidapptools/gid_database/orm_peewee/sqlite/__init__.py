import os
import sys


try:
    import apsw
    os.environ["_APSW_AVAILABLE"] = "1"
except ImportError:
    os.environ["_APSW_AVAILABLE"] = "0"
