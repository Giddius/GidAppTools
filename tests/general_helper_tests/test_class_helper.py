import pytest
from pytest import param
from gidapptools.general_helper.class_helper import make_repr
from typing import TYPE_CHECKING, Optional, Union, Mapping, Callable, Iterable, Any


class SimpleClass:
    def __init__(self, first_arg, second_arg) -> None:
        self.first_arg = first_arg
        self.second_arg = second_arg


class SimpleInheritedClass(SimpleClass):
    def __init__(self, first_arg, second_arg, new_arg) -> None:
        super().__init__(first_arg, second_arg)
        self.new_arg = new_arg


params_make_repr_basic = [param(str(), None, True, "", TypeError, id="string_instance"),
                          param(SimpleClass("something", 1), None, True, "SimpleClass(first_arg='something', second_arg=1)", None, id="simple_class_no_none"),
                          param(SimpleInheritedClass("something", 1, True), None, True, "SimpleInheritedClass(first_arg='something', second_arg=1, new_arg=True)", None, id="simple_inherited_class_no_none")]


@pytest.mark.parametrize("in_instance, attr_names, exclude_none, expected, error", params_make_repr_basic)
def test_make_repr(in_instance: object, attr_names: Union[Callable, Iterable[str]], exclude_none: bool, expected: str, error: Exception):
    if error:
        with pytest.raises(error):
            make_repr(instance=in_instance, attr_names=attr_names, exclude_none=exclude_none)
    else:
        assert make_repr(instance=in_instance, attr_names=attr_names, exclude_none=exclude_none) == expected
