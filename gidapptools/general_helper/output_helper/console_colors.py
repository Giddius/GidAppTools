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
from enum import Enum, Flag, auto, unique
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from types import UnionType
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
    ...

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR: Path = Path(__file__).parent.absolute().resolve()

# endregion [Constants]


class ConsoleCodeTypus(Enum):
    FOREGROUND = auto()
    BACKGROUND = auto()
    MODIFICATION = auto()


INDICATOR_REGEX: re.Pattern = re.compile(r"\<(?P<typus>(SET|UNSET))_CONSOLE_CODE:(?P<names>[\w\|]+)\>")


class ConsoleColor:
    typus: ConsoleCodeTypus = None

    __slots__ = ("_name", "_code")

    def __init__(self, name: str, code: str) -> None:
        self._name = name
        self._code = code

    @property
    def name(self) -> str:
        return self._name

    @property
    def code(self) -> str:
        return self._code

    @property
    def set_indicator(self) -> str:
        return f"<SET_CONSOLE_CODE:{self.name}>"

    @property
    def unset_indicator(self) -> str:
        return f"<UNSET_CONSOLE_CODE:{self.name}>"

    def __call__(self, text: str) -> str:
        return f"{self.set_indicator}{text}{self.unset_indicator}"

    def __or__(self, other: Any) -> UnionType:
        if isinstance(other, ConsoleColor):
            if other.name in self.name.split("|"):
                return self
            else:
                return ConsoleColor(name=self.name + "|" + other.name, code=self.code + other.code)

        return NotImplemented

    def __str__(self) -> str:
        return self.code

    def __hash__(self):
        return hash((self._name, self._code))


class ConsoleForegroundColor(ConsoleColor):
    typus: ConsoleCodeTypus = ConsoleCodeTypus.FOREGROUND


class _ConsoleCodeDescriptor:

    def __init__(self, klass: type, code: str) -> None:
        self._klass = klass
        self._code = code
        self._name = None
        self._obj = None

    def __get__(self, obj: "ConsoleCodes", objtype=None):
        if self._obj is None:
            code = self._code if obj.is_applicable is True else ""
            self._obj = self._klass(name=self._name, code=code)
        return self._obj

    def __set_name__(self, owner, name: str):

        self._name = name.lstrip("_")


class ConsoleCodes:
    """
    ANSI color codes
    based on: https://gist.github.com/rene-d/9e584a7dd2935d0f461904b9f2950007
    """

    # __slots__ = ('_BLACK', '_RED', '_GREEN', '_BROWN', '_BLUE', '_PURPLE', '_CYAN', '_LIGHT_GRAY', '_DARK_GRAY', '_LIGHT_RED', '_LIGHT_GREEN', '_YELLOW', '_LIGHT_BLUE', '_LIGHT_PURPLE', '_LIGHT_CYAN', '_LIGHT_WHITE', '_WHITE',
    #              '_BOLD', '_FAINT', '_ITALIC', '_UNDERLINE', '_BLINK', '_NEGATIVE', '_CROSSED',
    #              '_RESET')

    BLACK = _ConsoleCodeDescriptor(ConsoleForegroundColor, code="\033[0;30m")
    RED = _ConsoleCodeDescriptor(ConsoleForegroundColor, code="\033[0;31m")

    def __init__(self):
        self._GREEN = ConsoleForegroundColor(name="GREEN", code="\033[0;32m" if self.is_applicable else "")
        self._BROWN = ConsoleForegroundColor(name="BROWN", code="\033[0;33m" if self.is_applicable else "")
        self._BLUE = ConsoleForegroundColor(name="BLUE", code="\033[0;34m" if self.is_applicable else "")
        self._PURPLE = ConsoleForegroundColor(name="PURPLE", code="\033[0;35m" if self.is_applicable else "")
        self._CYAN = ConsoleForegroundColor(name="CYAN", code="\033[0;36m" if self.is_applicable else "")
        self._LIGHT_GRAY = ConsoleForegroundColor(name="LIGHT_GRAY", code="\033[0;37m" if self.is_applicable else "")
        self._DARK_GRAY = ConsoleForegroundColor(name="DARK_GRAY", code="\033[1;30m" if self.is_applicable else "")
        self._LIGHT_RED = ConsoleForegroundColor(name="LIGHT_RED", code="\033[1;31m" if self.is_applicable else "")
        self._LIGHT_GREEN = ConsoleForegroundColor(name="LIGHT_GREEN", code="\033[1;32m" if self.is_applicable else "")
        self._YELLOW = ConsoleForegroundColor(name="YELLOW", code="\033[1;33m" if self.is_applicable else "")
        self._LIGHT_BLUE = ConsoleForegroundColor(name="LIGHT_BLUE", code="\033[1;34m" if self.is_applicable else "")
        self._LIGHT_PURPLE = ConsoleForegroundColor(name="LIGHT_PURPLE", code="\033[1;35m" if self.is_applicable else "")
        self._LIGHT_CYAN = ConsoleForegroundColor(name="LIGHT_CYAN", code="\033[1;36m" if self.is_applicable else "")
        self._LIGHT_WHITE = ConsoleForegroundColor(name="LIGHT_WHITE", code="\033[1;37m" if self.is_applicable else "")
        self._WHITE = ConsoleForegroundColor(name="WHITE", code="\033[97m" if self.is_applicable else "")

        self._BOLD = "\033[1m" if self.is_applicable else ""
        self._FAINT = "\033[2m" if self.is_applicable else ""
        self._ITALIC = "\033[3m" if self.is_applicable else ""
        self._UNDERLINE = "\033[4m" if self.is_applicable else ""
        self._BLINK = "\033[5m" if self.is_applicable else ""
        self._NEGATIVE = "\033[7m" if self.is_applicable else ""
        self._CROSSED = "\033[9m" if self.is_applicable else ""

        self._RESET = "\033[0m" if self.is_applicable else ""

    @property
    def is_atty(self) -> bool:
        return sys.stdout.isatty()

    @property
    def is_windows(self) -> bool:
        return platform.system().casefold() == "windows"

    @property
    def is_applicable(self) -> bool:
        return all([self.is_atty, self.is_windows])

    @property
    def GREEN(self):
        return self._GREEN

    @property
    def BROWN(self):
        return self._BROWN

    @property
    def BLUE(self):
        return self._BLUE

    @property
    def PURPLE(self):
        return self._PURPLE

    @property
    def CYAN(self):
        return self._CYAN

    @property
    def LIGHT_GRAY(self):
        return self._LIGHT_GRAY

    @property
    def DARK_GRAY(self):
        return self._DARK_GRAY

    @property
    def LIGHT_RED(self):
        return self._LIGHT_RED

    @property
    def LIGHT_GREEN(self):
        return self._LIGHT_GREEN

    @property
    def YELLOW(self):
        return self._YELLOW

    @property
    def LIGHT_BLUE(self):
        return self._LIGHT_BLUE

    @property
    def LIGHT_PURPLE(self):
        return self._LIGHT_PURPLE

    @property
    def LIGHT_CYAN(self):
        return self._LIGHT_CYAN

    @property
    def LIGHT_WHITE(self):
        return self._LIGHT_WHITE

    @property
    def WHITE(self):
        return self._WHITE

    @property
    def BOLD(self):
        return self._BOLD

    @property
    def FAINT(self):
        return self._FAINT

    @property
    def ITALIC(self):
        return self._ITALIC

    @property
    def UNDERLINE(self):
        return self._UNDERLINE

    @property
    def BLINK(self):
        return self._BLINK

    @property
    def NEGATIVE(self):
        return self._NEGATIVE

    @property
    def CROSSED(self):
        return self._CROSSED

    @property
    def RESET(self):
        return self._RESET

    def resolve_text(self, in_text: str) -> str:

        stack = []

        def _replace_func(in_match: re.Match):
            typus = in_match.group("typus")

            names = in_match.group("names").split("|")

            if typus == "SET":
                code = "".join(getattr(self, name).code for name in names)
                stack.append(code)
                return code

            if typus == "UNSET":
                text = self._RESET
                stack.pop(-1)
                if stack:
                    text += stack[-1]
                return text

        return INDICATOR_REGEX.sub(_replace_func, in_text) + self.RESET

# region [Main_Exec]


if __name__ == '__main__':
    col = ConsoleCodes()

    x = col.RED("I am red " + col.BLACK("I am purple") + " I am red")

    print(col.resolve_text(x))

# endregion [Main_Exec]
