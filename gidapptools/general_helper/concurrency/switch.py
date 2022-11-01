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
from typing import (TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, ForwardRef, final,
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

from threading import RLock, Lock

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    ...

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class Switch:
    __slots__ = ("_lock", "_state")

    def __init__(self, initial_state: bool = False) -> None:
        self._lock = RLock()
        self._state = initial_state

    @property
    def state(self) -> bool:
        with self._lock:
            return self._state

    @property
    def is_true(self) -> bool:
        with self._lock:
            return self.state is True

    @property
    def is_false(self) -> bool:
        with self._lock:
            return self.state is False

    def switch_to(self, new_state: bool) -> None:
        with self._lock:
            self._state = new_state

    def switch(self) -> bool:
        with self._lock:
            self.switch_to(not self.state)
            return self.state

    def __bool__(self) -> bool:
        return self.state

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.state!r})"

# region[Main_Exec]


if __name__ == '__main__':
    pass


# endregion[Main_Exec]
