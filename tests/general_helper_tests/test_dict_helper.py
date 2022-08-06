import pytest
from gidapptools.general_helper.dict_helper import multiple_dict_get, replace_dict_keys
from collections import namedtuple

Param = namedtuple("Param", ["param", "name"], defaults=(None,))


def get_example_dict(number: int):
    example_dict_1 = {'alpha': 11, 'beta': 12, 'gamma': 13}

    example_dict_2 = {'beta': 22, 'gamma': 23, 'delta': 24}
    if number == 1:
        return dict(example_dict_1)
    if number == 2:
        return dict(example_dict_2)


def test_multiple_dict_get():
    assert multiple_dict_get("beta", get_example_dict(1), get_example_dict(2), final_default=99) == 12
    assert multiple_dict_get("does_not_exist", get_example_dict(1), get_example_dict(2), final_default=99) == 99
    assert multiple_dict_get("delta", get_example_dict(1), get_example_dict(2), final_default=99) == 24


replace_dict_parameters = [
    Param(
        (get_example_dict(1),
         [("alpha", "first")],
         {"first": 11, 'beta': 12, 'gamma': 13}),
        "replace_one"
    ),
    Param(
        (get_example_dict(1),
         [("alpha", "first"), ("gamma", 'third')],
         {"first": 11, 'beta': 12, 'third': 13}),
        "replace_two"
    ),
    Param(
        (get_example_dict(1),
         [("alpha", "first"), ("gamma", 'third'), ('beta', "second")],
         {"first": 11, 'second': 12, 'third': 13}),
        "replace_all"
    ),
    Param(
        (get_example_dict(1),
         [("not_in_dict", "this")],
         get_example_dict(1)),
        "replace_key_not_in_dict"
    ),
    Param(
        (get_example_dict(1),
         [("alpha", "first"), ("gamma", 'third'), ('beta', "second"), ("alpha", "erstes")],
         {"first": 11, 'second': 12, 'third': 13}),
        "duplicate_replace"
    ),
    Param(
        (get_example_dict(1),
         [("alpha", "first"), ("gamma", 'third'), ('beta', "second"), ("first", "erstes")],
         {"erstes": 11, 'second': 12, 'third': 13}),
        "replace_replacement"
    ),
]
actual_replace_dict_parameters = [item.param for item in replace_dict_parameters]
actual_replace_dict_parameters_names = [item.name for item in replace_dict_parameters]


@pytest.mark.parametrize("in_dict, replacements, expected_result", actual_replace_dict_parameters, ids=actual_replace_dict_parameters_names)
def test_replace_dict_keys(in_dict, replacements, expected_result):
    assert replace_dict_keys(in_dict, *replacements) == expected_result
