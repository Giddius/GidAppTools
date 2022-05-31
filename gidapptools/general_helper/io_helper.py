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
from dotenv import find_dotenv, load_dotenv
from gidapptools.custom_types import PATH_TYPE
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def amount_lines_in_file(in_file: PATH_TYPE):
    in_file = Path(in_file)
    if in_file.is_file() is False:
        raise FileNotFoundError(f"The path {in_file.as_posix()!r} is not a file.")
    with in_file.open("r", encoding='utf-8', errors='ignore') as f:

        count = sum(1 for _ in f)

    return count


def get_last_line(in_file: PATH_TYPE, decode: bool = True, encoding: str = "utf-8", errors: str = "ignore") -> str:
    in_file = Path(in_file)
    if in_file.is_file() is False:
        raise FileNotFoundError(f"The path {in_file.as_posix()!r} is not a file.")
    with in_file.open('rb') as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        last_line = f.readline()
        if last_line == b"\r\n":
            last_line = b""
        if decode is True:
            last_line = last_line.decode(encoding=encoding, errors=errors)
        return last_line


def escalating_find_file(file_name: str, directory: Union[str, os.PathLike], case_sensitive: bool = False) -> Path:

    def _case_sensitive_compare(in_file_name: str, target_file_name: str) -> bool:
        return in_file_name == target_file_name

    def _case_insensitive_compare(in_file_name: str, target_file_name: str) -> bool:
        return in_file_name.casefold() == target_file_name

    directory = Path(directory).resolve()
    if directory.is_dir() is False:
        raise NotADirectoryError(f"The path {directory.as_posix()!r} is not a directory.")

    compare_func = _case_sensitive_compare

    if case_sensitive is False:
        file_name = file_name.casefold()
        compare_func = _case_insensitive_compare
    for file in directory.iterdir():
        if not file.is_file():
            continue
        if compare_func(file.name, file_name) is True:
            return file.resolve()

    if len(directory.parts) <= 1:
        raise FileNotFoundError(f"Unable to find the file with the name {file_name!r}.")

    return escalating_find_file(file_name=file_name, directory=directory.parent, case_sensitive=case_sensitive)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
