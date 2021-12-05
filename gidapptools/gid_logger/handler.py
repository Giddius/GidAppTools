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
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.conversion import human2bytes
from logging.handlers import RotatingFileHandler, BaseRotatingHandler, BufferingHandler
from threading import RLock, Lock
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


DEFAULT_MAX_BYTES = human2bytes("5 mb")


class _DefaultFileNameTemplate:

    def __init__(self, base_name: str) -> None:
        self.base_name = base_name
        self.backup_file_name_regex = re.compile(rf"{self.base_name}.log\_\d+", re.IGNORECASE)

    def format(self, **kwargs) -> str:
        return "{base_name}.log".format(base_name=self.base_name, **kwargs)

    def is_same_kind_log_file(self, other_file: Path) -> bool:
        return other_file.name.casefold() == "{base_name}.log".format(base_name=self.base_name).casefold()

    def is_backup_log_file(self, other_file: Path) -> bool:
        return self.backup_file_name_regex.match(other_file.name) is not None


class GidBaseRotatingFileHandler(BaseRotatingHandler):

    def __init__(self,
                 base_name: str,
                 log_folder: "PATH_TYPE",
                 file_name_template: Union[str, Any] = None,
                 backup_folder: "PATH_TYPE" = MiscEnum.AUTO,
                 rotate_on_start: bool = True,
                 backup_amount_limit: int = 3) -> None:
        self.base_name = base_name
        self.file_name_template = _DefaultFileNameTemplate(self.base_name) if file_name_template is None else file_name_template
        self.log_folder = Path(log_folder)
        self.backup_folder = self.log_folder.joinpath("old_logs") if backup_folder is MiscEnum.AUTO else Path(backup_folder)
        self.rotate_on_start = rotate_on_start
        self.backup_amount_limit = backup_amount_limit
        self.full_file_path: Path = self._construct_full_file_path()
        self.first_record_emited: bool = False
        super().__init__(self.full_file_path, "a", encoding="utf-8", delay=True, errors="ignore")

    def emit(self, record) -> None:
        with self.lock:
            if self.first_record_emited is False:
                self.on_start_rotation()
                self.first_record_emited = True

        return super().emit(record)

    def _construct_full_file_path(self) -> Path:
        name = self.file_name_template.format(number=0)
        full_path = self.log_folder.joinpath(name)

        return full_path

    def _get_old_logs(self) -> tuple[Path]:
        def _is_old_log(_in_file: Path) -> bool:
            return _in_file.is_file() and self.file_name_template.is_same_kind_log_file(_in_file)

        _out = tuple(file for file in tuple(self.log_folder.iterdir()) if _is_old_log(file) is True)

        return _out

    def _get_backup_logs(self) -> list[Path]:
        if self.backup_folder.exists() is False:
            return []

        def _is_old_backup(_in_file: Path) -> bool:
            return _in_file.is_file() and self.file_name_template.is_backup_log_file(_in_file)

        _out = sorted((file for file in self.backup_folder.iterdir() if _is_old_backup(file)), key=lambda x: x.stat().st_mtime)
        return _out

    def on_start_rotation(self) -> None:
        try:
            self.acquire()
            self.full_file_path.parent.mkdir(exist_ok=True, parents=True)
            for file in self._get_old_logs():
                self.move_file_to_backup_folder(file)
            self.remove_excess_backup_files()
        finally:
            self.release()

    def remove_excess_backup_files(self) -> None:
        if self.backup_amount_limit is None:
            return
        backup_logs = self._get_backup_logs()
        while len(backup_logs) > self.backup_amount_limit:
            to_delete: Path = backup_logs.pop(0)
            to_delete.unlink(missing_ok=True)

    def move_file_to_backup_folder(self, file: Path) -> None:
        self.backup_folder.mkdir(parents=True, exist_ok=True)
        number = 0
        target_path = self.backup_folder.joinpath(file.name)

        while target_path.exists() is True:
            number += 1
            name = f"{file.name}_{number}"
            target_path = self.backup_folder.joinpath(name)
        os.rename(src=file, dst=target_path)

    def shouldRollover(self, record: logging.LogRecord) -> bool:
        return False
# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
