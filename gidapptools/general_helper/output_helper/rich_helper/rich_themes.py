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
from typing import (TYPE_CHECKING, Mapping, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, ForwardRef, final, Callable,
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

from rich.console import Console as RichConsole
from rich.theme import Theme
from rich.style import Style, StyleType
from rich.table import Table

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


# from typing import is_typeddict
from inspect import iscoroutine, isasyncgen, isawaitable, isc
from asyncio import iscoroutine, isawaitable
if TYPE_CHECKING:
    ...

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class GidTheme(Theme):

    def __init__(self,
                 name: str = None,
                 extra_styles: Mapping[str, StyleType] | None = None):

        self._name = name or self.__class__.__name__
        self._extra_styles = extra_styles or {}
        super().__init__(self._generate_styles(), inherit=True)

    @property
    def name(self) -> str:
        return self._name

    def _generate_styles(self) -> dict[str, StyleType]:
        _out = {}

        return _out | self._extra_styles

    @property
    def config_table(self) -> Table:
        table = Table("Style-name", "Style-value",
                      title=self.name,
                      row_styles=["on grey11", "on grey15"])

        for style_name, style_value in sorted(self.styles.items()):
            table.add_row(style_name, f"[{style_value}]'{style_value!s}'[/{style_value}]")

        return table

# region [Main_Exec]


if __name__ == '__main__':
    x = RichConsole(soft_wrap=True, theme=GidTheme())
    from rich.text import Text
    from rich.syntax import Syntax, PygmentsSyntaxTheme
    from rich.panel import Panel

    with THIS_FILE_DIR.joinpath("rich_helper.py").open("r", encoding='utf-8', errors='ignore') as f:
        t = Syntax(f.read(), "python", theme=PygmentsSyntaxTheme("dracula"), line_numbers=True, background_color="black", indent_guides=True)
    p = Panel(t)
    x.print(p)
# endregion [Main_Exec]
