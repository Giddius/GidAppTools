"""
WiP.

Soon.
"""

# region [Imports]

import os
import re
import sys
import json
import queue
import math
import base64
import pickle
import random
import shelve
import dataclasses
import shutil
import asyncio
import logging
import sqlite3
import platform

import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
import enum
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
import types
from typing import (TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, ForwardRef, final, Callable,
                    no_type_check, no_type_check_decorator, overload, get_type_hints, cast, Protocol, runtime_checkable, NoReturn, NewType, Literal, AnyStr, IO, BinaryIO, TextIO, Any)
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from collections.abc import (AsyncGenerator, AsyncIterable, AsyncIterator, Awaitable, ByteString, Callable, Collection, Container, Coroutine, Generator,
                             Hashable, ItemsView, Iterable, Iterator, KeysView, Mapping, MappingView, MutableMapping, MutableSequence, MutableSet, Reversible, Sequence, Set, Sized, ValuesView)
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property, cache
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, wait, as_completed, ALL_COMPLETED, FIRST_EXCEPTION, FIRST_COMPLETED


if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    from gidapptools.gidcolor.color import Color

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

FORMATTER_TYPE: TypeAlias = Callable[["Color", bool], str]


FORMATTER_TYPE_T = TypeVar("FORMATTER_TYPE_T", bound=FORMATTER_TYPE)


@enum.verify(enum.UNIQUE)
class ColorFormatSystem(enum.Enum):
    RGB = "rgb"
    HSL = "hsl"
    HSV = "hsv"

    HLS = "hls"

    @classmethod
    @property
    def target_string(self) -> str:
        return "system"


@enum.verify(enum.UNIQUE)
class ColorFormatContext(enum.Enum):
    CSS = "css"

    @classmethod
    @property
    def target_string(self) -> str:
        return "context"


@enum.verify(enum.UNIQUE)
class ColorFormatTypus(enum.Enum):
    FLOAT = "float"
    INT = "int"

    PRETTY = "pretty"

    @classmethod
    @property
    def target_string(self) -> str:
        return "typus"


class ColorStringFormatter:

    alpha_part_regex = re.compile(r"[+-](a|alpha)", re.IGNORECASE)

    def __init__(self) -> None:
        pass

    def parse_format_string(self, format_string: str) -> tuple["ColorFormat", bool]:
        color_format = ColorFormat()
        with_alpha = True
        for format_enum in (ColorFormatSystem, ColorFormatContext, ColorFormatTypus):
            if format_string.startswith(("+a", "-a")):
                with_alpha = format_string[0] == "+"
                format_string = format_string[2:]
            for item in format_enum._member_map_.values():
                identifier = item.value

                if format_string.startswith(identifier):
                    print(identifier)
                    setattr(color_format, format_enum.target_string, item)
                    format_string = format_string.removeprefix(identifier)
                    break

        if format_string != "":
            raise ValueError(f"Invalid Format-String {format_string!r}")
        return color_format, with_alpha

    def format_color(self,
                     color: "Color",
                     color_format: "ColorFormat" = None,
                     with_alpha: bool = True) -> str:
        if color_format is None:
            color_format = ColorFormat()

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}'


class ColorFormat:

    def __init__(self,
                 system: ColorFormatSystem = None,
                 context: ColorFormatContext = None,
                 typus: ColorFormatTypus = None) -> None:
        self.system = system
        self.context = context
        self.typus = typus

    def __or__(self, other: object) -> Self:
        if isinstance(other, ColorFormatSystem):
            return self.__class__(system=other, context=self.context, typus=self.typus)
        if isinstance(other, ColorFormatContext):
            return self.__class__(system=self.system, context=other, typus=self.typus)

        if isinstance(other, ColorFormatTypus):
            return self.__class__(system=self.system, context=self.context, typus=other)

        else:
            return NotImplemented

    def __contains__(self, other: object) -> bool:
        if isinstance(other, ColorFormatSystem):
            return self.system is other
        if isinstance(other, ColorFormatContext):
            return self.context is other

        if isinstance(other, ColorFormatTypus):
            return self.typus is other

        else:
            return NotImplemented

    def __str__(self) -> str:
        parts = []
        for attr_name in ("system", "context", "typus"):
            value = getattr(self, attr_name)
            if value is None:
                parts.append(str(None))
            else:
                parts.append(value.name)

        return "|".join(parts)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(system={self.system!r}, context={self.context!r}, typus={self.typus!r})'

# region [Main_Exec]


if __name__ == '__main__':
    x = ColorStringFormatter()

    y = "rgb+acssfloat"

    u = x.parse_format_string(y)

    print(u)

# endregion [Main_Exec]
