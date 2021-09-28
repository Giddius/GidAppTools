from typing import ClassVar, Iterable, Union
from gidapptools.general_helper.deprecation import deprecated_argument
import attr
import inflect
import re
from gidapptools.data.conversion_data import NANOSECONDS_IN_SECOND, STRING_FALSE_VALUES, STRING_TRUE_VALUES
from functools import cached_property, total_ordering
from gidapptools.general_helper.timing import time_execution, time_func


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

    def _get_names(self) -> Union[set[str]]:
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
            with time_execution(name):
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


@time_func()
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
        _amount = in_seconds // self.factor
        if _amount > 0:
            _rest = in_seconds - (_amount * self.factor)
            _amount = f"{_amount} {self.symbol}"
        else:
            _rest = in_seconds
            _amount = None
        return _amount, _rest


TIMEUNITS = [TimeUnit(*item) for item in [('nanosecond', 'ns', 1 / NANOSECONDS_IN_SECOND), ('millisecond', 'ms', 1 / 1000), ('second', 's', 1), ('minute', 'm', 60), ('hour', 'h', 60 * 60), ('day', 'd', 60 * 60 * 24), ('week', 'w', 60 * 60 * 24 * 7)]]
TIMEUNITS = sorted(TIMEUNITS, key=lambda x: x.factor, reverse=True)


def seconds2human(in_seconds: int) -> str:
    ...


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
