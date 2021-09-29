import pytest
from pathlib import Path
from gidapptools.general_helper.mixins.file_mixin import FileMixin


THIS_FILE_DIR = Path(__file__).parent.absolute()


@pytest.fixture
def check_file_path():
    path = THIS_FILE_DIR.joinpath('check_file.ini')
    path.touch()
    yield path
    path.unlink(missing_ok=True)
