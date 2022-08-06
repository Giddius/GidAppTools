# region [Imports]

import pytest
from pathlib import Path
import shutil

try:
    from .data import THIS_FILE_DIR as DATA_DIR, get_file_path
except ImportError:
    ...

# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


@pytest.fixture()
def basic_configspec_path(tmp_path) -> Path:
    temporary_dir = tmp_path
    orig_path = get_file_path("basic_configspec.json")
    new_path = temporary_dir.joinpath(orig_path.name)
    shutil.copyfile(orig_path, new_path)
    yield new_path


@pytest.fixture()
def basic_ini_file_not_existing(tmp_path) -> Path:
    temporary_dir = tmp_path
    ini_path = temporary_dir.joinpath("basic_config.ini")
    yield ini_path
