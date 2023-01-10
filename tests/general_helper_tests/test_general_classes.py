# region [Imports]

import pytest
from pytest import param
from pytest_lazyfixture import lazy_fixture

from pathlib import Path
from gidapptools.general_helper.general_classes import DecorateAbleList

# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

# region [test_1]


def test_decorateable_list_with_classes():
    the_list = DecorateAbleList()

    @the_list
    class FirstAdded:
        ...

    @the_list
    class SecondAdded:
        ...

    @the_list
    class ThirdAdded:
        ...

    assert the_list[0] == FirstAdded
    assert the_list[1] == SecondAdded
    assert the_list[2] == ThirdAdded

    assert list(the_list) == [FirstAdded, SecondAdded, ThirdAdded]


def test_decorateable_list_with_functions():

    the_list = DecorateAbleList()

    @the_list
    def first_func():
        ...

    @the_list
    def second_func(first_arg: str) -> str:
        return first_arg.upper()

    @the_list
    def third_func(first_arg, second_arg: str) -> int:
        ...

    assert the_list[0] == first_func
    assert the_list[0].__name__ == "first_func"
    assert the_list[1] == second_func
    assert the_list[1].__name__ == "second_func"
    assert the_list[2] == third_func
    assert the_list[2].__name__ == "third_func"

    assert list(the_list) == [first_func, second_func, third_func]
    assert the_list == [first_func, second_func, third_func]

    assert the_list[1]("abc") == "ABC"
    assert the_list[1] == second_func
# endregion [test_1]
