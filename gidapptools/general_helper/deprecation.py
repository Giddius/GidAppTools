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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO
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

from warnings import warn, warn_explicit, WarningMessage, catch_warnings, _is_internal_frame, _next_external_frame
from gidapptools.general_helper.enums import MiscEnum

try:
    from icecream import ic
except ImportError:
    ic = print

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class DeprecationWarningTypus(Enum):
    ARGUMENT = auto()


def _replace_default_argument_w_NOTHING(func, arg_name: str, *args, **kwargs) -> inspect.BoundArguments:
    func_sig = inspect.signature(func)
    new_arg = func_sig.parameters[arg_name].replace(default=MiscEnum.NOTHING)
    new_params = [param_value if param_name != arg_name else new_arg for param_name, param_value in func_sig.parameters.items()]
    new_sig = func_sig.replace(parameters=new_params)
    bound_args = new_sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    return bound_args


def _make_deprication_warning(typus: DeprecationWarning, **kwargs) -> None:
    if typus is DeprecationWarningTypus.ARGUMENT:

        needed = {"arg_name", "func_name", "func"}
        if any(kwarg_name not in kwargs for kwarg_name in needed):
            missing = [pos_missing for pos_missing in needed if kwargs.get(pos_missing, None) is None]
            raise AttributeError(f"missing needed kwargs {', '.join(repr(i) for i in missing)}.")

        message_parts = [f"The argument {kwargs.get('arg_name')!r} for '{kwargs.get('func_name')}()' is deprecated"]
        if kwargs.get('not_used', False):
            message_parts.append("it is not used anymore in the actual function (does not do anything)")
        if kwargs.get('alternative_arg_name', None):
            message_parts.append(f"use the alternative {kwargs.get('alternative_arg_name')!r}")
        message = ', '.join(message_parts) + '.'

    warn(message=message, category=DeprecationWarning, stacklevel=3)


def deprecated_argument(arg_name: str, alternative_arg_name: str = None):

    def _wrapper(func):
        func_name = func.__qualname__ or func.__name__

        @wraps(func)
        def _wrapped(*args, **kwargs):
            new_bound_args = _replace_default_argument_w_NOTHING(func, arg_name, *args, **kwargs)
            args = new_bound_args.args
            kwargs = new_bound_args.kwargs
            if new_bound_args.arguments[arg_name] is not MiscEnum.NOTHING:
                _make_deprication_warning(DeprecationWarningTypus.ARGUMENT, func=func, arg_name=arg_name, func_name=func_name, not_used=True, alternative_arg_name=alternative_arg_name)
            return func(*args, **kwargs)

        return _wrapped

    return _wrapper


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
