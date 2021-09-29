import pytest
from gidapptools.gid_config.parser.ini_parser import BaseIniParser, Entry, Section
from pathlib import Path

THIS_FILE_DIR = Path(__file__).parent.absolute()

SIMPLE_INI_CONFIG_FILE = THIS_FILE_DIR.joinpath("simple_example_config.ini")


@pytest.fixture
def simple_example_config_data() -> list[Section]:
    parser = BaseIniParser()
    text = SIMPLE_INI_CONFIG_FILE.read_text(encoding='utf-8', errors='ignore')
    data = parser.parse(text)
    yield data
