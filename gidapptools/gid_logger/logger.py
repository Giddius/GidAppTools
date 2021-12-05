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
from logging.handlers import QueueHandler, QueueListener
from gidapptools.gid_logger.enums import LoggingLevel
import atexit
from gidapptools.gid_logger.formatter import GidLoggingFormatter, GidSectionLoggingStyle, get_all_func_names, get_all_module_names
from gidapptools.gid_logger.handler import GidBaseRotatingFileHandler
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidLogger(logging.Logger):
    ...


def _modify_logger_name(name: str) -> str:
    if name == "__main__":
        return 'main'
    name = 'main.' + '.'.join(name.split('.')[1:])
    return name


def get_logger(name: str) -> Union[logging.Logger, GidLogger]:
    name = _modify_logger_name(name)
    return logging.getLogger(name)


def get_main_logger(name: str, path: Path, log_level: LoggingLevel = LoggingLevel.DEBUG, formatter: Union[logging.Formatter, GidLoggingFormatter] = None) -> Union[logging.Logger, GidLogger]:
    os.environ["MAX_FUNC_NAME_LEN"] = str(min([max(len(i) for i in get_all_func_names(path, True)), 20]))
    os.environ["MAX_MODULE_NAME_LEN"] = str(min([max(len(i) for i in get_all_module_names(path)), 20]))

    handler = logging.StreamHandler(stream=sys.stdout)

    que = queue.Queue(-1)
    que_handler = QueueHandler(que)
    listener = QueueListener(que, handler)
    formatter = GidLoggingFormatter() if formatter is None else formatter
    handler.setFormatter(formatter)
    _log = get_logger(name)
    _log.addHandler(que_handler)
    _log.setLevel(log_level)
    listener.start()
    atexit.register(listener.stop)
    return _log


def get_main_logger_with_file_logging(name: str, log_file_base_name: str, path: Path, log_level: LoggingLevel = LoggingLevel.DEBUG, formatter: Union[logging.Formatter, GidLoggingFormatter] = None, extra_logger: Iterable[str] = tuple()) -> Union[logging.Logger, GidLogger]:
    os.environ["MAX_FUNC_NAME_LEN"] = str(min([max(len(i) for i in get_all_func_names(path, True)), 20]))
    os.environ["MAX_MODULE_NAME_LEN"] = str(min([max(len(i) for i in get_all_module_names(path)), 20]))
    que = queue.Queue(-1)
    que_handler = QueueHandler(que)

    handler = logging.StreamHandler(stream=sys.stdout)
    file_handler = GidBaseRotatingFileHandler(base_name=log_file_base_name, log_folder=path.parent.joinpath("logs"))

    formatter = GidLoggingFormatter() if formatter is None else formatter
    handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    listener = QueueListener(que, handler, file_handler)
    _log = get_logger(name)
    for logger in [_log] + [logging.getLogger(l) for l in extra_logger]:
        logger.addHandler(que_handler)

        logger.setLevel(log_level)
    listener.start()
    atexit.register(listener.stop)
    return _log

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
