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
import atexit
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
from typing import TYPE_CHECKING, Union, TypeVar, ParamSpec, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr
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
import queue
from threading import Lock, RLock, Condition, Event, Semaphore, BoundedSemaphore, Barrier
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]
log = logging.getLogger(__name__)
THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AbstractThreadsafePool(ABC):
    __slots__ = ("_lock", "_max_size", "_prefill", "_objects", "_queue")

    def __init__(self, max_size: int = None, prefill: bool = False) -> None:
        self._lock = Lock()
        self._max_size: int = max_size or 10
        self._prefill = prefill
        self._objects: list[object] = []
        self._queue = queue.Queue(maxsize=self._max_size)
        if self._prefill is True:
            while True:
                created = self._create_if_possible()
                if created is False:
                    break

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def amount_objects(self) -> int:
        return len(self._objects)

    @abstractmethod
    def _create_new_object(self) -> object:
        ...

    def _create_if_possible(self) -> bool:
        if self.amount_objects >= self.max_size:
            return False
        new_object = self._create_new_object()
        self._objects.append(new_object)
        self._queue.put_nowait(new_object)
        return True

    def _get_object(self) -> object:
        with self._lock:
            try:
                return self._queue.get_nowait()
            except queue.Empty:
                self._create_if_possible()
                return self._queue.get(block=True)

    @contextmanager
    def __call__(self) -> Any:
        obj = self._get_object()

        yield obj

        self._queue.put_nowait(obj)
        self._queue.task_done()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(max_size={self.max_size!r}, prefill={self._prefill!r})'


class GenericThreadsafePool(AbstractThreadsafePool):
    __slots__ = ("_obj_creator",)

    def __init__(self, obj_creator: Callable, max_size: int = 0, prefill: bool = False) -> None:
        self._obj_creator = obj_creator
        super().__init__(max_size=max_size, prefill=prefill)

    def _create_new_object(self) -> object:

        return self._obj_creator()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(obj_creator={self._obj_creator!r}, max_size={self.max_size!r}, prefill={self._prefill!r})'


T = TypeVar('T')


class DecorateAbleList(list):

    def decorate_append(self, item: T) -> T:
        self.append(item)
        return item

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
