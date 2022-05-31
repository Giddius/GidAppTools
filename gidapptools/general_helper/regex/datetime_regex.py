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
from frozendict import frozendict

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

DATETIME_FORMAT_REGEX_MAPPING: frozendict[str, str] = frozendict(**{r"%Y": r"(?P<year>\d{4})",
                                                                    r"%m": r"(?P<month>[01]?\d)",
                                                                    r"%d": r"(?P<day>[0123]?\d)",
                                                                    r"%H": r"(?P<hour>[012]?\d)",
                                                                    r"%M": r"(?P<minute>[0-5]?\d)",
                                                                    r"%S": r"(?P<second>[0-5]?\d)",
                                                                    r"%f": r"(?P<microsecond>\d+)",
                                                                    r"%Z": r"(?P<tzinfo>[a-zA-Z]+([+-]\d{2}(\:\d{2})?)?)"})


def datetime_format_to_regex(in_format: str, flags: re.RegexFlag) -> re.Pattern:
    pattern_string = in_format
    for k, v in DATETIME_FORMAT_REGEX_MAPPING.items():
        pattern_string = pattern_string.replace(k, v)
    return re.compile(pattern_string, flags)

    # region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
