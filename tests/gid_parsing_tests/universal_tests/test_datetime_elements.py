import pytest
from contextlib import contextmanager
from gidapptools.gid_parsing.universal.datetime_elements import datetime_format_mapping, get_grammar_from_dt_format
import pyparsing as pp
from datetime import datetime, timezone


@contextmanager
def does_not_raise():
    yield


datetime_format_mapping_params_basic = [pytest.param("%Y", "2001", 2001, None, id="%Y Year"),
                                        pytest.param("%m", "01", 1, None, id="%m Month"),
                                        pytest.param("%d", "15", 15, None, id="%d Day"),
                                        pytest.param("%H", "21", 21, None, id="%H Hour"),
                                        pytest.param("%M", "23", 23, None, id="%M Minute"),
                                        pytest.param("%S", "59", 59, None, id="%S Second"),
                                        pytest.param("%f", "074040", 74040, None, id="%f Microsecond"),
                                        pytest.param("%Z", "UTC", "UTC", None, id="%Z Timezone")]

datetime_format_mapping_params_advanced = [pytest.param("%Z", "CET", "CET", None, id="%Z CET Timezone Advanced"),
                                           pytest.param("%Z", "UTC+03:00", "UTC+03:00", None, id="%Z UTC+03:00 Timezone Advanced"),
                                           pytest.param("%Z", "UTC-03:00", "UTC-03:00", None, id="%Z UTC-03:00 Timezone Advanced"),
                                           pytest.param("%m", "1", 1, None, id="%m Month Advanced"), ]


@pytest.mark.parametrize("format_char, in_data, expected, raises", datetime_format_mapping_params_basic + datetime_format_mapping_params_advanced)
def test_datetime_format_mapping(format_char: str, in_data: str, expected: str, raises):
    if raises is None:
        raises = does_not_raise()
    with raises:
        element: pp.ParserElement = datetime_format_mapping[format_char]
    result = element.parse_string(in_data, parse_all=True)

    assert result[0] == expected


get_grammar_from_dt_format_params_basic = [pytest.param("%Y-%m-%d %H:%M:%S %Z", "2021-10-30 18:17:54 UTC", datetime(2021, 10, 30, 18, 17, 54, tzinfo=timezone.utc), None),
                                           pytest.param("%Y/%m/%d %H:%M:%S %Z", "2021/10/30 18:17:54 UTC", datetime(2021, 10, 30, 18, 17, 54, tzinfo=timezone.utc), None),
                                           pytest.param("%Y.%m.%d %H:%M:%S %Z", "2021.10.30 18:17:54 UTC", datetime(2021, 10, 30, 18, 17, 54, tzinfo=timezone.utc), None),
                                           pytest.param("%Y_%m_%d-%H_%M_%S_%Z", "2021_10_30-18_17_54_UTC", datetime(2021, 10, 30, 18, 17, 54, tzinfo=timezone.utc), None),
                                           pytest.param("%Y_%m_%d_%H_%M_%S_%Z", "2021_10_30_18_17_54_UTC", datetime(2021, 10, 30, 18, 17, 54, tzinfo=timezone.utc), None)]

get_grammar_from_dt_format_params_advanced = []


@pytest.mark.parametrize("in_format, in_date_string,expected, raises", get_grammar_from_dt_format_params_basic + get_grammar_from_dt_format_params_advanced)
def test_get_grammar_from_dt_format(in_format: str, in_date_string: str, expected, raises):
    if raises is None:
        raises = does_not_raise()
    with raises:
        grammar = get_grammar_from_dt_format(in_format)

        assert grammar.parse_string(in_date_string, parse_all=True)[0].as_datetime() == expected
