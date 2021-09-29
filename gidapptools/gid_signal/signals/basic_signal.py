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
import unicodedata
import inspect

import asyncio
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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr, Awaitable, Coroutine
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
from gidapptools.utility.helper import get_qualname_or_name
from .abstract_signal import AbstractSignal
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class Signal(AbstractSignal):

    def emit(self, *args, **kwargs):
        if not self.targets:
            return
        for target in self.targets:
            name = get_qualname_or_name(target)
            info = self.targets_info.get()

            if info.get('is_coroutine') is True:
                task_name = f"{self.name}-Signal_{name}"
                asyncio.create_task(target(*args, **kwargs), name=task_name)
            else:
                target(*args, **kwargs)

    async def aemit(self, *args, **kwargs):
        if not self.targets:
            return

        for target in self.targets:
            name = get_qualname_or_name(target)
            info = self.targets_info.get(name)
            task_name = f"{self.name}-Signal_{name}"
            if info.get('is_coroutine') is False:
                task = asyncio.to_thread(target, *args, **kwargs)
            else:
                task = target(*args, **kwargs)
            asyncio.create_task(task, name=task_name)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
