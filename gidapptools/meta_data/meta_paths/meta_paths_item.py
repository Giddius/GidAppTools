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

import random

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
from enum import Enum, Flag, auto
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, NoReturn
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory, mkdtemp, gettempdir
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from itertools import product, combinations
import attr
import requests
from yarl import URL
from tzlocal import get_localzone
from gidapptools.utility.enums import OperatingSystem, NamedMetaPath
from gidapptools.utility.helper import memory_in_use, handle_path, utc_now, PathLibAppDirs, mark_appdir_path, make_pretty
from gidapptools.general_helper.date_time import DatetimeFmt
from gidapptools.types import PATH_TYPE
from appdirs import AppDirs, user_data_dir, user_config_dir, user_cache_dir, user_log_dir
import orjson
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem
# REMOVE_BEFORE_BUILDING_DIST
from gidapptools.utility._debug_tools import dprint

print = dprint

# end REMOVE_BEFORE_BUILDING_DIST

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MetaPaths(AbstractMetaItem):

    def __init__(self, code_base_dir: Path, paths: dict[NamedMetaPath, Path]) -> None:
        self.code_base_dir = Path(code_base_dir).resolve()
        self._paths: dict[Union[NamedMetaPath, str], Optional[Path]] = paths
        self._created_normal_paths: set[Path] = set()
        self._created_temp_dirs: set[Path] = set()

    def get_path(self, identifier: Union[NamedMetaPath, str], default: Any = NotImplemented) -> Path:
        if isinstance(identifier, str):
            try:
                identifier = NamedMetaPath(identifier)
            except ValueError:
                pass
        path = self._paths.get(identifier, None)
        if path is None:
            return default

        if path.exists() is False:
            path.mkdir(parents=True, exist_ok=True)
            self._created_normal_paths.add(path)
        return path

    @property
    def data_dir(self) -> Path:
        return self.get_path(NamedMetaPath.DATA)

    @property
    def cache_dir(self) -> Path:
        return self.get_path(NamedMetaPath.CACHE)

    @property
    def temp_dir(self) -> Path:
        return self.get_path(NamedMetaPath.TEMP)

    @property
    def log_dir(self) -> Path:
        return self.get_path(NamedMetaPath.LOG)

    @property
    def config_dir(self) -> Path:
        return self.get_path(NamedMetaPath.CONFIG)

    @property
    def config_spec_dir(self) -> Path:
        return self.get_path(NamedMetaPath.CONFIG_SPEC)

    @property
    def db_dir(self) -> Path:
        return self.get_path(NamedMetaPath.DB)

    def get_new_temp_dir(self, suffix: str = None) -> Path:
        temp_dir = Path(mkdtemp(dir=self.temp_dir, suffix=suffix))
        if temp_dir.exists() is False:
            temp_dir.mkdir(parents=True, exist_ok=True)
        self._created_temp_dirs.add(temp_dir)
        return temp_dir

    @contextmanager
    def context_new_temp_dir(self, suffix: str = None):
        temp_dir = self.get_new_temp_dir(suffix=suffix)
        yield temp_dir
        shutil.rmtree(temp_dir)

    def clean_all_temp(self) -> None:
        while len(self._created_temp_dirs) != 0:
            temp_dir = self._created_temp_dirs.pop()
            shutil.rmtree(temp_dir)

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:

        _out = vars(self)
        if pretty is True:
            _out = make_pretty(self)

        return pformat(_out)

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    def clean_up(self, remove_all_paths: bool = False, **kwargs) -> None:
        self.clean_all_temp()
        if remove_all_paths is True:
            for path in self._created_normal_paths:
                if path.exists():
                    if kwargs.get('dry_run', False) is True:
                        print(f"Simulating deleting of path {path.as_posix()!r}, with 'shutil.rmtree'.")
                    else:
                        shutil.rmtree(path)
        # TODO: find a way to clean shit up, but completely, also add optional kwarg that also removes the author folder


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
