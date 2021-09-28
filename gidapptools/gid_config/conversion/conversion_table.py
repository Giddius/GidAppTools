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

from gidapptools.general_helper.dispatch_table import BaseDispatchTable
from gidapptools.errors import DispatchError
import attr
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.enums import SpecialTypus
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


@attr.s(auto_attribs=True, auto_detect=True)
class EntryTypus:
    original_value: str = attr.ib(on_setattr=attr.setters.NO_OP, default=None)
    base_typus: type = attr.ib(on_setattr=attr.setters.NO_OP, default=SpecialTypus.DELAYED)
    named_arguments: dict[str, Any] = attr.ib(default=None, converter=attr.converters.default_if_none(factory=dict))
    other_arguments: list[Any] = attr.ib(default=None, converter=attr.converters.default_if_none(factory=list))

    def __hash__(self) -> int:
        return hash(self.base_typus)

    def __getitem__(self, key: Union[str, int]) -> Any:
        if isinstance(key, int):
            return self.other_arguments[key]

        return self.named_arguments[key]

    def get(self, key: Union[str, int], default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: Union[str, int], default: Any = None) -> Any:
        if isinstance(key, int):
            return self.other_arguments.pop(key, default)
        return self.named_arguments.pop(key, default)

    def __repr__(self) -> str:
        if self.base_typus is SpecialTypus.DELAYED:
            return f"{self.base_typus.name}(original_value={self.original_value!r})"
        text = f"{self.base_typus}"
        if self.named_arguments:
            text += "(" + ', '.join(f"{key}={value}" for key, value in self.named_arguments.items()) + ')'
        return text

    @property
    def typus(self) -> type:
        sub_typus = [item for item in self.named_arguments.values() if isinstance(item, EntryTypus)]
        if sub_typus:
            sub_typus = sub_typus[0]
            return self.base_typus[sub_typus.typus]
        return self.base_typus

    @classmethod
    @property
    def special_name_conversion_table(cls) -> str:
        return {'str': 'string',
                'int': 'integer',
                'bool': 'boolean'}

    def convert_for_json(self) -> str:

        if self.original_value is not None:
            return self.original_value
        _out = self.base_typus.__name__
        _out = self.special_conversion_map.get(_out, _out)
        args = ''
        if self.named_arguments:
            args = ', '.join(value for value in self.named_arguments.values())
        if self.other_arguments:
            args += ', ' + ', '.join(value for value in self.other_arguments)

        if args:
            _out += f"({args})"
        return _out


class ConversionTable(BaseDispatchTable):

    def get_converter(self, typus: Union[type, EntryTypus]) -> Callable:
        if not isinstance(typus, EntryTypus):
            typus = EntryTypus(base_typus=typus)

        return self.get(typus)

# region[Main_Exec]


if __name__ == '__main__':
    x = EntryTypus(None, datetime)
    print(x.base_typus.__name__)

# endregion[Main_Exec]
