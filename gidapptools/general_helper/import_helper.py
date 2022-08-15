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
import importlib.util
import pkgutil
import pp

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def is_importable(package_name: str) -> bool:
    """
    Checks if the package is importable, without actually trying to import it.

    :param package_name: Name of the Package to check, is case-sensitive
    :type package_name: str
    :return: True if the package is importable in the current environment
    :rtype: bool
    """
    return importlib.util.find_spec(name=package_name) is not None


def all_importable_package_names(exclude_underscored: bool = True, exclude_std_lib: bool = False) -> tuple[str]:

    def _check_exclude(in_name: str) -> bool:
        if exclude_underscored is True and in_name.startswith("_"):
            return False
        if exclude_std_lib is True and in_name in sys.stdlib_module_names:
            return False
        return True

    return tuple(sorted([i for i in pkgutil.iter_modules() if _check_exclude(i.name)], key=lambda x: x.name.casefold()))

# region[Main_Exec]


if __name__ == '__main__':
    pp(all_importable_package_names(exclude_std_lib=True, exclude_underscored=True))


# endregion[Main_Exec]
