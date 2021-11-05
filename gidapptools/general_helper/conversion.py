from typing import ClassVar, Iterable, Union
from gidapptools.general_helper.deprecation import deprecated_argument
import attr
import inflect
import re
from functools import cached_property, total_ordering
from datetime import datetime, timedelta, timezone
import random

NANOSECONDS_IN_SECOND: int = 1_000_000_000


RAW_STRING_TRUE_VALUES = {'yes',
                          'y',
                          '1',
                          'true',
                          '+'}

RAW_STRING_FALSE_VALUES = {'no',
                           'n',
                           '0',
                           'false',
                           '-'}


STRING_TRUE_VALUES = {str(value).casefold() for value in RAW_STRING_TRUE_VALUES}

STRING_FALSE_VALUES = {str(value).casefold() for value in RAW_STRING_FALSE_VALUES}


@total_ordering
class FileSizeUnit:

    def __init__(self, short_name: str, long_name: str, factor: int, aliases: Iterable[str] = None) -> None:
        self._short_name = short_name
        self._long_name = long_name
        self.factor = factor
        self.aliases = [] if aliases is None else aliases
        self.aliases += self._get_default_aliases()
        self.all_names = self._get_names()
        self.all_names_casefolded = {name.casefold() for name in self.all_names}

    @cached_property
    def short_name(self) -> str:
        return f"{self._short_name}b"

    @cached_property
    def long_name(self) -> str:
        return f"{self._long_name}bytes"

    def _get_names(self) -> set[str]:
        all_names = [self.short_name, self.long_name] + self.aliases
        all_names += [name.removesuffix('s') for name in all_names]
        all_names += [name + 's' for name in all_names if not name.endswith('s')]
        return set(all_names)

    def _get_default_aliases(self) -> Iterable[str]:
        _out = []

        _out.append(f"{self._long_name} bytes")

        return _out

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.factor == o.factor

        if isinstance(o, int):
            return self.factor == o

        if isinstance(o, str):
            return o in {self.short_name, self.long_name}.union(set(self.aliases))

        return NotImplemented

    def __lt__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.factor < o.factor
        if isinstance(o, int):
            return self.factor < o

        return NotImplemented

    def __truediv__(self, o: object) -> float:
        if isinstance(o, self.__class__):
            return self.factor / o.factor
        if isinstance(o, int):
            return self.factor / o

        if isinstance(o, float):
            return float(self.factor) / o
        return NotImplemented

    def __rtruediv__(self, o: object) -> float:
        if isinstance(o, self.__class__):
            return o.factor / self.factor
        if isinstance(o, int):
            return o / self.factor

        if isinstance(o, float):
            return o / float(self.factor)

        return NotImplemented

    def __str__(self) -> str:
        return self.short_name


class FileSizeByte(FileSizeUnit):
    # pylint: disable=super-init-not-called
    def __init__(self) -> None:
        self.short_name = 'b'
        self.long_name = 'bytes'
        self.factor = 1
        self.aliases = []
        self.all_names = self._get_names()
        self.all_names_casefolded = {name.casefold() for name in self.all_names}


class FileSizeReference:

    def __init__(self) -> None:
        self.byte_unit = FileSizeByte()
        self.units: tuple[FileSizeUnit] = None
        self._make_units()

    def _make_units(self) -> None:
        self.units = []
        symbol_data = [('K', 'Kilo'),
                       ('M', 'Mega'),
                       ('G', 'Giga'),
                       ('T', 'Tera'),
                       ('P', 'Peta'),
                       ('E', 'Exa'),
                       ('Z', 'Zetta'),
                       ('Y', 'Yotta')]
        temp_unit_info = {s: 1 << (i + 1) * 10 for i, s in enumerate(symbol_data)}
        for key, value in temp_unit_info.items():
            self.units.append(FileSizeUnit(short_name=key[0], long_name=key[1], factor=value))
        self.units = tuple(sorted(self.units))

    @property
    def symbols(self) -> Iterable[str]:
        return tuple(item.short_name for item in self.units)

    def get_unit_by_name(self, name: str, case_insensitive: bool = True) -> FileSizeUnit:
        try:
            all_names = [unit for unit in self.units if name in unit.all_names_casefolded]
            return all_names[0]
        except IndexError as error:
            if name in self.byte_unit.all_names_casefolded:
                return self.byte_unit
            raise KeyError(name) from error


FILE_SIZE_REFERENCE = FileSizeReference()


@deprecated_argument(arg_name='annotate')
def bytes2human(n: int, annotate: bool = True) -> str:
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    # if annotate is not None:

    # symbols = ('Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb')
    # prefix = {s: 1 << (i + 1) * 10 for i, s in enumerate(symbols)}

    for unit in reversed(FILE_SIZE_REFERENCE.units):
        if n >= unit:
            _out = float(n) / unit

            _out = f'{_out:.1f} {unit}'
            return _out
    _out = n

    return f"{_out} b"


def human2bytes(in_text: str) -> int:
    def _clean_name(name: str) -> str:
        name = name.strip()
        name = name.casefold()
        name = white_space_regex.sub(' ', name)
        return name
    white_space_regex = re.compile(r"\s{2,}")
    number_regex_pattern = r"(?P<number>\d+)"
    name_regex_pattern = r"(?P<name>\w([\w\s]+)?)"
    parse_regex = re.compile(number_regex_pattern + r'\s*' + name_regex_pattern)

    match = parse_regex.match(in_text.strip())
    if match:
        number = int(match.group('number'))
        name = _clean_name(match.group('name'))
        unit = FILE_SIZE_REFERENCE.get_unit_by_name(name)
        return number * unit.factor
    else:
        # TODO: custom error
        raise RuntimeError(f"Unable to parse input string {in_text!r}.")


def ns_to_s(nano_seconds: int, decimal_places: int = None) -> Union[int, float]:
    seconds = nano_seconds / NANOSECONDS_IN_SECOND
    if decimal_places is None:
        return seconds
    return round(seconds, decimal_places)


@attr.s(auto_attribs=True, auto_detect=True, frozen=True)
class TimeUnit:
    inflect_engine: ClassVar[inflect.engine] = inflect.engine()
    name: str = attr.ib()
    symbol: str = attr.ib()
    factor: int = attr.ib()

    @property
    def plural(self):
        return self.inflect_engine.plural_noun(self.name)

    def convert_seconds(self, in_seconds: int) -> int:
        return in_seconds / self.factor

    def convert_with_rest(self, in_seconds: int) -> tuple[int, int]:
        _amount, _rest = divmod(in_seconds, self.factor)

        return int(_amount), _rest

    def value_to_string(self, in_value: int, use_symbols: bool = False) -> str:
        if use_symbols is True:
            return f"{in_value}{self.symbol}"
        if in_value == 1:
            return f"{in_value} {self.name}"
        return f"{in_value} {self.plural}"


TIMEUNITS = [TimeUnit(*item) for item in [('nanosecond', 'ns', 1 / NANOSECONDS_IN_SECOND), ('millisecond', 'ms', 1 / 1000), ('second', 's', 1),
                                          ('minute', 'm', 60), ('hour', 'h', 60 * 60), ('day', 'd', 60 * 60 * 24), ('week', 'w', 60 * 60 * 24 * 7), ("year", "y", (60 * 60 * 24 * 7 * 52) + (60 * 60 * 24))]]
TIMEUNITS = sorted(TIMEUNITS, key=lambda x: x.factor, reverse=True)


class TimeUnits:

    def __init__(self, with_year: bool = True) -> None:
        self._units = TIMEUNITS.copy()
        self.with_year = with_year

    @property
    def smallest_unit(self) -> TimeUnit:
        return self.units[-1]

    @property
    def units(self):
        if self.with_year is False:
            return [u for u in self._units.copy() if u.name != 'year']
        return self._units.copy()

    def __iter__(self):
        return iter(self.units)


def seconds2human(in_seconds: Union[int, float, timedelta], as_symbols: bool = False, with_year: bool = True) -> str:
    rest = in_seconds.total_seconds() if isinstance(in_seconds, timedelta) else in_seconds
    result = {}
    _time_units = TimeUnits(with_year=with_year)
    for unit in _time_units:
        amount, rest = unit.convert_with_rest(rest)
        if amount:
            result[unit] = int(amount)

    results = [k.value_to_string(v, as_symbols) for k, v in result.items()]
    if not results:
        _unit = _time_units.smallest_unit
        _name = f" {_unit.plural}" if as_symbols is False else _unit.symbol
        return f"0{_name}"
    if len(results) > 1:
        return ' '.join(results[:-1]) + ' and ' + results[-1]
    return results[0]


def str_to_bool(in_string: str, strict: bool = False) -> bool:
    if isinstance(in_string, bool):
        return in_string
    mod_string = in_string.casefold().strip()
    if strict is False:
        return mod_string in STRING_TRUE_VALUES

    if mod_string in STRING_TRUE_VALUES:
        return True
    if mod_string in STRING_FALSE_VALUES:
        return False

    raise TypeError(f'Unable to convert string {in_string!r} to a Boolean value.')


if __name__ == '__main__':
    pass
