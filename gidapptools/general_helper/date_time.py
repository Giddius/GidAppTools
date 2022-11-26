"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone, timedelta
from functools import total_ordering

# * Third Party Imports --------------------------------------------------------------------------------->
import attr

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import DateTimeFrameTimezoneError, NotUtcDatetimeError

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


# def seconds2human()


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


def _validate_date_time_frame_tzinfo(instance: "DateTimeFrame", attribute: attr.Attribute, value: datetime):
    if instance.start.tzinfo is None or instance.end.tzinfo is None:
        raise DateTimeFrameTimezoneError(instance, instance.start.tzinfo, instance.end.tzinfo, 'start time and end time need to be timezone aware')
    if instance.start.tzinfo != instance.end.tzinfo:
        raise DateTimeFrameTimezoneError(instance, instance.start.tzinfo, instance.end.tzinfo, 'start time and end time do not have the same timezone')


@attr.s(auto_attribs=True, auto_detect=True, frozen=True, slots=True)
@total_ordering
class DateTimeFrame:
    start: datetime = attr.ib(validator=_validate_date_time_frame_tzinfo)
    end: datetime = attr.ib(validator=_validate_date_time_frame_tzinfo)

    @property
    def delta(self) -> timedelta:
        return self.end - self.start

    @property
    def tzinfo(self) -> timezone:
        return self.start.tzinfo

    def __eq__(self, other: object) -> bool:
        if isinstance(other, datetime):
            return self.start <= other <= self.end
        if isinstance(other, self.__class__):
            return self.start == other.start and self.end == other.end
        if isinstance(other, timedelta):
            return self.delta == other
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, datetime):
            return self.start < other
        if isinstance(other, self.__class__):
            return self.end < other.start
        if isinstance(other, timedelta):
            return self.delta < other
        return NotImplemented

    def __contains__(self, other: object) -> bool:
        if isinstance(other, datetime):
            return self.start <= other <= self.end
        return NotImplemented

    def __str__(self) -> str:
        return f"{self.start.isoformat(sep=' ')} until {self.end.isoformat(sep=' ')}"

    def __hash__(self) -> int:
        return hash(self.start) + hash(self.end) + hash(self.delta)


ZERO_TIMEDELTA = timedelta()


def calculate_utc_offset(utc_datetime: datetime, local_datetime: datetime, offset_class: type[timezone] = timezone):
    if utc_datetime.tzinfo.tzname(None) != "UTC" and utc_datetime.tzinfo != timezone.utc and utc_datetime.tzinfo.utcoffset(None) != ZERO_TIMEDELTA:
        raise NotUtcDatetimeError(utc_datetime)
    difference_seconds = (local_datetime.replace(tzinfo=timezone.utc) - utc_datetime)

    difference_seconds = difference_seconds.total_seconds()
    offset_timedelta = timedelta(seconds=int(difference_seconds))
    offset_hours = offset_timedelta.total_seconds() / (60 * 60)

    offset_hours = int(offset_hours)
    prefix = "" if offset_hours < 0 else "+"

    name = prefix + str(offset_hours)
    return offset_class(offset=offset_timedelta, name=name)

# region[Main_Exec]


if __name__ == '__main__':
    from tzlocal import get_localzone
    from dateutil.tz import UTC
    x = calculate_utc_offset(datetime.now(tz=UTC), datetime.now())
    print(x)


# endregion[Main_Exec]
