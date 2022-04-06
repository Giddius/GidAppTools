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

from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
import logging

from gidapptools.gid_logger.logger import get_logger
if TYPE_CHECKING:
    from gidapptools.gid_logger.records import LOG_RECORD_TYPES
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ProhibitiveSingletonMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is not None:
            raise RuntimeError(f"There can only be one instance of {cls.__name__}")
        cls._instance = super(ProhibitiveSingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instance


class QtMessageHandler(metaclass=ProhibitiveSingletonMeta):
    received_records: list["LOG_RECORD_TYPES"] = []

    def __init__(self) -> None:
        self.msg_split_regex = re.compile(r"(?P<q_class>.*)\:\:(?P<q_method>.*)\:(?P<actual_message>.*)")

    def install(self) -> "QtMessageHandler":
        from PySide6.QtCore import qInstallMessageHandler
        import atexit
        qInstallMessageHandler(self)
        return self

    def mode_to_log_level(self, in_mode):
        in_mode = str(in_mode).rsplit('.', maxsplit=1)[-1].strip().removeprefix("Qt").removesuffix("Msg").upper()
        if in_mode == "FATAL":
            in_mode = "ERROR"
        elif in_mode == "SYSTEM":
            in_mode = "INFO"
        return logging.getLevelName(in_mode)

    def get_context(self, in_context: None):
        frame = sys._getframe(2)
        _context_data = {"fn": in_context.file or frame.f_code.co_filename,
                         "func": in_context.function or frame.f_code.co_name,
                         "lno": in_context.line or frame.f_lineno}

        _logger = get_logger(frame.f_globals["__name__"])
        return _context_data, _logger

    def modify_message(self, in_msg: str) -> str:

        if re_match := self.msg_split_regex.match(in_msg):
            named_parts = re_match.groupdict()
            _message = named_parts.pop("actual_message").strip()
            return _message, {"is_qt": True} | named_parts

        return in_msg, {"is_qt": True}

    def __call__(self, mode, context, message) -> Any:
        context_data, logger = self.get_context(context)
        log_level = self.mode_to_log_level(mode)
        msg, extras = self.modify_message(message)
        record = logger.makeRecord(logger.name, log_level, msg=msg, extra=extras, exc_info=None, args=None, ** context_data)
        logger.handle(record)
        self.received_records.append(record)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
