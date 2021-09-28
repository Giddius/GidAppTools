from gidapptools.general_helper.string_helper import StringCaseConverter, StringCase
import pytest
from functools import reduce
from operator import add

case_convert_1_input = 'THIS_IS_A_TEST'

case_convert_1_results = {StringCase.CAMEL: 'thisIsATest',
                          StringCase.SNAKE: "this_is_a_test",
                          StringCase.SCREAMING_SNAKE: "THIS_IS_A_TEST",
                          StringCase.PASCAL: 'ThisIsATest',
                          StringCase.KEBAP: 'this-is-a-test',
                          StringCase.SPLIT: 'this is a test',
                          StringCase.TITLE: 'This Is A Test',
                          StringCase.UPPER: "THIS IS A TEST"}

case_convert_1_parameters = [(case_convert_1_input, k, v) for k, v in case_convert_1_results.items()]

case_convert_2_input = 'this is a test'

case_convert_2_results = {StringCase.CAMEL: 'thisIsATest',
                          StringCase.SNAKE: "this_is_a_test",
                          StringCase.SCREAMING_SNAKE: "THIS_IS_A_TEST",
                          StringCase.PASCAL: 'ThisIsATest',
                          StringCase.KEBAP: 'this-is-a-test',
                          StringCase.SPLIT: 'this is a test',
                          StringCase.TITLE: 'This Is A Test',
                          StringCase.UPPER: "THIS IS A TEST"}

case_convert_2_parameters = [(case_convert_2_input, k, v) for k, v in case_convert_2_results.items()]

case_convert_parameters = reduce(add, [case_convert_1_parameters, case_convert_2_parameters])


@pytest.mark.parametrize("string_input,target_case,expected",
                         case_convert_parameters)
def test_convert_to(string_input: str, target_case: StringCase, expected: str):
    assert StringCaseConverter.convert_to(string_input, target_case) == expected
