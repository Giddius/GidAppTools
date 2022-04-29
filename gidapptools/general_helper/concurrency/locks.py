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
import pp
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
from threading import RLock, Lock, Semaphore, Event, Condition, Barrier, Thread, Timer
import gc

from gidapptools.custom_types import PATH_TYPE, LOCK_TYPE
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class FileLocksManager:

    def __init__(self, lock_type: LOCK_TYPE):
        self._lock_type = lock_type
        self._interaction_lock: Lock = Lock()
        self._file_locks: dict[Path, LOCK_TYPE] = {}

    def _handle_file_path(self, file_path: PATH_TYPE) -> Path:
        return Path(file_path).resolve()

    def _get_or_create(self, file_path: PATH_TYPE) -> LOCK_TYPE:
        file_path = self._handle_file_path(file_path=file_path)
        with self._interaction_lock:
            try:
                return self._file_locks[file_path]
            except KeyError:
                file_lock = self._lock_type()
                self._file_locks[file_path] = file_lock
                return file_lock

    def get_file_lock(self, file_path: PATH_TYPE) -> LOCK_TYPE:
        return self._get_or_create(file_path=file_path)

    def __getitem__(self, file_path: PATH_TYPE) -> LOCK_TYPE:
        return self.get_file_lock(file_path=file_path)

    def __len__(self) -> int:
        with self._interaction_lock:
            return len(self._file_locks)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lock_type={self._lock_type!r})"


GLOBAL_LOCK_MANAGER = FileLocksManager(Lock)
GLOBAL_RLOCK_MANAGER = FileLocksManager(RLock)

# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
