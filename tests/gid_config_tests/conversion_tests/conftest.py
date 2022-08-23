

# region [Imports]

import pytest
from pathlib import Path
import shutil
from typing import Optional
from ..data import THIS_FILE_DIR as DATA_DIR, get_file_path
import json
from gidapptools.gid_config.conversion.converter_grammar import ConverterSpecData

from frozendict import frozendict
# endregion [Imports]


# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

# pylint: disable=redefined-outer-name


@pytest.fixture()
def basic_configspec_example_1(tmp_path) -> Path:
    temporary_dir = tmp_path
    orig_path = get_file_path("basic_configspec.json")
    new_path = temporary_dir.joinpath(orig_path.name)
    shutil.copyfile(orig_path, new_path)
    yield new_path
