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


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class Color:

    def __init__(self, values: Iterable[float], name: str = None) -> None:
        self._values = tuple(values)
        self._name = name
        self._red: float = self._values[0]
        self._green: float = self._values[1]
        self._blue: float = self._values[2]
        self._alpha: float = self._values[3]

    @property
    def values(self) -> tuple[float]:
        return self._values

    @property
    def name(self) -> str:
        return self._name

    @property
    def red(self) -> float:
        return self._red

    @property
    def green(self) -> float:
        return self._green

    @property
    def blue(self) -> float:
        return self._blue

    @property
    def alpha(self) -> float:
        return self._alpha

    def with_alpha(self, new_alpha: float, new_name: str = None) -> "Color":
        new_values = (self.red, self.green, self.blue, new_alpha)
        return self.__class__(new_values, name=new_name)

    def with_red(self, new_red: float, new_name: str = None) -> "Color":
        new_values = (new_red, self.green, self.blue, self.alpha)
        return self.__class__(new_values, name=new_name)

    def with_green(self, new_green: float, new_name: str = None) -> "Color":
        new_values = (self.red, new_green, self.blue, self.alpha)
        return self.__class__(new_values, name=new_name)

    def with_blue(self, new_blue: float, new_name: str = None) -> "Color":
        new_values = (self.red, self.green, new_blue, self.alpha)
        return self.__class__(new_values, name=new_name)

    def to_int_rgba(self) -> tuple(int):
        ...

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(values={self.values!r}, name={self.name!r})'
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
