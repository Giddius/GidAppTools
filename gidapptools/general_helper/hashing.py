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
from hashlib import blake2b, md5, sha256, sha512, shake_128, shake_256

if TYPE_CHECKING:
    from gidapptools.types import PATH_TYPE
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


# FILE_HASH_INCREMENTAL_THRESHOLD: int = 104857600  # 100mb
FILE_HASH_INCREMENTAL_THRESHOLD: int = 52428800  # 50mb


def file_hash(in_file: "PATH_TYPE", hash_algo: Callable = blake2b) -> str:
    in_file = Path(in_file)
    if not in_file.is_file():
        raise OSError(f"The path {in_file.as_posix()!r} either does not exist or is a Folder.")
    if in_file.stat().st_size > FILE_HASH_INCREMENTAL_THRESHOLD:
        _hash = hash_algo(usedforsecurity=False)
        with in_file.open("rb", buffering=FILE_HASH_INCREMENTAL_THRESHOLD // 4) as f:
            for chunk in f:
                _hash.update(chunk)
        return _hash.hexdigest()

    return hash_algo(in_file.read_bytes(), usedforsecurity=False).hexdigest()


# region[Main_Exec]

if __name__ == '__main__':
    print(file_hash(Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_Logbook\antistasi_logbook\storage\storage.db")))

# endregion[Main_Exec]
