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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict, UserDict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from configparser import ConfigParser, RawConfigParser
from types import MethodType, ClassMethodDescriptorType, MethodWrapperType
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.timing import time_execution, time_func
from gidapptools.general_helper.dict_helper import get_by_keypath, set_by_key_path
from warnings import warn
from gidapptools.general_helper.dict_helper import AdvancedDict
from gidapptools.gid_config.enums import SpecialTypus
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

CONFIG_DATA_TYPE = dict[str, dict[str, Union[Any, None]]]
CONFIG_SPEC_DATA_TYPE = dict[str, dict[str, Union[Any, None]]]


class ConfigSpecData(UserDict):

    # pylint: disable=super-init-not-called
    def __init__(self,
                 data: CONFIG_SPEC_DATA_TYPE) -> None:
        self._data = data

    @property
    def data(self) -> CONFIG_SPEC_DATA_TYPE:
        return self._data

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        if key is None:
            return self.data.get(section, default)
        return self.data.get(section, {}).get(key, default)


class BaseGidConfig:
    AUTO = SpecialTypus.AUTO
    RAW = SpecialTypus.RAW

    def __init__(self,
                 config_data: CONFIG_DATA_TYPE = None,
                 spec_data: CONFIG_SPEC_DATA_TYPE = None,
                 converter: BaseDispatchTable = None,
                 guess_missing_typus: bool = False,
                 key_path_separator: str = '.',
                 default_section_name: str = 'DEFAULT') -> None:
        self.data = {} if config_data is None else config_data
        self.spec = {} if spec_data is None else spec_data
        self.guess_missing_typus = guess_missing_typus
        self.key_path_separator = key_path_separator
        self.default_section_name = default_section_name
        self.converter = BaseDispatchTable(instance=self, aliases={SpecialTypus.RAW: BaseDispatchTable.DEFAULT}, default_value=lambda x: x, extra_dispatch={str: str, int: int, float: float}) if converter is None else converter

    @property
    def default_typus(self) -> SpecialTypus:
        if self.guess_missing_typus is True:
            return SpecialTypus.AUTO
        return SpecialTypus.RAW

    def _from_default_section(self, key_path: Union[list[str], str]) -> Union[Any, MiscEnum]:
        temp_key_path = [self.default_section_name] + key_path.copy()[1:]
        return get_by_keypath(self.data, temp_key_path, default=MiscEnum.NOT_FOUND)

    def _direct_get(self, key_path: Union[list[str], str]) -> Union[Any, MiscEnum]:
        return get_by_keypath(self.data, key_path, default=self._from_default_section(key_path))

    @time_func()
    def get(self,
            key_path: Union[list[str], str],
            typus=None,
            *,
            fallback_key_path: Union[list[str], str] = MiscEnum.NOTHING,
            direct_fallback: Any = MiscEnum.NOTHING,
            default: Any = None,
            strict: bool = False) -> Any:
        if strict is True and default is not None:
            warn("if strict=True, the value of 'default' is ignored!", stacklevel=3)

        key_path = [key.strip() for key in key_path.split(self.key_path_separator)] if isinstance(key_path, str) else key_path

        value = self._direct_get(key_path)

        if value is MiscEnum.NOT_FOUND:
            if direct_fallback is not MiscEnum.NOTHING:
                return direct_fallback

            elif fallback_key_path is not MiscEnum.NOTHING:
                fallback_key_path = [key.strip() for key in fallback_key_path.split(self.key_path_separator)] if isinstance(fallback_key_path, str) else fallback_key_path
                value = self._direct_get(fallback_key_path)

        if value is MiscEnum.NOT_FOUND:
            if strict is False:
                return default

            # TODO: custom error
            raise RuntimeError(f'keypath {".".join(key_path)!r} not found.')

        typus = self.default_typus if typus is None else typus
        return self.converter.get(typus)(value)
# region[Main_Exec]


if __name__ == '__main__':
    c_data = {'DEFAULT': {'job': "unemployed"},
              'first': {'name': 'tom',
                                'age': "50",
                                'job': 'sausage maker'}}
    x = BaseGidConfig(config_data=c_data)
    x.get(['second', 'job'])
    print(x.get(['first', 'job'], fallback_key_path='first.cat', strict=False, default=1))
    print(x.get(['first', 'job'], fallback_key_path='first.cat', strict=True, default=1))
    print(x.get(['first', 'age'], fallback_key_path='first.cat', typus=int))
# endregion[Main_Exec]
