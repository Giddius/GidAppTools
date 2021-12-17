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
import importlib
import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
import logging
from gidapptools.general_helper.enums import BaseGidEnum
import warnings
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def _add_new_logging_level(name: str, value: int) -> None:
    if (name in logging._nameToLevel and value in logging._levelToName) and (logging._nameToLevel.get(name) == value and logging._levelToName.get(value) == name):
        return
    if name not in logging._nameToLevel:
        if logging._levelToName.get(value) is not None:
            raise ValueError(f"Value {value!r} already used by a different LoggingLevel ({logging._levelToName(value)!r}).")
        logging.addLevelName(value, name)
    elif value not in logging._levelToName:
        if logging._nameToLevel.get(name) is not None:
            raise ValueError(f"Name {name!r} already used by a different LoggingLevel ({logging._nameToLevel(name)!r}).")
        logging.addLevelName(value, name)
    else:
        raise RuntimeError(f"something went wrong with checking the LogLevel {name=}, {value=}.")


def _check_if_all_levels_are_in_LoggingLevel() -> None:
    if any(name not in set(LoggingLevel._member_map_.keys()) for name in logging._nameToLevel):
        missing_member_names = set(logging._nameToLevel.keys()).difference(set(LoggingLevel._member_map_.keys()))
        missing_members = [(name, logging._nameToLevel.get(name)) for name in missing_member_names]
        missing_members = sorted(missing_members, key=lambda x: (x[1], x[0]))
        missing_members_string = '\n\t\t'.join(f"(name: {item[0]!r}, value: {item[1]!r})" for item in missing_members)
        msg = f"{LoggingLevel.__name__!r} is missing logging level members ->\n\t\t{missing_members_string}"
        warnings.warn_explicit(message=msg, category=Warning, filename=THIS_FILE_DIR.name, lineno=inspect.findsource(LoggingLevel)[1], module=__name__, module_globals=globals(), source=inspect.getmodule(__name__))


def _align_left(text: str, width: int = 0) -> str:
    return text.ljust(width)


def _align_center(text: str, width: int = 0) -> str:
    return text.center(width)


def _align_right(text: str, width: int = 0) -> str:
    return text.rjust(width)


class LoggingSectionAlignment(Enum):
    LEFT = (_align_left, "<")
    CENTER = (_align_center, "^")
    RIGHT = (_align_right, ">")

    def __init__(self, align_func: Callable[[str, Optional[int]], str], aliases: str = "") -> None:
        self.align_func = align_func
        self.aliases = set(aliases)

    def align(self, text: str, width: int = 0) -> str:
        return self.align_func(text, width)

    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, str):
            mod_value = value.casefold()
            for member in cls.__members__.values():
                if mod_value == member.name.casefold():
                    return member
                if mod_value in member.aliases:
                    return member
        return super()._missing_(value)


class LoggingLevel(int, Enum):
    NOTSET = 0
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    WARN = WARNING
    FATAL = CRITICAL

    def __init__(self, level: int) -> None:
        self.level = level
        if not self.is_alias:
            _add_new_logging_level(self.name, self.level)

    @ property
    def is_alias(self) -> bool:
        return self.name in {"WARN", "FATAL"}

    def __index__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return self.name


_check_if_all_levels_are_in_LoggingLevel()


# region[Main_Exec]
if __name__ == '__main__':
    x = LoggingSectionAlignment("center")
    print('| ' + x.align('this', 2) + ' |')
# endregion[Main_Exec]
