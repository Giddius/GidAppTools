import pytest
from gidapptools.general_helper.conversion import seconds2human, human2timedelta
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


def year_to_seconds(in_year_amount: int) -> int:
    return in_year_amount * (60 * 60 * 24 * 7 * 52) + (60 * 60 * 24)


def nanoseconds_to_seconds(in_nanoseconds: int) -> int:
    return in_nanoseconds * (1 / 1_000_000_000)


test_human2timedelta_params = [pytest.param("", timedelta(), id="empty string"),
                               pytest.param("1 nanosecond", timedelta(seconds=nanoseconds_to_seconds(1)), id="nanosecond positive"),
                               pytest.param("1 microsecond", timedelta(microseconds=1), id="microsecond positive"),
                               pytest.param("1 millisecond", timedelta(milliseconds=1), id="millisecond positive"),
                               pytest.param("1 second", timedelta(seconds=1), id='second positive'),
                               pytest.param("1 minute", timedelta(minutes=1), id="minute positive"),
                               pytest.param("1 hour", timedelta(hours=1), id="hour positive"),
                               pytest.param("1 day", timedelta(days=1), id="day positive"),
                               pytest.param("1 week", timedelta(weeks=1), id="week positive"),
                               pytest.param("1 year", timedelta(seconds=year_to_seconds(1)), id="year positive"),
                               pytest.param("-1 nanosecond", -timedelta(seconds=nanoseconds_to_seconds(1)), id="nanosecond negative"),
                               pytest.param("-1 microsecond", -timedelta(microseconds=1), id="microsecond negative"),
                               pytest.param("-1 millisecond", -timedelta(milliseconds=1), id="millisecond negative"),
                               pytest.param("-1 second", -timedelta(seconds=1), id='second negative'),
                               pytest.param("-1 minute", -timedelta(minutes=1), id="minute negative"),
                               pytest.param("-1 hour", -timedelta(hours=1), id="hour negative"),
                               pytest.param("-1 day", -timedelta(days=1), id="day negative"),
                               pytest.param("-1 week", -timedelta(weeks=1), id="week negative"),
                               pytest.param("-1 year", -timedelta(seconds=year_to_seconds(1)), id="year negative"),
                               pytest.param("22 hours 7 seconds 4 microseconds", timedelta(hours=22, seconds=7, microseconds=4), id="combined 1 positive"),
                               pytest.param("since 40 weeks 7 hours 1 second", -timedelta(weeks=40, hours=7, seconds=1), id="combined 2 word-negative")
                               ]


@ pytest.mark.parametrize("in_text, expected", test_human2timedelta_params)
def test_human2timedelta(in_text, expected):
    assert human2timedelta(in_text) == expected
