

NANOSECONDS_IN_SECOND: int = 1_000_000_000
MICROSECONDS_IN_SECOND: int = 1_000_000

RAW_STRING_TRUE_VALUES: set[str] = {'yes',
                                    'y',
                                    '1',
                                    'true',
                                    '+'}

RAW_STRING_FALSE_VALUES: set[str] = {'no',
                                     'n',
                                     '0',
                                     'false',
                                     '-'}


STRING_TRUE_VALUES: set[str] = {str(value).casefold() for value in RAW_STRING_TRUE_VALUES}

STRING_FALSE_VALUES: set[str] = {str(value).casefold() for value in RAW_STRING_FALSE_VALUES}


FILE_SIZE_SYMBOL_DATA: tuple[tuple[str, str]] = (('K', 'Kilo'),
                                                 ('M', 'Mega'),
                                                 ('G', 'Giga'),
                                                 ('T', 'Tera'),
                                                 ('P', 'Peta'),
                                                 ('E', 'Exa'),
                                                 ('Z', 'Zetta'),
                                                 ('Y', 'Yotta'))


RAW_TIMEUNITS: tuple[tuple[str, str, float, list[str]]] = (('nanosecond', 'ns', 1 / NANOSECONDS_IN_SECOND, []),
                                                           ("microsecond", "us", 1 / MICROSECONDS_IN_SECOND, ["mi", "mis", "mü", "müs", "μs"]),
                                                           ('millisecond', 'ms', 1 / 1000, []),
                                                           ('second', 's', 1.0, ["sec"]),
                                                           ('minute', 'm', 60.0, ["min", "mins"]),
                                                           ('hour', 'h', 60.0 * 60, []),
                                                           ('day', 'd', 60.0 * 60 * 24, []),
                                                           ('week', 'w', 60.0 * 60 * 24 * 7, []),
                                                           ("year", "y", (60.0 * 60 * 24 * 7 * 52) + (60.0 * 60 * 24), ["a"]))
