import pytest
from gidapptools.gid_parsing.universal.datetime_elements import datetime_format_mapping
import pyparsing as pp
datetime_format_mapping_params_basic = [pytest.param("%Y", "2001", 2001, None, id="%Y Year"),
                                        pytest.param("%m", "01", 1, None, id="%m Month"),
                                        pytest.param("%d", "15", 15, None, id="%d Day"),
                                        pytest.param("%H", "21", 21, None, id="%H Hour"),
                                        pytest.param("%M", "23", 23, None, id="%M Minute"),
                                        pytest.param("%S", "59", 59, None, id="%S Second"),
                                        pytest.param("%f", "074040", "074040", None, id="%f Microsecond"),
                                        pytest.param("%Z", "UTC", "UTC", None, id="%Z Timezone")]

datetime_format_mapping_params_advanced = [pytest.param("%Z", "CET", "CET", None, id="%Z CET Timezone Advanced"),
                                           pytest.param("%Z", "UTC+03:00", "UTC+03:00", None, id="%Z UTC+03:00 Timezone Advanced"),
                                           pytest.param("%Z", "UTC-03:00", "UTC-03:00", None, id="%Z UTC-03:00 Timezone Advanced"),
                                           pytest.param("%m", "1", 1, None, id="%m Month Advanced"), ]


@pytest.mark.parametrize("format_char, in_data, expected, raises", datetime_format_mapping_params_basic + datetime_format_mapping_params_advanced)
def test_datetime_format_mapping(format_char: str, in_data: str, expected: str, raises):
    element: pp.ParserElement = datetime_format_mapping[format_char]
    result = element.parse_string(in_data, parse_all=True)
    print(result)
    assert result[0] == expected
