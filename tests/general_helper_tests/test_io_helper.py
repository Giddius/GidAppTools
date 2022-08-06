import pytest
from pytest import param

from pathlib import Path
from gidapptools.general_helper.io_helper import get_last_line, escalating_find_file, amount_lines_in_file
from faked_pack_src import FAKE_PACKAGE_DIR

THIS_FILE_DIR = Path(__file__).parent.absolute()


def test_get_last_line_1(file_helper_file_1: Path):
    assert get_last_line(file_helper_file_1, decode=True) == ""


def test_get_last_line_2(file_helper_file_2: Path):
    assert get_last_line(file_helper_file_2, decode=True) == "this is the last line"


def test_get_last_line_3(file_helper_file_3: Path):
    assert get_last_line(file_helper_file_3, decode=True) == ""


def test_get_last_line_4(file_helper_file_4: Path):
    assert get_last_line(file_helper_file_4, decode=True) == "\t"


def test_get_last_line_not_a_file(file_helper_file_1: Path):
    with pytest.raises(FileNotFoundError):
        get_last_line(file_helper_file_1.parent)


def test_amount_lines_in_file_1(file_helper_file_1: Path):
    assert amount_lines_in_file(file_helper_file_1) == 8


def test_amount_lines_in_file_2(file_helper_file_2: Path):
    assert amount_lines_in_file(file_helper_file_2) == 5


def test_amount_lines_in_file_3(file_helper_file_3: Path):
    assert amount_lines_in_file(file_helper_file_3) == 8


def test_amount_lines_in_file_4(file_helper_file_4: Path):
    assert amount_lines_in_file(file_helper_file_4) == 8


def test_amount_lines_in_file_not_a_file(file_helper_file_4: Path):
    with pytest.raises(FileNotFoundError):
        amount_lines_in_file(file_helper_file_4.parent)


def test_escalating_find_file_not_a_directory():
    with pytest.raises(NotADirectoryError):
        escalating_find_file("not_important", THIS_FILE_DIR.joinpath("__init__.py"))


def test_escalating_find_file():
    result = escalating_find_file("pyproject.toml", THIS_FILE_DIR)

    assert result == THIS_FILE_DIR.parent.parent.joinpath("pyproject.toml")


def test_escalating_find_file_2():
    result = escalating_find_file("README.md", FAKE_PACKAGE_DIR)
    assert result == FAKE_PACKAGE_DIR.parent.joinpath("README.md")


def test_escalating_find_file_case_sensitive():
    with pytest.raises(FileNotFoundError):
        escalating_find_file("readme.md", FAKE_PACKAGE_DIR, case_sensitive=True)
    result = escalating_find_file("README.md", FAKE_PACKAGE_DIR)
    assert result == FAKE_PACKAGE_DIR.parent.joinpath("README.md")
