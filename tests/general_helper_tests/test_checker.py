# region [Imports]

import pytest
from pytest import param
from pytest_lazyfixture import lazy_fixture

from pathlib import Path

from gidapptools.general_helper.checker import is_hashable
import pp
# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class NoContentClass:
    ...


def no_content_func():
    ...


is_hashable_params = [param("text", True, id="string"),
                      param(13, True, id="integer"),
                      param(45.5, True, id="float"),
                      param(list(), False, id="list"),
                      param(tuple(), True, id="tuple"),
                      param(set(), False, id="set"),
                      param(dict(), False, id="dict"),
                      param(NoContentClass, True, id="type/class"),
                      param(no_content_func, True, id="function"),
                      param(None, True, id="None"),
                      param((list(), list()), False, id="tuple of lists"),
                      param((tuple(), tuple()), True, id="tuple of tuples"),
                      param(Path.cwd().resolve(), True, id="path")]


@pytest.mark.parametrize(["obj", "target_value"], is_hashable_params)
def test_is_hashable(obj: object, target_value: bool):
    assert is_hashable(obj) is target_value
