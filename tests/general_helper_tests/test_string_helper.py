from gidapptools.general_helper.string_helper import StringCaseConverter, StringCase, split_quotes_aware, clean_whitespace, make_attribute_name
import pytest
from functools import reduce
from typing import Iterable
from operator import add
from collections import namedtuple

Param = namedtuple("Param", ["param", "name"], defaults=(None,))

case_convert_1_input = 'THIS_IS_A_TEST'

case_convert_1_results = {StringCase.CAMEL: 'thisIsATest',
                          StringCase.SNAKE: "this_is_a_test",
                          StringCase.SCREAMING_SNAKE: "THIS_IS_A_TEST",
                          StringCase.PASCAL: 'ThisIsATest',
                          StringCase.KEBAP: 'this-is-a-test',
                          StringCase.SPLIT: 'this is a test',
                          StringCase.TITLE: 'This Is A Test',
                          StringCase.UPPER: "THIS IS A TEST"}

case_convert_1_parameters = [Param((case_convert_1_input, k, v), k.name) for k, v in case_convert_1_results.items()]

case_convert_2_input = 'this is a test'

case_convert_2_results = {StringCase.CAMEL: 'thisIsATest',
                          StringCase.SNAKE: "this_is_a_test",
                          StringCase.SCREAMING_SNAKE: "THIS_IS_A_TEST",
                          StringCase.PASCAL: 'ThisIsATest',
                          StringCase.KEBAP: 'this-is-a-test',
                          StringCase.SPLIT: 'this is a test',
                          StringCase.TITLE: 'This Is A Test',
                          StringCase.UPPER: "THIS IS A TEST"}

case_convert_2_parameters = [Param((case_convert_2_input, k, v), k.name + '_with_spaces') for k, v in case_convert_2_results.items()]

case_convert_parameters = case_convert_1_parameters + case_convert_2_parameters

actual_case_convert_parameters = [item.param for item in case_convert_parameters]
actual_case_convert_parameter_names = [item.name for item in case_convert_parameters]


@pytest.mark.parametrize("string_input,target_case,expected",
                         actual_case_convert_parameters, ids=actual_case_convert_parameter_names)
def test_convert_to(string_input: str, target_case: StringCase, expected: str):
    assert StringCaseConverter.convert_to(string_input, target_case) == expected


split_parameters = [
    Param(({","}, {'"', "'"}, True, """1, 2, 3, "4, 5, 6", 7, 8, '9, 10, 11'""", ["1", "2", "3", "4, 5, 6", "7", "8", "9, 10, 11"]), 'simple'),
    Param(({","}, {'"', "'"}, True, """1, 2, 3, "4, '5, 6'", 7, 8, '9, 10, 11'""", ["1", "2", "3", "4, '5, 6'", "7", "8", "9, 10, 11"]), 'nested_quote'),
    Param(({","}, {'"', "'"}, True, """ """, []), 'empty'),
    Param(({","}, {'"', "'"}, True, """there are not separators in here""", ["there are not separators in here"]), 'no_separator'),
    Param(({","}, {'"', "'"}, True, """there are not separators in here but a 'quoted part'""", ["there are not separators in here but a 'quoted part'"]), 'no_separator_but_quote'),
]
actual_split_parameters = [item.param for item in split_parameters]
actual_split_parameter_names = [item.name for item in split_parameters]


@pytest.mark.parametrize("split_chars, quote_chars, strip_parts, in_text, expected_result",
                         actual_split_parameters, ids=actual_split_parameter_names)
def test_split_quotes_aware(split_chars: Iterable[str], quote_chars: Iterable[str], strip_parts: bool, in_text: str, expected_result: list[str]):
    assert split_quotes_aware(in_text, split_chars, quote_chars, strip_parts) == expected_result


clean_whitespace_params_basic = [pytest.param("This       is a Test", "This is a Test", False),
                                 pytest.param("This       is\na Test", "This is\na Test", False),
                                 pytest.param("This       is\na Test", "This is a Test", True),
                                 pytest.param("This is a Test", "This is a Test", False),
                                 pytest.param("This is a Test", "This is a Test", True)]


@pytest.mark.parametrize("in_string, out_string, clean_newline", clean_whitespace_params_basic)
def test_clean_whitespace(in_string: str, out_string: str, clean_newline: bool):
    assert clean_whitespace(in_string, clean_newline) == out_string


make_attribute_name_params_basic = [pytest.param("attribute", "attribute"),
                                    pytest.param("1attribute", "attribute"),
                                    pytest.param("1_attribute", "_attribute"),
                                    pytest.param("Attribute", "attribute"),
                                    pytest.param("_1_attribute", "_1_attribute")]


@pytest.mark.parametrize("in_name, out_name", make_attribute_name_params_basic)
def test_make_attribute_name(in_name: str, out_name: str):
    assert make_attribute_name(in_name) == out_name
