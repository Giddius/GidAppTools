import pytest
from gidapptools.general_helper.dict_helper import multiple_dict_get, replace_dict_keys
from collections import namedtuple

Param = namedtuple("Param", ["param", "name"], defaults=(None,))

example_dict_1 = {'alpha': 11, 'beta': 12, 'gamma': 13}

example_dict_2 = {'beta': 22, 'gamma': 23, 'delta': 24}


def test_multiple_dict_get():
    assert multiple_dict_get("beta", example_dict_1, example_dict_2, final_default=99) == 12
    assert multiple_dict_get("does_not_exist", example_dict_1, example_dict_2, final_default=99) == 99
    assert multiple_dict_get("delta", example_dict_1, example_dict_2, final_default=99) == 24


replace_dict_parameters = [
    Param(
        (example_dict_1,
         [("alpha", "first")],
         {"first": 11, 'beta': 12, 'gamma': 13}),
        "replace_one"
    ),
    Param(
        (example_dict_1,
         [("alpha", "first"), ("gamma", 'third')],
         {"first": 11, 'beta': 12, 'third': 13}),
        "replace_two"
    ),
    Param(
        (example_dict_1,
         [("alpha", "first"), ("gamma", 'third'), ('beta', "second")],
         {"first": 11, 'second': 12, 'third': 13}),
        "replace_all"
    ),
    Param(
        (example_dict_1,
         [("not_in_dict", "this")],
         example_dict_1),
        "replace_key_not_in_dict"
    ),
    Param(
        (example_dict_1,
         [("alpha", "first"), ("gamma", 'third'), ('beta', "second"), ("alpha", "erstes")],
         {"first": 11, 'second': 12, 'third': 13}),
        "duplicate_replace"
    ),
    Param(
        (example_dict_1,
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
