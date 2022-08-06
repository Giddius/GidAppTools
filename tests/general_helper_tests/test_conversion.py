import pytest
from pytest import param
from typing import Union, Literal, Mapping, Any, Optional
from gidapptools.general_helper.conversion import seconds2human, human2timedelta, ns_to_s, str_to_bool, human2bytes, bytes2human, number_to_pretty
from collections import namedtuple
import random
from datetime import timedelta, datetime
from gidapptools.errors import FlagConflictError
Param = namedtuple("Param", ["param", "name"], defaults=(None,))


# TODO: rewrite to use pytests param class
seconds2human_no_year_as_name_params = [
    Param([0.0000000001, "0 nanoseconds"], "less_than_a_nanosecond"),
    Param([0.000000001, "1 nanosecond"], "single_nanosecond"),
    Param([0.001, "1 millisecond"], "single_millisecond"),
    Param([1, "1 second"], "single_second"),
    Param([60, "1 minute"], "single_minute"),
    Param([3600, "1 hour"], "single_hour"),
    Param([3600 * 24, "1 day"], "single_day"),
    Param([3600 * 24 * 7, "1 week"], "single_week"),
    Param([0, "0 nanoseconds"], "no_time"),
    Param([123456, "1 day 10 hours 17 minutes and 36 seconds"], "random_value_1"),
    Param([654321, "1 week 13 hours 45 minutes and 21 seconds"], "random_value_2"),
    Param([8848601, '14 weeks 4 days 9 hours 56 minutes and 41 seconds'], "random_value_3"),
    Param([54223915, '89 weeks 4 days 14 hours 11 minutes and 55 seconds'], "random_value_4"),
    Param([91769010, '151 weeks 5 days 3 hours 23 minutes and 30 seconds'], "random_value_5"),
    Param([13068242, '21 weeks 4 days 6 hours 4 minutes and 2 seconds'], "random_value_6"),
    Param([7828312, '12 weeks 6 days 14 hours 31 minutes and 52 seconds'], "random_value_7"),
    Param([timedelta(seconds=45183587), '74 weeks 4 days 22 hours 59 minutes and 47 seconds'], 'timedela_value_1'),
    Param([timedelta(seconds=13085958), '21 weeks 4 days 10 hours 59 minutes and 18 seconds'], 'timedela_value_2'),
    Param([timedelta(seconds=9831794), '16 weeks 1 day 19 hours 3 minutes and 14 seconds'], 'timedela_value_3'),
    Param([timedelta(seconds=2739818), '4 weeks 3 days 17 hours 3 minutes and 38 seconds'], 'timedela_value_4'),
    Param([timedelta(seconds=64584636), '106 weeks 5 days 12 hours 10 minutes and 36 seconds'], 'timedela_value_5'),
    Param([-12, '-12 seconds'], 'negative_seconds_1'),
]


actual_seconds2human_no_year_as_name_values = [item.param for item in seconds2human_no_year_as_name_params]
actual_seconds2human_no_year_as_name_names = [item.name for item in seconds2human_no_year_as_name_params]


@pytest.mark.parametrize("in_seconds, expected", actual_seconds2human_no_year_as_name_values, ids=actual_seconds2human_no_year_as_name_names)
def test_seconds2human_no_year_as_name(in_seconds, expected):
    assert seconds2human(in_seconds, as_symbols=False, with_year=False) == expected


seconds2human_params_basic = [param(60, "minute", False, "1 minute", id="one_minute_min_unit_minute"),
                              param(65, "minute", False, "1 minute", id="one_minute_5_sec_min_unit_minute")]

seconds2human_params_advanced = [param(60, "hour", False, "0 hours", id="one_minute_min_unit_hour"),
                                 param(270, None, True, ["4 minutes", "30 seconds"], id="as_list_1")]


@pytest.mark.parametrize("in_seconds, min_unit, as_list_result, expected", seconds2human_params_basic + seconds2human_params_advanced)
def test_seconds2human_with_param(in_seconds: Union[int, timedelta], min_unit: Optional[str], as_list_result: bool, expected: str):
    if as_list_result is True:
        converted = seconds2human(in_seconds, as_symbols=False, with_year=False, min_unit=min_unit, as_list_result=as_list_result)
        assert converted == expected
    else:
        assert seconds2human(in_seconds, as_symbols=False, with_year=False, min_unit=min_unit, as_list_result=as_list_result) == expected


def test_seconds2human_error():
    with pytest.raises(FlagConflictError, match="No more than one of"):
        seconds2human(10, as_list_result=True, as_dict_result=True)


def year_to_seconds(in_year_amount: int) -> int:
    return in_year_amount * (60 * 60 * 24 * 7 * 52) + (60 * 60 * 24)


def nanoseconds_to_seconds(in_nanoseconds: int) -> int:
    return in_nanoseconds * (1 / 1_000_000_000)


test_human2timedelta_params = [pytest.param("", None, timedelta(), id="empty string"),
                               pytest.param("1 nanosecond", None, timedelta(seconds=nanoseconds_to_seconds(1)), id="nanosecond positive"),
                               pytest.param("1 microsecond", None, timedelta(microseconds=1), id="microsecond positive"),
                               pytest.param("1 millisecond", None, timedelta(milliseconds=1), id="millisecond positive"),
                               pytest.param("1 second", None, timedelta(seconds=1), id='second positive'),
                               pytest.param("1 minute", None, timedelta(minutes=1), id="minute positive"),
                               pytest.param("1 hour", None, timedelta(hours=1), id="hour positive"),
                               pytest.param("1 day", None, timedelta(days=1), id="day positive"),
                               pytest.param("1 week", None, timedelta(weeks=1), id="week positive"),
                               pytest.param("1 year", None, timedelta(seconds=year_to_seconds(1)), id="year positive"),
                               pytest.param("-1 nanosecond", None, -timedelta(seconds=nanoseconds_to_seconds(1)), id="nanosecond negative"),
                               pytest.param("-1 microsecond", None, -timedelta(microseconds=1), id="microsecond negative"),
                               pytest.param("-1 millisecond", None, -timedelta(milliseconds=1), id="millisecond negative"),
                               pytest.param("-1 second", None, -timedelta(seconds=1), id='second negative'),
                               pytest.param("-1 minute", None, -timedelta(minutes=1), id="minute negative"),
                               pytest.param("-1 hour", None, -timedelta(hours=1), id="hour negative"),
                               pytest.param("-1 day", None, -timedelta(days=1), id="day negative"),
                               pytest.param("-1 week", None, -timedelta(weeks=1), id="week negative"),
                               pytest.param("-1 year", None, -timedelta(seconds=year_to_seconds(1)), id="year negative"),
                               pytest.param("22 hours 7 seconds 4 microseconds", None, timedelta(hours=22, seconds=7, microseconds=4), id="combined 1 positive"),
                               pytest.param("since 40 weeks 7 hours 1 second", None, -timedelta(weeks=40, hours=7, seconds=1), id="combined 2 word-negative")
                               ]

test_human2timedelta_params_advanced = [pytest.param("in 1 millisecond ago", ValueError, -timedelta(milliseconds=1), id="error_on_two_signs"), ]


@ pytest.mark.parametrize("in_text,error, expected", test_human2timedelta_params + test_human2timedelta_params_advanced)
def test_human2timedelta(in_text, error: Optional[type[Exception]], expected):
    if error:
        with pytest.raises(error):
            human2timedelta(in_text)
    else:
        assert human2timedelta(in_text) == expected


ns_to_s_param_basic = [param(10, 0, 0, id="less_than_one_second_no_decimal"),
                       param(1_000_000_000, None, 1, id="exactly one second"),
                       param(1_500_000_000, None, 1.5, id="exactly_one_and_a_half_seconds")]


@ pytest.mark.parametrize("in_nano_seconds, in_decimal_places, expected", ns_to_s_param_basic)
def test_ns_to_s(in_nano_seconds: int, in_decimal_places: Optional[int], expected: Union[int, float]):
    converted = ns_to_s(nano_seconds=in_nano_seconds, decimal_places=in_decimal_places)

    assert converted == expected


str_to_bool_param_basic = [param("yes", True, None, True, id="simple_yes_strict"),
                           param("yes", False, None, True, id="simple_yes_not_strict"),
                           param("no", False, None, False, id="simple_no_not_strict"),
                           param("no", True, None, False, id="simple_no_strict"),
                           param("YeS", True, None, True, id="weird_case_yes_strict"),
                           param("nO", True, None, False, id="weird_case_no_strict"),
                           param("tRuE", True, None, True, id="weird_case_true_strict"),
                           param("fALsE", True, None, False, id="weird_case_false_strict"),
                           param("              yes            ", True, None, True, id="excess_ws_yes_strict"),
                           param("              yes\n            ", True, None, True, id="excess_ws_nl_yes_strict")]

str_to_bool_param_advanced = [param(True, True, None, True, id="already_bool"),
                              param("non_bool_string", True, TypeError, None, id="not_a_bool_string_strict"),
                              param("non_bool_string", False, None, False, id="not_a_bool_string_not_strict")]


@ pytest.mark.parametrize("in_text, strict, error, expected", str_to_bool_param_basic + str_to_bool_param_advanced)
def test_str_to_bool(in_text: Union[str, bool], strict: bool, error: Optional[type[Exception]], expected: bool):
    if error:
        with pytest.raises(error, match=r"Unable to convert string \'.*\' to a Boolean value."):
            str_to_bool(in_string=in_text, strict=strict)
    else:

        converted = str_to_bool(in_string=in_text, strict=strict)

        assert converted is expected


human2bytes_param_basic = [param("1 b", True, None, 1, id="exactly_one_byte")]

human2bytes_param_advanced = [param("0", False, None, "", id="zero_bytes_not_strict"),
                              param("0", True, ValueError, None, id="zero_bytes_strict"),
                              param("this is not a convertable string", True, ValueError, None, id="non_convertable_string_strict"),
                              param("this is not a convertable string", False, ValueError, None, id="non_convertable_string_not_strict")]


@ pytest.mark.parametrize("in_text, strict, error, expected", human2bytes_param_basic + human2bytes_param_advanced)
def test_human2bytes(in_text: str, strict: bool, error: Optional[type[Exception]], expected: int):
    if error:
        with pytest.raises(error, match="Unable to parse input string"):
            human2bytes(in_text=in_text, strict=strict)

    else:
        converted = human2bytes(in_text=in_text, strict=strict)

        assert converted == expected


bytes2human_param_basic = [param(1, None, "1 b", id="exatly_one_byte"),
                           param(1024, None, "1.0 Kb", id="exactly_one_kilo_byte"),
                           param(52_428_800, None, "50.0 Mb", id="50_mega_bytes")]

bytes2human_param_advanced = [param(12.5, TypeError, "", id="float TypeError")]


@ pytest.mark.parametrize("in_bytes, error, expected", bytes2human_param_basic + bytes2human_param_advanced)
def test_bytes2human(in_bytes: int, error: Optional[type[Exception]], expected: str):
    if error:
        with pytest.raises(error):
            bytes2human(in_bytes)
    else:
        converted = bytes2human(in_bytes)
        assert converted == expected


def test_number_to_pretty():
    assert number_to_pretty(10_000) == "10,000"

    assert number_to_pretty(1) == "1"

    assert number_to_pretty(10) == "10"

    assert number_to_pretty(100) == "100"

    assert number_to_pretty(0.1) == "0.1"

    assert number_to_pretty(100_000_000) == "100,000,000"
