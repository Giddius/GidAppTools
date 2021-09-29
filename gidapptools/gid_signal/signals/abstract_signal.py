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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr, cast
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
from weakref import WeakSet, WeakMethod, ref
from gidapptools.utility.helper import get_qualname_or_name
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AdaptableWeakSet(WeakSet):

    def add(self, item) -> None:
        if self._pending_removals:
            self._commit_removals()
        if inspect.ismethod(item):
            ref_item = WeakMethod(item, self._remove)
        else:
            ref_item = ref(item, self._remove)
        self.data.add(ref_item)

    def __bool__(self) -> bool:
        return self.data is not None and len(self.data) > 0


class AbstractSignal(ABC):

    def __init__(self, name: str, allow_sync_targets: bool = True, allow_async_target: bool = True) -> None:
        self.name = name
        self.allow_sync_targets = allow_sync_targets
        self.allow_async_targets = allow_async_target
        if self.allow_async_targets is False and self.allow_async_targets is False:
            raise AttributeError('A signal cannot have both SYNC and ASYNC targets disabled.')
        self.targets = AdaptableWeakSet()
        self.targets_info: dict[str, dict[str:Any]] = {}

    def _add_target_info(self, target: Callable) -> None:
        info = {'is_coroutine': asyncio.iscoroutine(target)}
        name = get_qualname_or_name(target)
        self.targets_info[name] = info

    def _verify(self, target: Callable) -> None:
        target_is_coroutine = asyncio.iscoroutine(target)
        if target_is_coroutine is True and self.allow_async_targets is False:
            raise TypeError('Signal is set to only allow SYNC targets.')
        if target_is_coroutine is False and self.allow_sync_targets is False:
            raise TypeError('Signal is set to only allow ASYNC targets.')

    def connect(self, target: Callable) -> None:
        self._verify(target)
        self._add_target_info(target)
        self.targets.add(target)

    def disconnect(self, target: Callable) -> None:
        name = get_qualname_or_name(target)
        self.targets.discard(target)
        self.targets_info.pop(name)

    @abstractmethod
    def emit(self, *args, **kwargs):
        ...

    @abstractmethod
    async def aemit(self, *args, **kwargs):
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name}(targets={self.targets!r})"


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
