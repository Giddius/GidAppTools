"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Union, Generator
from datetime import datetime, timezone, timedelta, tzinfo
from functools import total_ordering
import pytz
import traceback
from collections import defaultdict
import copy
from threading import Lock
import pp
from math import ceil
# * Third Party Imports --------------------------------------------------------------------------------->


# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import DateTimeFrameTimezoneError, NotUtcDatetimeError
from gidapptools.gid_logger.logger import get_logger

import sys
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
log = get_logger(__name__)
# endregion [Constants]


def get_all_timezone_names() -> tuple[str]:
    return tuple(sorted(pytz.all_timezones))


def get_all_timezones() -> tuple[pytz.BaseTzInfo]:
    return tuple(pytz.timezone(i) for i in get_all_timezone_names())


def get_all_timezone_names_by_region() -> dict[str, list[str]]:
    single_europe_names = {"Poland", "Portugal", "Iceland", "Turkey", "Eire", "GB", "GB-Eire", "EET", "CET", "WET", "Greenwich"}

    single_asia_names = {"Hongkong", "Japan", "Singapore", "ROK", "ROC", "PRC", "Turkey", "Iran", "Israel"}

    single_africa_names = {"Libya", "Egypt"}

    single_america_names = {"Cuba", "Jamaica", "Navajo", "HST", "MST"}

    single_pacific_names = {"Kwajalein", "NZ", "NZ-CHAT", "HST"}

    all_single_names = single_europe_names.union(single_asia_names, single_africa_names, single_america_names, single_pacific_names)

    region_map = defaultdict(list)
    for time_zone_name in get_all_timezone_names():
        if time_zone_name.casefold().startswith("etc/") or "/" not in time_zone_name:
            if time_zone_name in all_single_names:
                if time_zone_name in single_europe_names:
                    region_map["Europe"].append(time_zone_name)

                if time_zone_name in single_asia_names:
                    region_map["Asia"].append(time_zone_name)

                if time_zone_name in single_africa_names:
                    region_map["Africa"].append(time_zone_name)

                if time_zone_name in single_america_names:
                    region_map["America"].append(time_zone_name)

                if time_zone_name in single_pacific_names:
                    region_map["Pacific"].append(time_zone_name)
            else:
                region_map["misc"].append(time_zone_name)

        else:
            for region_name in time_zone_name.split("/")[:-1]:
                region_map[region_name].append(time_zone_name)

    return region_map


def get_all_timezones_by_region() -> dict[str, list[pytz.BaseTzInfo]]:
    new_map = {}
    time_zone_map = get_all_timezone_names_by_region()
    for region in time_zone_map:
        new_map[region] = [pytz.timezone(i) for i in time_zone_map[region]]

    return new_map


def get_all_timezones_by_offset_hours(include_dst_timezone: bool = True) -> dict[int, tuple[pytz.BaseTzInfo]]:
    now = datetime.now()
    now_three_years_ago = now.replace(year=now.year - 3)
    _out = defaultdict(list)

    for time_zone in get_all_timezones():
        if include_dst_timezone is False and isinstance(time_zone, pytz.tzinfo.DstTzInfo) and time_zone._utc_transition_times[-1] >= now_three_years_ago:

            continue
        try:
            offset = time_zone.utcoffset(now)
            offset_hours = int(offset.total_seconds() // 3600)
            _out[offset_hours].append(time_zone)
        except Exception as e:
            log.error(e, exc_info=True)

    return {k: tuple(v) for k, v in _out.items()}


class DatetimeFmt(str, Enum):
    STANDARD = "%Y-%m-%d %H:%M:%S"
    FILE = "%Y-%m-%d_%H-%M-%S"
    LOCAL = "%x %X"

    STANDARD_TZ = "%Y-%m-%d %H:%M:%S %Z"
    FILE_TZ = "%Y-%m-%d_%H-%M-%S_%Z"
    LOCAL_TZ = "%x %X %Z"

    def strf(self, date_time: datetime) -> str:
        non_tz_fmt = self if not self.name.endswith('_TZ') else getattr(self, self.name.removesuffix('_TZ'))
        tz_fmt = self if self.name.endswith('_TZ') else getattr(self, self.name + '_TZ')
        if date_time.tzinfo is None:
            return date_time.strftime(non_tz_fmt)
        return date_time.strftime(tz_fmt)


def get_aware_now(tz: timezone) -> datetime:
    return datetime.now(tz=tz)


def get_utc_now() -> datetime:
    return get_aware_now(tz=timezone.utc)


@ total_ordering
class DateTimeFrame:
    __slots__ = ("_start",
                 "_end")

    def __init__(self, start: datetime, end: datetime) -> None:
        self._start = start
        self._end = end
        self._validate()

    def _validate(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise DateTimeFrameTimezoneError(self, self.start.tzinfo, self.end.tzinfo, 'start time and end time need to be timezone aware')
        if self.start.tzinfo != self.end.tzinfo:
            raise DateTimeFrameTimezoneError(self, self.start.tzinfo, self.end.tzinfo, 'start time and end time do not have the same timezone')

        if self.start > self.end:
            raise ValueError(f"start {self.start!r} cannot be after end ({self.end!r}) for {self.__class__.__name__!r}.")

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def end(self) -> datetime:
        return self._end

    @ property
    def delta(self) -> timedelta:
        return self.end - self.start

    @ property
    def tzinfo(self) -> timezone:
        return self.start.tzinfo

    def with_start(self, new_start: datetime) -> Self:
        return self.__class__(new_start, self.end)

    def with_end(self, new_end: datetime) -> Self:
        return self.__class__(self.start, new_end)

    def modify_start(self, delta: timedelta) -> Self:
        return self.__class__(self.start + delta, self.end)

    def modify_end(self, delta: timedelta) -> Self:
        return self.__class__(self.start, self.end + delta)

    def modify_start_and_end(self, delta: timedelta) -> Self:
        return self.__class__(self.start + delta, self.end + delta)

    def iter_equal_steps(self, amount_of_steps: int) -> Generator[datetime, None, None]:
        step_size = self.delta / (amount_of_steps - 1)
        print(f"{step_size=}")

        for i in range(amount_of_steps - 1):
            yield self.start + (step_size * i)
        yield self.end

    def __sub__(self, other: object) -> Self:
        if isinstance(other, timedelta):
            return self.modify_end(-other)

        if isinstance(other, datetime) and other in self:
            if other <= self.end:
                return self.with_end(other)

            if other >= self.start:
                return self.with_start(other)

        return NotImplemented

    def __add__(self, other: object) -> Self:
        if isinstance(other, timedelta):
            return self.modify_end(other)

        if isinstance(other, datetime):
            if other > self.end:
                return self.with_end(other)

            if other < self.start:
                return self.with_start(other)

            if other in self:
                return copy.copy(self)

        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DateTimeFrame):
            return self.start == other.start and self.end == other.end

        if isinstance(other, timedelta):
            return self.delta == other

        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, datetime):
            return self.start < other

        if isinstance(other, DateTimeFrame):
            return self.start < other.start

        if isinstance(other, timedelta):
            return self.delta < other

        return NotImplemented

    def __contains__(self, other: object) -> bool:
        if isinstance(other, datetime):
            return self.start <= other <= self.end

        if isinstance(other, DateTimeFrame):
            return self.start <= other.start and self.end >= other.end

        return NotImplemented

    def __copy__(self) -> Self:
        new_instance = self.__class__.__new__(self.__class__)

        for attr_name in self.__slots__:
            if attr_name not in {"weakref", }:
                setattr(new_instance, attr_name, getattr(self, attr_name))

        return new_instance

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(start={self.start!r}, end={self.end!r})"

    def __str__(self) -> str:
        return f"{self.start.isoformat(sep=' ')} until {self.end.isoformat(sep=' ')}"


ZERO_TIMEDELTA = timedelta()


def calculate_utc_offset(utc_datetime: datetime, local_datetime: datetime, offset_class: type[timezone] = timezone, as_pytz_timezone: bool = False) -> Union[timezone, pytz.BaseTzInfo]:
    if utc_datetime.tzinfo.tzname(None) != "UTC" and utc_datetime.tzinfo != timezone.utc and utc_datetime.tzinfo.utcoffset(None) != ZERO_TIMEDELTA:
        raise NotUtcDatetimeError(utc_datetime)
    difference_seconds = (local_datetime.replace(tzinfo=timezone.utc) - utc_datetime).total_seconds()

    offset_timedelta = timedelta(seconds=int(difference_seconds))
    offset_hours = offset_timedelta.total_seconds() / (60 * 60)

    offset_hours = round(offset_hours)

    prefix = "" if (offset_hours * (-1)) < 0 else "+"

    name = "Etc/GMT" + prefix + str(offset_hours * (-1))

    if as_pytz_timezone is True:
        return pytz.timezone(name)
    return offset_class(offset=timedelta(hours=offset_hours), name=name)


def pytz_timezone_from_utc_offset(in_offset_hours: int, only_named_timezones: bool = False, allow_dst_timezone: bool = True) -> tuple[pytz.BaseTzInfo]:
    ...


# region [Main_Exec]
if __name__ == '__main__':
    begi = datetime.now(tz=timezone.utc) - timedelta(days=1)
    x = DateTimeFrame(begi, datetime.now(tz=timezone.utc))

    print(f"{x=}")

    y = list(x.iter_equal_steps(1000))
    print(f"{len(y)=}")
    print(f"{y[-2]=}")
    print(f"{y[-1]=}")
    print(f"{x.end=}")

    print(f"{y[0]=}")
    print(f"{x.start=}")
    print(f"{y[0]==x.start=}")
    print(f"{y[-1]==x.end=}")

    for ii in y:
        print(ii.timestamp())

    a = x.__copy__()

    print(a)
    print(f"{a == x=}")
    print(f"{a is x=}")
    print(f"{hash(x) == hash(a)=}")


# endregion [Main_Exec]
