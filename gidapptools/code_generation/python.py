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
import ast
import textwrap
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

check_sample = '''
class ConsoleColors:
    """
    ANSI color codes
    based on: https://gist.github.com/rene-d/9e584a7dd2935d0f461904b9f2950007
    """

    def __init__(self):
        self._is_atty: bool = sys.stdout.isatty()
        self._is_windows: bool = platform.system().casefold() == "windows"

        self._BLACK = "\033[0;30m" if self.is_applicable else ""
        self._RED = "\033[0;31m" if self.is_applicable else ""
        self._GREEN = "\033[0;32m" if self.is_applicable else ""
        self._BROWN = "\033[0;33m" if self.is_applicable else ""
        self._BLUE = "\033[0;34m" if self.is_applicable else ""
        self._PURPLE = "\033[0;35m" if self.is_applicable else ""
        self._CYAN = "\033[0;36m" if self.is_applicable else ""
        self._LIGHT_GRAY = "\033[0;37m" if self.is_applicable else ""
        self._DARK_GRAY = "\033[1;30m" if self.is_applicable else ""
        self._LIGHT_RED = "\033[1;31m" if self.is_applicable else ""
        self._LIGHT_GREEN = "\033[1;32m" if self.is_applicable else ""
        self._YELLOW = "\033[1;33m" if self.is_applicable else ""
        self._LIGHT_BLUE = "\033[1;34m" if self.is_applicable else ""
        self._LIGHT_PURPLE = "\033[1;35m" if self.is_applicable else ""
        self._LIGHT_CYAN = "\033[1;36m" if self.is_applicable else ""
        self._LIGHT_WHITE = "\033[1;37m" if self.is_applicable else ""
        self._WHITE = "\033[97m" if self.is_applicable else ""
        self._BOLD = "\033[1m" if self.is_applicable else ""
        self._FAINT = "\033[2m" if self.is_applicable else ""
        self._ITALIC = "\033[3m" if self.is_applicable else ""
        self._UNDERLINE = "\033[4m" if self.is_applicable else ""
        self._BLINK = "\033[5m" if self.is_applicable else ""
        self._NEGATIVE = "\033[7m" if self.is_applicable else ""
        self._CROSSED = "\033[9m" if self.is_applicable else ""
        self._RESET = "\033[0m" if self.is_applicable else ""


'''


PROP_TEMPLATE = textwrap.indent('''
@property
def {prop_name}(self):
    return self.{attr_name}

'''.strip(), "    ")


def _get_attribute_names(in_source_code: str) -> tuple[str]:

    class _CustomVisitor(ast.NodeVisitor):

        def __init__(self):
            self._found_names: list[str] = []

        def visit_Assign(self, node: ast.Assign) -> Any:

            self._found_names.append(node.targets[0].attr)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
            self._found_names.append(node.target.attr)

        def get_found_names(self) -> tuple[str]:
            return tuple(self._found_names)

    ast_tree = ast.parse(in_source_code)
    visitor = _CustomVisitor()
    visitor.visit(ast_tree)

    return visitor.get_found_names()

    # print(ast.dump(ast_tree, indent=4))

    # THIS_FILE_DIR.joinpath("blah.txt").write_text(ast.dump(ast_tree, indent=4), encoding='utf-8', errors='ignore')
# region [Main_Exec]


if __name__ == '__main__':
    for _name in _get_attribute_names(check_sample):
        prop_name = _name.removeprefix("_")

        prop_text = PROP_TEMPLATE.format(prop_name=prop_name, attr_name=_name)
        print(prop_text + "\n\n")
# endregion [Main_Exec]
