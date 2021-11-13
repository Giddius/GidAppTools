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
import logging
import threading
from gidapptools.gid_logger.enums import LoggingLevel
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
logging.basicConfig()
log = logging.getLogger(__name__)

log.setLevel(LoggingLevel.DEBUG)
# endregion[Constants]


class GidLogRecordFactory:
    activation_lock = threading.RLock()

    def __init__(self) -> None:
        self.special_records_registry: dict[str, logging.LogRecord] = {}
        self.original_factory: Callable = None

    def is_active(self) -> bool:
        return logging.getLogRecordFactory() is self

    def __call__(self,
                 name: str,
                 level: Union[int, str, Enum],
                 pathname: Union[os.PathLike, str, Path],
                 lineno: int,
                 msg: str,
                 args: tuple[Any],
                 exc_info: Union[tuple, bool, BaseException] = None,
                 func: str = None,
                 sinfo: str = None,
                 **kwargs):
        special_record = kwargs.pop("record_typus", None)

        print(f"{special_record=}")

        if inspect.isclass(special_record):
            record_class = special_record
        else:
            record_class = self.special_records_registry.get(special_record, self.original_factory)

        return record_class(name=name,
                            level=level,
                            pathname=pathname,
                            lineno=lineno,
                            msg=msg,
                            args=args,
                            exc_info=exc_info,
                            func=func,
                            sinfo=sinfo,
                            **kwargs)

    def activate(self, raise_on_already_active: bool = False) -> bool:
        with self.activation_lock:

            if self.is_active() is True:
                if raise_on_already_active is True:
                    # TODO: Custom Error!
                    raise RuntimeError(f"{self!r} is already active.")
                return False

            self.original_factory = logging.getLogRecordFactory()
            logging.setLogRecordFactory(self)
            return True

    def deactivate(self, raise_on_not_active: bool = False) -> bool:
        with self.activation_lock:

            if self.is_active() is False:
                if raise_on_not_active is True:
                    # TODO: Custom Error!
                    raise RuntimeError(f"Unable to deactivate {self!r}, because it is currently not active.")
                return False

            logging.setLogRecordFactory(self.original_factory)

            self.original_factory = None
            return True


gid_log_record_factory = GidLogRecordFactory()


class GidBaseLogRecord(logging.LogRecord):
    ...


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
