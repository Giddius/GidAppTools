import pytest
from gidapptools.general_helper.general import defaultable_list_pop
from collections import namedtuple
import inspect
Param = namedtuple("Param", ["param", "name"], defaults=(None,))


defaultable_list_pop_params = [
    Param([[1, 2, 3, 4, 5], 0, None, 1], "not_default_1"),
    Param([[1, 2, 3, 4, 5], 6, None, None], "default_None_1"),
    Param([[1, 2, 3, 4, 5], 7, 42, 42], "default_42"),
    Param([[1, 2, 3, 4, 5], "not an int", 42, TypeError], "not_int_default_42")
]
actual_defaultable_list_pop_parameters = [item.param for item in defaultable_list_pop_params]
actual_defaultable_list_pop_parameter_names = [item.name for item in defaultable_list_pop_params]


@pytest.mark.parametrize("in_list, in_index, in_default, expected", actual_defaultable_list_pop_parameters, ids=actual_defaultable_list_pop_parameter_names)
def test_defaultable_list_pop(in_list, in_index, in_default, expected):
    if inspect.isclass(expected) and issubclass(expected, Exception):
        with pytest.raises(expected):
            defaultable_list_pop(in_list, in_index, default=in_default)
    else:
        assert defaultable_list_pop(in_list, in_index, default=in_default) == expected
