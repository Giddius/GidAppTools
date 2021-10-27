import pytest
from gidapptools.general_helper.conversion import seconds2human
from collections import namedtuple
import random
from datetime import timedelta, datetime
Param = namedtuple("Param", ["param", "name"], defaults=(None,))

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
]


actual_seconds2human_no_year_as_name_values = [item.param for item in seconds2human_no_year_as_name_params]
actual_seconds2human_no_year_as_name_names = [item.name for item in seconds2human_no_year_as_name_params]


@pytest.mark.parametrize("in_seconds, expected", actual_seconds2human_no_year_as_name_values, ids=actual_seconds2human_no_year_as_name_names)
def test_seconds2human_no_year_as_name(in_seconds, expected):
    assert seconds2human(in_seconds, as_symbols=False, with_year=False) == expected
