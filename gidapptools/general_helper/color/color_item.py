"""
WiP.

Soon.
"""

# region [Imports]

import gc
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
import unicodedata
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

import attr
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

INT_OR_FLOAT = Union[int, float]


def _validate_rgba_float(instance: object, attribute: attr.Attribute, value: Optional[float]) -> None:
    if 0.0 > value > 1.0:
        raise ValueError(f"{attribute.name!r}-value can only be between 0 and 1, not {value!r}.")


@attr.s(auto_attribs=True, auto_detect=True, slots=True, weakref_slot=True, frozen=True)
class Color:
    red: float = attr.ib(validator=_validate_rgba_float)
    green: float = attr.ib(validator=_validate_rgba_float)
    blue: float = attr.ib(validator=_validate_rgba_float)
    alpha: float = attr.ib(default=1, validator=_validate_rgba_float)

    def as_tuple(self, exclude_alpha: bool = False) -> tuple[float, float, float, float]:
        _out = [self.red, self.green, self.blue]
        if exclude_alpha is False:
            _out.append(self.alpha)
        return tuple(_out)

    @property
    def has_alpha(self) -> bool:
        return self.alpha is not None

    def to_rgb(self, rounded: bool = False) -> tuple[INT_OR_FLOAT, INT_OR_FLOAT, INT_OR_FLOAT]:
        _out = [sub_col * 255 for sub_col in self.as_tuple(exclude_alpha=True)]
        if rounded is True:
            _out = [round(part) for part in _out]
        return tuple(_out)

    def to_rgba(self, rounded: bool = False) -> tuple[INT_OR_FLOAT, INT_OR_FLOAT, INT_OR_FLOAT, float]:
        _out = [sub_col * 255 for sub_col in self.as_tuple(exclude_alpha=True)]
        if rounded is True:
            _out = [round(part) for part in _out]
        _out.append(self.alpha)
        return tuple(_out)


        # region[Main_Exec]
if __name__ == '__main__':
    x = Color(0.5, 1, 0.3, 0.2)
    print(x.to_rgb_256(True))

# endregion[Main_Exec]
