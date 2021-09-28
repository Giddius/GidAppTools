from gidapptools.general_helper.dispatch_table import BaseDispatchTable, dispatch_mark
import pytest


def test_collecting(check_dispatch_table: BaseDispatchTable):
    check_dispatch_table._collect_dispatch_data()
    assert check_dispatch_table._table == {dispatch_mark.DEFAULT: check_dispatch_table._the_default,
                                           str: check_dispatch_table._on_string_type,
                                           "something": check_dispatch_table._on_something,
                                           1: check_dispatch_table._on_1,
                                           "callable_key_conversion": check_dispatch_table._on_callable_key_conversion}


get_test_parameters = [(int, 'default'),
                       (str, str),
                       ("something", "something"),
                       (1, 1),
                       ("callable_key_conversion", "callable_key_conversion")]


@pytest.mark.parametrize("key,result",
                         get_test_parameters)
def test_get(check_dispatch_table: BaseDispatchTable, key, result):
    argument = 'check'
    assert check_dispatch_table.get(key)(argument) == (result, argument)


mod_key_get_test_parameters = [(int, 'default'),
                               (str, str),
                               ("something", "something"),
                               (1, 1),
                               ("modified_callable_key_conversion", "callable_key_conversion")]


@pytest.mark.parametrize("key,result",
                         mod_key_get_test_parameters)
def test_mod_key_get(mod_key_check_dispatch_table: BaseDispatchTable, key, result):
    argument = 'check_mod'
    assert mod_key_check_dispatch_table.get(key)(argument) == (result, argument)
