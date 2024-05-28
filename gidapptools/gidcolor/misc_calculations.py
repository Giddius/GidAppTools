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

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


_RGB_FLOAT_TUPLE_TYPE: TypeAlias = Union[tuple[float, float, float], tuple[float, float, float, float]]


def calculate_luminace(value: float) -> float:

    if value < 0.03928:
        return value / 12.92
    else:
        return ((value + 0.055) / 1.055) ** 2.4


def calculate_relative_luminance(r: float, g: float, b: float) -> float:
    return 0.2126 * calculate_luminace(r) + 0.7152 * calculate_luminace(g) + 0.0722 * calculate_luminace(b)


def calculate_contrast_ratio(rgb_first: _RGB_FLOAT_TUPLE_TYPE, rgb_second: _RGB_FLOAT_TUPLE_TYPE) -> float:
    """
    see `https://www.w3.org/TR/2008/REC-WCAG20-20081211/`

    Between 1.0 and 21.0, higher is better constrast.

    Args:
        rgb_first (_RGB_FLOAT_TUPLE_TYPE): _description_
        rgb_second (_RGB_FLOAT_TUPLE_TYPE): _description_

    Returns:
        float: _description_
    """

    def _split_off_alpha(in_color: _RGB_FLOAT_TUPLE_TYPE) -> tuple[tuple[float, float, float], float]:
        col_values = in_color[:3]
        try:
            col_alpha = in_color[3]
        except IndexError:
            col_alpha = 1.0

        return col_values, col_alpha

    dark, light = sorted([rgb_first, rgb_second], key=lambda x: sum(x[:3]))

    light_luminance = calculate_relative_luminance(*light[:3])
    dark_luminance = calculate_relative_luminance(*dark[:3])
    contrast_ratio = (light_luminance + 0.05) / (dark_luminance + 0.05)

    if contrast_ratio < 0:
        contrast_ratio = (dark_luminance + 0.05) / (light_luminance + 0.05)

    return round(contrast_ratio, ndigits=3)

# region [Main_Exec]


if __name__ == '__main__':
    ...
# endregion [Main_Exec]
