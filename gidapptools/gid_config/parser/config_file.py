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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Literal, TypeVar, TypedDict
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
from hashlib import blake2b
from gidapptools.gid_config.parser.ini_parser import SimpleIniParser
from threading import Lock
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

CONFIG_SPEC_DATA_TYPE = dict[str, dict[str, Union[Any, None]]]


class ConfigFileTypus(Enum):
    INI = '.ini'
    JSON = '.json'


class ConfigFile:

    def __init__(self,
                 file_path: Path,
                 changed_parameter: Union[Literal['size'], Literal['file_hash']] = 'size',
                 parser: SimpleIniParser = None,
                 spec_data: CONFIG_SPEC_DATA_TYPE = None,
                 **kwargs) -> None:
        self.file_path = Path(file_path).resolve()
        self.config_typus = ConfigFileTypus(self.file_path.suffix)
        self.changed_parameter = changed_parameter
        self.parser = SimpleIniParser(**kwargs) if parser is None else parser(**kwargs)
        self.spec = {} if spec_data is None else spec_data
        self._size: int = None
        self._file_hash: str = None
        self._content: Mapping[str, Any] = None
        self.lock = Lock()

    @property
    def content(self) -> Mapping[str, Any]:
        with self.lock:
            if self._content is None or self.has_changed is True:
                self.load()
            return self._content

    @property
    def size(self) -> int:
        return self.file_path.stat().st_size

    @property
    def file_hash(self) -> str:
        _file_hash = blake2b()
        with self.file_path.open('rb') as f:
            for chunk in f:
                _file_hash.update(chunk)
        return _file_hash.hexdigest()

    @property
    def has_changed(self) -> bool:
        if self.changed_parameter == 'size':
            if self._size is None or self.size != self._size:
                return True
        elif self.changed_parameter == 'file_hash':
            if self._file_hash is None or self.file_hash != self._file_hash:
                return True
        return False

    def load(self) -> None:
        self._content = self.parser.parse(self.file_path)
        self._size = self.size
        self._file_hash = self.file_hash

    def write(self) -> None:
        with self.lock:
            with self.file_path.open('w', encoding='utf-8', errors='ignore') as f:
                header_comment = self.spec.get('header')
                if header_comment:
                    for line in header_comment.splitlines():
                        f.write(f"# {line}\n")
                    f.write("\n\n\n")
                for section, values in self._content.items():
                    section_comments = self.spec.get(section, {}).get('comments', [])
                    for comment in section_comments:
                        f.write(f"# {comment}\n")
                    f.write(f"[{section}]\n\n")
                    for key, value in values.items():
                        key_comments = self.spec.get(section, {}).get(key, {}).get('comments', [])
                        for comment in key_comments:
                            f.write(f"# {comment}\n")
                        f.write(f"{key} = {value}\n")
                    f.write('\n\n')
            self.load()


# region[Main_Exec]
if __name__ == '__main__':
    x = ConfigFile(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Gid_Scratches\gid_scratch\check_w_comments.ini", spec_data={"header": "this is a header", 'general_settings': {'comments': ["this is a comment for the section"]}})
    print(x.content)
    print(x.file_hash)
    print(x.size)
    print(x.config_typus)
    x._content['this'] = {'that': 17}
    x.write()

# endregion[Main_Exec]
