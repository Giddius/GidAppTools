import pytest
from gidapptools.general_helper.dict_helper import multiple_dict_get


example_dict_1 = {'alpha': 11, 'beta': 12, 'gamma': 13}

example_dict_2 = {'beta': 22, 'gamma': 23, 'delta': 24}


def test_multiple_dict_get():
    assert multiple_dict_get("beta", example_dict_1, example_dict_2, final_default=99) == 12
    assert multiple_dict_get("does_not_exist", example_dict_1, example_dict_2, final_default=99) == 99
    assert multiple_dict_get("delta", example_dict_1, example_dict_2, final_default=99) == 24
