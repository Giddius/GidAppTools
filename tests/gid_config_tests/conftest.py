import pytest
from gidapptools.gid_config.interface import GidIniConfig
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil


THIS_FILE_DIR = Path(__file__).parent.absolute()

EXAMPLE_CONFIG_1_ORIGINAL_PATH = THIS_FILE_DIR.joinpath('example_config_1.ini')
EXAMPLE_SPEC_1_ORIGINAL_PATH = THIS_FILE_DIR.joinpath("example_spec_1.json")


EXAMPLE_CONFIG_2_ORIGINAL_PATH = THIS_FILE_DIR.joinpath('example_config_2.ini')
EXAMPLE_SPEC_2_ORIGINAL_PATH = THIS_FILE_DIR.joinpath("example_spec_2.json")

EXAMPLE_CONFIG_3_ORIGINAL_PATH = THIS_FILE_DIR.joinpath('example_config_3.ini')
EXAMPLE_SPEC_3_ORIGINAL_PATH = THIS_FILE_DIR.joinpath("example_spec_3.json")


@pytest.fixture(scope="function")
def example_config_1():
    with TemporaryDirectory() as temp_folder:
        new_path = shutil.copy(EXAMPLE_CONFIG_1_ORIGINAL_PATH, temp_folder)
        yield Path(new_path)


@pytest.fixture(scope="function")
def example_spec_1():
    with TemporaryDirectory() as temp_folder:
        new_path = shutil.copy(EXAMPLE_SPEC_1_ORIGINAL_PATH, temp_folder)
        yield Path(new_path)


@pytest.fixture(scope="function")
def example_config_2():
    with TemporaryDirectory() as temp_folder:
        new_path = shutil.copy(EXAMPLE_CONFIG_2_ORIGINAL_PATH, temp_folder)
        yield Path(new_path)


@pytest.fixture(scope="function")
def example_spec_2():
    with TemporaryDirectory() as temp_folder:
        new_path = shutil.copy(EXAMPLE_SPEC_2_ORIGINAL_PATH, temp_folder)
        yield Path(new_path)


@pytest.fixture(scope="function")
def example_spec_3():
    with TemporaryDirectory() as temp_folder:
        new_path = shutil.copy(EXAMPLE_SPEC_3_ORIGINAL_PATH, temp_folder)
        yield Path(new_path)


@pytest.fixture(scope="function")
def example_config_3():
    with TemporaryDirectory() as temp_folder:
        new_path = shutil.copy(EXAMPLE_CONFIG_3_ORIGINAL_PATH, temp_folder)
        yield Path(new_path)


@pytest.fixture(scope="function")
def gid_ini_config(example_config_1: Path, example_spec_1: Path):
    config = GidIniConfig(config_file=example_config_1, spec_file=example_spec_1)
    yield config


@pytest.fixture(scope="function")
def gid_ini_config_2(example_config_2: Path, example_spec_2: Path):
    config = GidIniConfig(config_file=example_config_2, spec_file=example_spec_2)
    yield config


@pytest.fixture(scope="function")
def gid_ini_config_3(example_config_3: Path, example_spec_3: Path):
    config = GidIniConfig(config_file=example_config_3, spec_file=example_spec_3)
    yield config
