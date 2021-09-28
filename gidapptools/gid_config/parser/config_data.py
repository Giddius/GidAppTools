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
from gidapptools.errors import AdvancedDictError, DispatchError
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.enums import SpecialTypus
from gidapptools.gid_config.parser.tokens import Section, Entry

if TYPE_CHECKING:
    from gidapptools.gid_config.conversion.conversion_table import ConversionTable
    from gidapptools.gid_config.conversion.spec_data import SpecData
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ConfigData:
    AUTO = SpecialTypus.AUTO
    RAW = SpecialTypus.RAW

    def __init__(self,
                 conversion_table: "ConversionTable",
                 spec_data: "SpecData" = None,
                 default_auto_convert: bool = True,

                 default_if_section_missing: bool = True,
                 empty_is_missing: bool = False) -> None:
        self.conversion_table = conversion_table
        self.spec_data = spec_data
        self.sections: dict[str, Section] = {}
        self.default_auto_convert = SpecialTypus.AUTO if default_auto_convert is None else SpecialTypus.RAW

        self.default_if_section_missing = default_if_section_missing
        self.empty_is_missing = empty_is_missing

    def add_section(self, section) -> None:
        self.sections[section.name] = section

    def _get_section(self, section_name: str) -> Union[Section, MiscEnum]:
        try:
            return self.sections[section_name]
        except KeyError as error:
            if self.default_if_section_missing is True:
                return MiscEnum.NOT_FOUND
            raise

    def _get_value(self, section: Section, key: str) -> Union[Section, MiscEnum]:
        if section is MiscEnum.NOT_FOUND:
            return MiscEnum.NOT_FOUND

        value = section.get(key, MiscEnum.NOT_FOUND)
        if self.empty_is_missing is True and value in {'', None, [], {}}:
            value = MiscEnum.NOT_FOUND
        return MiscEnum.NOT_FOUND

    def _convert(self, key_path: list[str], value, typus: Union[SpecialTypus, type], *, _is_retry: bool = False) -> Any:
        if typus is SpecialTypus.RAW:
            return value

        if typus is SpecialTypus.AUTO:
            typus = self.spec_data.get_converter(key_path)
        if typus is SpecialTypus.DELAYED:
            if _is_retry is False:
                self.spec_data.reload()
                return self._convert(key_path=key_path, value=value, typus=typus, _is_retry=True)
            # TODO: Custom error
            raise TypeError(typus)
        converter = self.conversion_table.get_converter(typus)

        return converter(value)

    def get(self, section_name: str, key: str, typus: Union[SpecialTypus, type] = None, default: Any = None) -> Any:
        typus = self.default_auto_convert if typus is None else typus
        section = self._get_section(section_name)
        if section is MiscEnum.NOT_FOUND:
            return default
        value = self._get_value(section=section, key=key)

        if value is MiscEnum.NOT_FOUND:
            return default

        if typus is SpecialTypus.RAW:
            return value
        try:
            return self._convert([section_name, key], value, typus)
        except (KeyError, AdvancedDictError, DispatchError):
            return default

    def clear_sections(self) -> None:
        self.sections = {}

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
