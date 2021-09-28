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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, ClassVar
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
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
import importlib.metadata
from psutil import virtual_memory
from itertools import cycle
from gidapptools.errors import NotBaseInitFileError
from urlextract import URLExtract
import attr
import requests
from yarl import URL
from tzlocal import get_localzone
from gidapptools.utility.enums import OperatingSystem
from gidapptools.utility.helper import memory_in_use, handle_path, utc_now, make_pretty
from gidapptools.general_helper.conversion import bytes2human
from gidapptools.general_helper.date_time import DatetimeFmt
from gidapptools.types import PATH_TYPE
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem
# REMOVE_BEFORE_BUILDING_DIST
from gidapptools.utility._debug_tools import dprint

print = dprint

# end REMOVE_BEFORE_BUILDING_DIST


# endregion[Imports]

# region [TODO]

# - Make into a class

# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

def url_converter(in_url: str) -> Optional[URL]:
    if in_url is None:
        return in_url
    return URL(in_url)


@attr.s(auto_attribs=True, auto_detect=True, kw_only=True, frozen=True)
class MetaInfo(AbstractMetaItem):
    app_name: str = attr.ib(default=None)
    app_author: str = attr.ib(default=None)
    version: str = attr.ib(default=None)
    url: URL = attr.ib(converter=url_converter, default=None)
    pid: int = attr.ib(factory=os.getpid)
    os: OperatingSystem = attr.ib(factory=OperatingSystem.determine_operating_system)
    os_release: str = attr.ib(factory=platform.release)
    python_version: str = attr.ib(factory=platform.python_version)
    started_at: datetime = attr.ib(factory=utc_now)
    base_mem_use: int = attr.ib(default=memory_in_use())
    is_dev: bool = attr.ib(default=False)
    is_gui: bool = attr.ib(default=False)

    @property
    def pretty_base_mem_use(self) -> str:
        return bytes2human(self.base_mem_use)

    @property
    def pretty_started_at(self) -> str:
        return DatetimeFmt.STANDARD.strf(self.started_at)

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:

        if pretty is True:
            return make_pretty(self)
        return attr.asdict(self)

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    def clean_up(self, **kwargs) -> None:
        pass

    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
