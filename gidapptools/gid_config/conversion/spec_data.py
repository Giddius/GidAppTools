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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable
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
from threading import Lock
from yarl import URL
from gidapptools.general_helper.dict_helper import AdvancedDict, AdvancedDictError, KeyPathError, BaseVisitor
from gidapptools.gid_config.conversion.conversion_table import EntryTypus
from gidapptools.general_helper.general import defaultable_list_pop
from gidapptools.general_helper.conversion import str_to_bool
from hashlib import blake2b
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SpecVisitor(BaseVisitor):
    sub_argument_regex = re.compile(r"(?P<base_type>\w+)\(((?P<sub_arguments>.*)\))?")

    def __init__(self, advanced_dict: "AdvancedDict", extra_handlers: dict[Hashable, Callable] = None, sub_argument_separator: str = ',') -> None:
        super().__init__(advanced_dict, extra_handlers=extra_handlers)
        self.sub_argument_separator = sub_argument_separator

    def _modify_value(self, value: Any) -> Any:
        value = super()._modify_value(value)
        try:
            value = self.sub_argument_regex.sub(r"\g<base_type>", value)
        except (AttributeError, TypeError):
            pass

        return value

    def _get_handler_direct(self, value: str) -> Callable:
        return self.handlers.get(value, self._handle_string)

    def _get_sub_arguments(self, value: str, default: list[Any] = None) -> list[Any]:

        try:
            match = self.sub_argument_regex.match(value)
            sub_arguments_string = match.groupdict().get("sub_arguments", default)
            sub_arguments = [i.strip() for i in sub_arguments_string.split(self.sub_argument_separator) if i]
            if not sub_arguments:
                return default
            return sub_arguments
        except AttributeError:
            return default

    def _handle_default(self, value: Any) -> EntryTypus:
        """
        handles all values that other handlers, can't or that raised an error while dispatching to handlers.

        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): The nodes value.

        Returns:
            EntryTypus: An `EntryTypus` with only an `original_value` and the base_typus set to `SpecialTypus.DELAYED)
        """
        return EntryTypus(original_value=value)

    def _handle_boolean(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=bool, other_arguments=self._get_sub_arguments(value, None))

    def _handle_string(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=str, other_arguments=self._get_sub_arguments(value, None))

    def _handle_integer(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=int, other_arguments=self._get_sub_arguments(value, None))

    def _handle_float(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=float, other_arguments=self._get_sub_arguments(value, None))

    def _handle_bytes(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=bytes, other_arguments=self._get_sub_arguments(value, None))

    def _handle_list(self, value: Any) -> EntryTypus:
        """
        Converts the value to `list` with optional sub_type (eg: `list[int]`).

        NAMED_VALUE_ARGUMENTS:
            subtype: The subtype of the list, defaults to `string`, can be any other handled type.
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        sub_arguments = self._get_sub_arguments(value)

        subtype_string = defaultable_list_pop(sub_arguments, 0, "string")

        handler = self._get_handler_direct(subtype_string)

        subtype = handler(subtype_string)
        return EntryTypus(original_value=value, base_typus=list, named_arguments={"subtype": subtype}, other_arguments=sub_arguments)

    def _handle_datetime(self, value: Any) -> EntryTypus:
        """
        [summary]

        NAMED_VALUE_ARGUMENTS:
            fmt: The format to use with `datetime.strptime`, if it is "isoformat" then `datetime.fromisoformat` will be used and if it is `timestamp` then `datetime.fromtimestamp`, defaults to "isoformat"
            time_zone: The timezone to provide to datetime, defaults to: "utc"
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        sub_arguments = self._get_sub_arguments(value)
        fmt = defaultable_list_pop(sub_arguments, 0, "isoformat")
        time_zone = defaultable_list_pop(sub_arguments, 0, "utc")
        return EntryTypus(original_value=value, base_typus=datetime, named_arguments={'fmt': fmt, 'tz': time_zone}, other_arguments=sub_arguments)

    def _handle_path(self, value: Any) -> EntryTypus:
        sub_arguments = self._get_sub_arguments(value)
        resolve = defaultable_list_pop(sub_arguments, 0, 'true')
        return EntryTypus(original_value=value, base_typus=Path, named_arguments={'resolve': resolve}, other_arguments=sub_arguments)

    def _handle_url(self, value: Any) -> EntryTypus:
        sub_arguments = self._get_sub_arguments(value)
        return EntryTypus(original_value=value, base_typus=URL, other_arguments=sub_arguments)


class SpecData(AdvancedDict):

    def __init__(self, data: dict = None, visitor_class: SpecVisitor = None) -> None:
        visitor_class = SpecVisitor if visitor_class is None else visitor_class
        super().__init__(data=data, visitor_class=visitor_class)

    def get_converter(self, key_path: Union[list[str], str]) -> EntryTypus:
        return self[key_path]['converter']

    def _resolve_converter(self) -> None:
        self.visit()

    def reload(self) -> None:
        self.visitor.reload()
        self._resolve_converter()


class SpecDataFile(SpecData):

    def __init__(self, in_file: Path, changed_parameter: str = 'size', ensure: bool = True, visitor_class: SpecVisitor = None, **kwargs) -> None:
        super().__init__(visitor_class=visitor_class, **kwargs)

        self.file_path = Path(in_file).resolve()
        self.changed_parameter = changed_parameter
        self.ensure = ensure
        self.last_size: int = None
        self.last_file_hash: str = None
        self.data = None
        self.lock = Lock()

    @property
    def has_changed(self) -> bool:
        if self.changed_parameter == 'always':
            return True
        if self.changed_parameter == 'both':
            if any([param is None for param in [self.last_size, self.last_file_hash]] + [self.last_size != self.size, self.last_file_hash != self.last_file_hash]):
                return True
        if self.changed_parameter == 'size':
            if self.last_size is None or self.size != self.last_size:
                return True
        elif self.changed_parameter == 'file_hash':
            if self.last_file_hash is None or self.file_hash != self.last_file_hash:
                return True
        return False

    def get_converter(self, key_path: Union[list[str], str]) -> EntryTypus:
        with self.lock:
            if self.data is None or self.has_changed is True:
                self.reload(locked=True)
            return super().get_converter(key_path)

    @property
    def size(self) -> int:
        return self.file_path.stat().st_size

    @property
    def file_hash(self) -> str:
        _file_hash = blake2b()
        with self.file_path.open('rb') as f:
            for chunk in f:
                _file_hash.update(chunk)
        return _file_hash.hexdigest()

    def reload(self, locked: bool = False) -> None:
        self.load(locked)
        super().reload()

    def _json_converter(self, item: Union[EntryTypus, type]) -> str:
        try:
            return item.convert_for_json()
        except AttributeError:
            return EntryTypus.special_name_conversion_table(type.__name__, type.__name__)

    def load(self, locked: bool = False):
        def _load():
            with self.file_path.open('r', encoding='utf-8', errors='ignore') as f:
                return json.load(f)

        if self.file_path.exists() is False and self.ensure is True:
            self.write(locked=locked)
        if locked is False:
            with self.lock:
                self.data = _load()
        else:
            self.data = _load()

    def write(self, locked: bool = False) -> None:
        def _write():
            with self.file_path.open('w', encoding='utf-8', errors='ignore') as f:
                data = {} if self.data is None else self.data
                json.dump(data, f, default=self._json_converter, indent=4, sort_keys=True)

        if locked is False:
            with self.lock:
                _write()
        else:
            _write()


# region[Main_Exec]


if __name__ == '__main__':
    x = SpecDataFile(Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\example_spec_file.json"))
    x.reload()
    import rich
    for k, v in x.data.items():
        for key, _value in v.items():
            if isinstance(_value, EntryTypus):
                print(_value.typus)
# endregion[Main_Exec]
