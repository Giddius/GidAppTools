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
from gidapptools.general_helper.timing import time_func
from tzlocal import get_localzone
from dateutil.tz import UTC
from gidapptools.general_helper.string_helper import StringCaseConverter, StringCase
from gidapptools.gid_logger.enums import LoggingLevel, LoggingSectionAlignment
if TYPE_CHECKING:
    from gidapptools.gid_logger.records import LOG_RECORD_TYPES
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AbstractLoggingStyleSection:
    default_alignment: LoggingSectionAlignment = LoggingSectionAlignment.LEFT
    default_width: int = 0

    def __init__(self,
                 position: int = None,
                 width: int = None,
                 alignment: Union[LoggingSectionAlignment, str] = None) -> None:
        self.position = position
        self.width = width or self.default_width
        if alignment is None:
            self.alignment = self.default_alignment
        elif isinstance(alignment, str):
            self.alignment = LoggingSectionAlignment(alignment)
        else:
            self.alignment = alignment

    @abstractmethod
    def get_formated_value(self, record: "LOG_RECORD_TYPES") -> str:
        ...

    def align(self, text: str) -> str:
        return self.alignment.align(text, self.width)

    def format(self, record: "LOG_RECORD_TYPES") -> str:
        text = str(self.get_formated_value(record=record))
        return self.align(text)

    @classmethod
    def ___section_name___(cls) -> str:
        return StringCaseConverter.convert_to(cls.__name__.removesuffix("Section"), StringCase.SNAKE)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(position={self.position!r})"


class TimeSection(AbstractLoggingStyleSection):

    local_timezone: timezone = get_localzone()
    default_time_format = '%Y-%m-%d %H:%M:%S'
    default_msec_format = '.{msec:03.0f}'
    default_alignment: LoggingSectionAlignment = LoggingSectionAlignment.LEFT

    def __init__(self,
                 position: int = None,
                 time_zone: timezone = None,
                 time_format: str = None,
                 msec_format: str = None,
                 width: int = None,
                 alignment: Union[LoggingSectionAlignment, str] = None) -> None:
        super().__init__(position=position, alignment=alignment)

        self.time_zone = time_zone
        self.time_format = time_format or self.default_time_format
        self.msec_format = msec_format or self.default_msec_format
        self.width = width or (len(self.time_format) + len(self.msec_format.format(msec=0)) + 2)

    def get_formated_value(self, record: "LOG_RECORD_TYPES") -> str:
        time_value = datetime.fromtimestamp(record.created, tz=self.local_timezone)
        if self.time_zone is not None:
            time_value = time_value.replace(tzinfo=self.time_zone)
        if self.time_format.casefold() == "isoformat":
            return time_value.isoformat(timespec='seconds') + self.msec_format.format(msec=record.msecs)
        return time_value.strftime(self.time_format) + self.msec_format.format(msec=record.msecs)


class LevelSection(AbstractLoggingStyleSection):
    default_case: StringCase = StringCase.UPPER
    default_alignment: LoggingSectionAlignment = LoggingSectionAlignment.CENTER
    default_width: int = 6

    def __init__(self,
                 position: int = None,
                 case: StringCase = None,
                 width: int = None,
                 alignment: Union[LoggingSectionAlignment, str] = None) -> None:
        super().__init__(position=position, alignment=alignment, width=width)
        if case is None:
            self.case = self.default_case
        elif isinstance(case, str):
            self.case = StringCase(case)
        else:
            self.case = case

    def get_formated_value(self, record: "LOG_RECORD_TYPES") -> str:
        return StringCaseConverter.convert_to(record.levelname, self.case)


class ThreadSection(AbstractLoggingStyleSection):
    default_alignment: LoggingSectionAlignment = LoggingSectionAlignment.CENTER

    def get_formated_value(self, record: "LOG_RECORD_TYPES") -> str:
        return record.threadName


class LineNumberSection(AbstractLoggingStyleSection):
    default_alignment: LoggingSectionAlignment = LoggingSectionAlignment.CENTER
    default_width: int = 5

    def get_formated_value(self, record: "LOG_RECORD_TYPES") -> str:
        return record.lineno


class PathSection(AbstractLoggingStyleSection):
    default_alignment: LoggingSectionAlignment = LoggingSectionAlignment.LEFT

    def __init__(self, position: int = None,
                 depth: int = 2,
                 with_extension: bool = False,
                 width: int = None,
                 alignment: Union[LoggingSectionAlignment, str] = None) -> None:
        super().__init__(position=position, width=width, alignment=alignment)
        self.with_extension = with_extension
        self.depth = depth

    def get_formated_value(self, record: "LOG_RECORD_TYPES") -> str:
        path, extension = record.pathname.rsplit('.', 1)
        _out = '/'.join(part for part in path.split('/')[-self.depth:])
        if self.with_extension is True:
            return _out + '.' + extension
        return _out


class FunctionNameSection(AbstractLoggingStyleSection):
    default_alignment: LoggingSectionAlignment = LoggingSectionAlignment.LEFT

    def get_formated_value(self, record: "LOG_RECORD_TYPES") -> str:
        return record.funcName


class AbstractSectionLoggingStyle(ABC):
    default_separator: str = " | "
    default_message_start_indicator: str = ' ||--> '

    def __init__(self, sections: Iterable[Union[str, Any]], separator: str = None, message_start_indicator: str = None, message_section: AbstractLoggingStyleSection = None):
        self.sections = sections
        self.sorted_sections: tuple[AbstractLoggingStyleSection] = self.sort_sections()
        self.separator = separator or self.default_separator
        self.message_start_indicator = message_start_indicator or self.default_message_start_indicator
        self.message_section = message_section

    def sort_sections(self) -> tuple[AbstractLoggingStyleSection]:
        temp_sorted = [i[0] for i in sorted([(v, idx) for idx, v in enumerate(self.sections)], key=lambda x: (x[0].position, x[1]))]
        for idx, sect in enumerate(temp_sorted):
            if sect.position is None:
                sect.position = idx
        return tuple(temp_sorted)

    def usesTime(self) -> bool:
        return False

    @abstractmethod
    def validate(self) -> None:
        ...

    @abstractmethod
    def _format(self, record: "LOG_RECORD_TYPES") -> str:
        ...

    def format(self, record: "LOG_RECORD_TYPES"):
        try:
            return self._format(record)
        except KeyError as e:
            raise ValueError(f'Formatting field not found in record: {e}') from e


class GidSectionLoggingStyle(AbstractSectionLoggingStyle):

    def validate(self) -> None:
        if any(isinstance(i, AbstractLoggingStyleSection) is False for i in self.sections):
            raise ValueError("invalid format")

    @time_func(condition=True)
    def _format(self, record: "LOG_RECORD_TYPES") -> str:

        message_part = record.getMessage() if self.message_section is None else self.message_section.format(record)

        return self.separator.join(section.format(record) for section in self.sorted_sections) + self.message_start_indicator + message_part


class GidLoggingFormatter(logging.Formatter):
    ...


# region[Main_Exec]

class RR:
    def __init__(self) -> None:
        self.created = time()
        self.msecs = 203
        self.threadName = None
        self.lineno = 20
        self.pathname = Path(__file__).resolve().as_posix()
        self.funcName = "wuff"

    def getMessage(self) -> str:
        return "no message"


if __name__ == '__main__':
    sections = [TimeSection(), ThreadSection(), LineNumberSection(), PathSection(), FunctionNameSection()]
    x = GidSectionLoggingStyle(sections=sections)

    for y in range(100):
        x.format(RR())
# endregion[Main_Exec]
