import attr


NANOSECONDS_IN_SECOND: int = 1_000_000_000
MICROSECONDS_IN_SECOND: int = 1_000_000

RAW_STRING_TRUE_VALUES: frozenset[str] = frozenset({'yes',
                                                    'y',
                                                    '1',
                                                    'true',
                                                    '+'})

RAW_STRING_FALSE_VALUES: frozenset[str] = frozenset({'no',
                                                     'n',
                                                     '0',
                                                     'false',
                                                     '-'})


STRING_TRUE_VALUES: frozenset[str] = frozenset({str(value).casefold() for value in RAW_STRING_TRUE_VALUES})

STRING_FALSE_VALUES: frozenset[str] = frozenset({str(value).casefold() for value in RAW_STRING_FALSE_VALUES})


FILE_SIZE_SYMBOL_DATA: tuple[tuple[str, str]] = (('K', 'Kilo'),
                                                 ('M', 'Mega'),
                                                 ('G', 'Giga'),
                                                 ('T', 'Tera'),
                                                 ('P', 'Peta'),
                                                 ('E', 'Exa'),
                                                 ('Z', 'Zetta'),
                                                 ('Y', 'Yotta'))


@attr.s(auto_attribs=True, auto_detect=True, frozen=True, slots=True, weakref_slot=True)
class TimeUnit:
    name: str = attr.ib()
    symbol: str = attr.ib()
    factor: float = attr.ib(order=True, eq=True)
    aliases: tuple[str] = attr.ib(converter=tuple, default=tuple())
    plural: str = attr.ib()

    @plural.default
    def default_plural(self):
        return self.name + "s"

    def convert_seconds(self, in_seconds: int) -> int:
        return int(in_seconds / self.factor)

    def convert_with_rest(self, in_seconds: int) -> tuple[int, int]:
        _amount, _rest = divmod(in_seconds, self.factor)

        return int(_amount), _rest

    def value_to_string(self, in_value: int, use_symbols: bool = False) -> str:
        if use_symbols is True:
            return f"{in_value}{self.symbol}"
        if in_value == 1:
            return f"{in_value} {self.name}"
        return f"{in_value} {self.plural}"


RAW_TIMEUNITS: tuple[TimeUnit] = (
    TimeUnit(name='nanosecond', symbol='ns', factor=1 / NANOSECONDS_IN_SECOND, aliases=tuple()),
    TimeUnit(name="microsecond", symbol="us", factor=1 / MICROSECONDS_IN_SECOND, aliases=("mi", "mis", "mü", "müs", "μs")),
    TimeUnit(name='millisecond', symbol='ms', factor=1 / 1000, aliases=tuple()),
    TimeUnit(name='second', symbol='s', factor=1.0, aliases=("sec",)),
    TimeUnit(name='minute', symbol='m', factor=60.0, aliases=("min", "mins")),
    TimeUnit(name='hour', symbol='h', factor=60.0 * 60, aliases=tuple()),
    TimeUnit(name='day', symbol='d', factor=60.0 * 60 * 24, aliases=tuple()),
    TimeUnit(name='week', symbol='w', factor=60.0 * 60 * 24 * 7, aliases=tuple()),
    TimeUnit(name="year", symbol="y", factor=(60.0 * 60 * 24 * 7 * 52) + (60.0 * 60 * 24), aliases=("a",))
)


TIMEUNITS = sorted(RAW_TIMEUNITS, reverse=True)

TIMEUNIT_NAME_MAP = {t.name.casefold(): t for t in TIMEUNITS}
