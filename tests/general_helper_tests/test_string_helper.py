from gidapptools.general_helper.string_helper import StringCaseConverter, StringCase, split_quotes_aware, clean_whitespace, multi_line_dedent, make_attribute_name, fix_multiple_quotes, replace_by_dict, extract_by_map, shorten_string, deindent
import pytest
from pytest import param
from functools import reduce
from typing import Iterable, Union, Mapping, Literal, Optional
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


@pytest.mark.parametrize("string_input, target_case, expected", actual_case_convert_parameters, ids=actual_case_convert_parameter_names)
def test_convert_to(string_input: str, target_case: StringCase, expected: str):
    assert StringCaseConverter.convert_to(string_input, target_case) == expected


params_convert_to_advanced = [param("QtWARNING", StringCase.BLOCK_UPPER, "QTWARNING", id="qt_warning_test"),
                              param("They were dropping losing altitude in a canyon of rainbow foliage a lurid communal mural that completely covered the hull of the room where Case waited That was Wintermute manipulating the lock the way it had manipulated the drone micro and the corners hed cut in Night City",
                              StringCase.SNAKE,
                              "they_were_dropping_losing_altitude_in_a_canyon_of_rainbow_foliage_a_lurid_communal_mural_that_completely_covered_the_hull_of_the_room_where_case_waited_that_was_wintermute_manipulating_the_lock_the_way_it_had_manipulated_the_drone_micro_and_the_corners_hed_cut_in_night_city",
                                    id="long_to_snake")]


@pytest.mark.parametrize("string_input, target_case, expected", params_convert_to_advanced)
def test_convert_to_advanced(string_input: str, target_case: StringCase, expected: str):
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


fix_multiple_quotes_params_basic = [pytest.param('""text""', '"text"', id="2 x double_quotes")]


@pytest.mark.parametrize("in_text, expected", fix_multiple_quotes_params_basic)
def test_fix_multiple_quotes(in_text: str, expected: str):
    assert fix_multiple_quotes(in_text) == expected


replace_by_dict_params_basic = [pytest.param("a_string", {"_": " "}, "a string", id="single_underscore_replace"),
                                param("a_different_string", {"_": " "}, "a different string", id="multiple_underscore_replace"),
                                param("a string", {" ": "_"}, "a_string", id="reverse_single_underscore_replace"),
                                param("a different string", {" ": "_"}, "a_different_string", id="reverse_multiple_underscore_replace")]


@pytest.mark.parametrize("in_text, in_dict, expected", replace_by_dict_params_basic)
def test_replace_by_dict(in_text: str, in_dict: dict[str, str], expected: str):
    assert replace_by_dict(in_text, in_dict) == expected


extract_by_map_params_basic = [param("first_part/second_part/first_part", ["first_part"], ["first_part", "first_part"], id="simple_extract_literal")]

extract_by_map_params_advanced = [param("first_part/second_part/first_part", {"first_part": "found_a_first_part"}, ["found_a_first_part", "found_a_first_part"], id="advanced_extract_with_mapping_literal")]


@pytest.mark.parametrize("in_text, in_extract_data, expected", extract_by_map_params_basic + extract_by_map_params_advanced)
def test_extract_by_map(in_text: str, in_extract_data: Union[Iterable[str], Mapping[str, str]], expected: Iterable[str]):
    assert extract_by_map(in_text, extract_data=in_extract_data) == expected


default_shorten_side = "right"
default_placeholder = "..."
default_clean_before = True
default_ensure_space_around_placeholder = False
default_split_on = "\s|\n"

shorten_string_params_basic = [param("a simple test to check the shortening on spaces", 12, default_shorten_side, default_placeholder, default_clean_before, default_ensure_space_around_placeholder, default_split_on, "a simple...", None, id="1"),
                               param("a simple test to check the shortening on spaces", 10, default_shorten_side, default_placeholder, default_clean_before, default_ensure_space_around_placeholder, default_split_on, "a...", None, id="2"),
                               param("a simple test to check the shortening on spaces", 20, default_shorten_side, default_placeholder, default_clean_before, default_ensure_space_around_placeholder, default_split_on, "a simple test to...", None, id="3"),
                               param("a simple test to check the shortening on spaces", 20, "left", default_placeholder, default_clean_before, default_ensure_space_around_placeholder, default_split_on, "...on spaces", None, id="left_1")]

shorten_string_params_advanced = [param("a simple test to check the shortening on spaces", 20, "not_existing_side", default_placeholder, default_clean_before, default_ensure_space_around_placeholder, default_split_on, "a simple test to...", ValueError, id="error_wrong_shorten_side"),
                                  param("a simple test to check the shortening on spaces", 20000, default_shorten_side, default_placeholder, default_clean_before, default_ensure_space_around_placeholder, default_split_on, "a simple test to check the shortening on spaces", None, id="max_length_greater_than_text_length"),
                                  param("a simple test to check the shortening on spaces", 13, default_shorten_side, default_placeholder, default_clean_before, True, default_split_on, "a simple ...", None, id="ensure_space_around_placeholder_true")]


@pytest.mark.parametrize("in_text, max_length, shorten_side, placeholder, clean_before, ensure_space_around_placeholder, split_on, expected, error", shorten_string_params_basic + shorten_string_params_advanced)
def test_shorten_string(in_text: str,
                        max_length: int,
                        shorten_side: Literal["right", "left"],
                        placeholder: str,
                        clean_before: bool,
                        ensure_space_around_placeholder: bool,
                        split_on: str,
                        expected: str,
                        error: Optional[type[Exception]]):

    if error:
        with pytest.raises(error):
            shorten_string(in_text=in_text,
                           max_length=max_length,
                           shorten_side=shorten_side,
                           clean_before=clean_before,
                           split_on=split_on,
                           ensure_space_around_placeholder=ensure_space_around_placeholder,
                           placeholder=placeholder)
    else:
        new_string = shorten_string(in_text=in_text,
                                    max_length=max_length,
                                    shorten_side=shorten_side,
                                    clean_before=clean_before,
                                    split_on=split_on,
                                    ensure_space_around_placeholder=ensure_space_around_placeholder,
                                    placeholder=placeholder)

        assert len(new_string) <= max_length
        assert new_string == expected


first_deindent_test_text = """First Line
                            Second Line
                            Third Line"""

first_deindent_expected_text = """First Line\nSecond Line\nThird Line"""

deindent_params_basic = [param(first_deindent_test_text, False, first_deindent_test_text, id="1"),
                         param(first_deindent_test_text, True, first_deindent_expected_text, id="2"),
                         param("    this has indent but only one line", False, "this has indent but only one line", id="3"),
                         param("    this has indent but only one line", True, "    this has indent but only one line", id="4")]

deindent_params_advanced = [param("", False, "", id="adv_1"),
                            param("this has not indent and only one line", False, "this has not indent and only one line", id="adv_2")]


@pytest.mark.parametrize("in_text, ignore_first_line, expected", deindent_params_basic + deindent_params_advanced)
def test_deindent(in_text: str, ignore_first_line: bool, expected: str):
    converted = deindent(in_text=in_text, ignore_first_line=ignore_first_line)

    assert converted == expected


# TODO: make file to get strings and expected
multi_line_dedent_params_basic = [param("this has no indent", True, True, "this has no indent", id="single_line_no_indent")]

multi_line_dedent_params_advanced = []


@pytest.mark.parametrize("in_text, strip_pre_lines, strip_post_lines, expected", multi_line_dedent_params_basic + multi_line_dedent_params_advanced)
def test_multi_line_dedent(in_text: str, strip_pre_lines: bool, strip_post_lines: bool, expected: str):
    converted = multi_line_dedent(in_text=in_text, strip_pre_lines=strip_pre_lines, strip_post_lines=strip_post_lines)
    assert converted == expected
