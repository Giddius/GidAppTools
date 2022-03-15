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

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]
APSW_AVAILABLE = os.getenv("_APSW_AVAILABLE", "0") == "1"
THIS_FILE_DIR = Path(__file__).parent.absolute()

if APSW_AVAILABLE:
    from apsw import SQLITE_OK, SQLITE_CHECKPOINT_TRUNCATE, Connection
    from playhouse.apsw_ext import APSWDatabase
    DB_BASE_CLASS = APSWDatabase
else:
    from playhouse.sqlite_ext import SqliteExtDatabase
    DB_BASE_CLASS = SqliteExtDatabase
# endregion[Constants]

DEFAULT_PRAGMAS = frozendict({
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
    "analysis_limit": 100000
})


class GidSqliteDatabase(DB_BASE_CLASS):

    def __init__(self, database, **kwargs):
        super().__init__(database, **kwargs)

# region[Main_Exec]


if __name__ == '__main__':
    print(dict(DEFAULT_PRAGMAS | {"a": 3}))

# endregion[Main_Exec]
