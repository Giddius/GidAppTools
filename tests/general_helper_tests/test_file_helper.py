import pytest
from pytest import param

from pathlib import Path
from gidapptools.general_helper.file_helper import get_last_line


def test_get_last_line_1(file_helper_file_1: Path):
    assert get_last_line(file_helper_file_1, decode=True) == ""


def test_get_last_line_2(file_helper_file_2: Path):
    assert get_last_line(file_helper_file_2, decode=True) == "this is the last line"


def test_get_last_line_3(file_helper_file_3: Path):
    assert get_last_line(file_helper_file_3, decode=True) == ""


def test_get_last_line_4(file_helper_file_4: Path):
    assert get_last_line(file_helper_file_4, decode=True) == "\t"
