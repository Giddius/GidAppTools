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
from frozendict import frozendict
from gidapptools.general_helper.conversion import human2bytes
from peewee import JOIN, DatabaseProxy

from sqlite3 import Cursor as SqliteCursor
from playhouse.sqlite_ext import SqliteExtDatabase, CYTHON_SQLITE_EXTENSIONS

if TYPE_CHECKING:
    from gidapptools.custom_types import PATH_TYPE

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
APSW_AVAILABLE = os.getenv("_APSW_AVAILABLE", "0") == "1"


# endregion[Constants]

STD_DEFAULT_PRAGMAS = frozendict({
    "cache_size": -1 * 128000,
    "journal_mode": 'wal',
    "synchronous": 0,
    "ignore_check_constraints": 0,
    "foreign_keys": 1,
    "temp_store": "MEMORY",
    "mmap_size": 268435456 * 8,
    "journal_size_limit": 209_715_200,
    "wal_autocheckpoint": 1000,
    "page_size": 32768 * 2,
    "analysis_limit": 100_000
})

STD_DEFAULT_EXTENSIONS = frozendict({"c_extensions": True,
                                     "rank_functions": True,
                                     "hash_functions": True,
                                     "json_contains": True,
                                     "bloomfilter": True,
                                     "regexp_function": True})


class GidSqliteDatabase(SqliteExtDatabase):
    default_pragmas: Mapping[str, object] = frozendict(**STD_DEFAULT_PRAGMAS)
    default_extensions: Mapping[str, bool] = frozendict(**STD_DEFAULT_EXTENSIONS)
    default_backup_folder_name: str = "backup"

    def __init__(self,
                 database_path: "PATH_TYPE",
                 backup_folder: "PATH_TYPE" = None,
                 thread_safe: bool = True,
                 autoconnect: bool = True,
                 autorollback: bool = None,
                 timeout: int = 100,
                 pragmas: Mapping = None,
                 extensions: Mapping = None):

        self._db_path = Path(database_path).resolve()
        self._backup_folder = Path(backup_folder).resolve() if backup_folder is not None else None
        pragmas = pragmas or {}
        extensions = extensions or {}

        super().__init__(database=self.db_string_path,
                         autoconnect=autoconnect,
                         autorollback=autorollback,
                         thread_safe=thread_safe,
                         timeout=timeout,
                         pragmas=dict(self.default_pragmas | pragmas),
                         **dict(self.default_extensions | extensions))

    @property
    def db_path(self) -> Path:
        return self._db_path

    @property
    def backup_folder(self) -> Path:
        if self._backup_folder is not None:
            backup_folder = self._backup_folder
        else:
            backup_folder = self._get_default_backup_folder()
        backup_folder.mkdir(exist_ok=True, parents=True)
        return backup_folder

    @property
    def db_string_path(self) -> str:
        return os.fspath(self._db_path)

    def _get_default_backup_folder(self) -> Path:
        return self.db_path.parent.joinpath(self.default_backup_folder_name).resolve()

    def _get_backup_name(self) -> str:
        suffix = self.db_path.suffix
        stem = datetime.now().strftime("%Y-%m-%dT%H-%M-%S") + '_' + self.db_path.stem + "_backup"
        return stem + suffix

    def set_backup_folder(self, backup_folder: "PATH_TYPE") -> None:

        if backup_folder is None:
            self._backup_folder = backup_folder
        else:
            backup_folder = Path(backup_folder).resolve()
            if backup_folder.suffix != "":
                raise NotADirectoryError(f"backup_folder {os.fspath(backup_folder)!r} is not a directory")
            self._backup_folder = backup_folder


if APSW_AVAILABLE is True:
    from apsw import SQLITE_OK, SQLITE_CHECKPOINT_TRUNCATE, Connection
    from playhouse.apsw_ext import APSWDatabase

# region[Main_Exec]


if __name__ == '__main__':
    x = GidSqliteDatabase(THIS_FILE_DIR.joinpath("blah.db"))
    print(x._get_backup_name())
# endregion[Main_Exec]
