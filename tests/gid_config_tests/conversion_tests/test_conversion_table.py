# region [Imports]

import pytest
from pytest import param
from pytest_lazyfixture import lazy_fixture

from pathlib import Path
from gidapptools.gid_config.conversion.conversion_table import ConversionTable, ConfigValueConverter, ConverterSpecData
from gidapptools.errors import UnconvertableTypusError
from gidapptools.gid_config.conversion.base_converters import (StringConfigValueConverter, IntegerConfigValueConverter, FloatConfigValueConverter, PathConfigValueConverter,
                                                               ListConfigValueConverter, DateTimeConfigValueConverter, TimedeltaConfigValueConverter, BooleanConfigValueConverter)
# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


# region [test_1]


# endregion [test_1]
