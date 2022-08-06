# region [Imports]

import pytest
from pathlib import Path


try:
    from ..data import THIS_FILE_DIR as DATA_DIR
except ImportError:
    ...

# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]
