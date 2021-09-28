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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator
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
from gidapptools.errors import KeyPathError, NotMappingError, AdvancedDictError
from gidapptools.general_helper.checker import is_hashable
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.conversion.conversion_table import EntryTypus
from gidapptools.general_helper.conversion import str_to_bool
from threading import Lock
from yarl import URL

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def get_by_keypath(the_dict: dict, key_path: list[str], default: Any = None, *, strict: bool = False) -> Any:
    key_path = key_path.copy()
    last_key = key_path.pop(-1)
    for key in key_path:
        try:
            the_dict = the_dict[key]
        except KeyError as e:
            if strict is True:
                raise KeyError(f"The {key_path.index(key)+1}. key {key!r} was not found in the dict.") from e
            return default
    return the_dict.get(last_key, default)


def set_by_key_path(the_dict: dict, key_path: list[str], value: Any, *, create_intermediates: bool = False) -> None:
    key_path = key_path.copy()
    last_key = key_path.pop(-1)
    for key in key_path:
        try:
            the_dict = the_dict[key]
        except KeyError as e:
            if create_intermediates is True:
                the_dict[key] = {}
                the_dict = the_dict[key]
            else:
                raise KeyError(f"The {key_path.index(key)+1}. key {key!r} was not found in the dict, use 'create_intermediates=True' to auto-create intermediated keys if missing.") from e

    the_dict[last_key] = value


class BaseVisitor:
    handle_prefix = "_handle_"
    handler_regex = re.compile(rf"^{handle_prefix}(?P<target>\w+)$")
    named_args_doc_identifier = "NAMED_VALUE_ARGUMENTS"

    def __init__(self, advanced_dict: "AdvancedDict", extra_handlers: dict[Hashable, Callable] = None, default_handler: Callable = None) -> None:
        self.advanced_dict = advanced_dict
        self.extra_handlers = {} if extra_handlers is None else extra_handlers
        self.default_handler = default_handler
        self._handlers: dict[Hashable, Callable] = None
        self._inspect_lock = Lock()

    def reload(self) -> None:
        self._collect_handlers()

    def add_extra_handlers(self, target_name: str, handler: Callable) -> None:
        self.extra_handlers[target_name] = handler
        self.reload()

    def get_all_handler_names(cls) -> tuple[str]:
        instance = cls(AdvancedDict())
        return tuple(instance.handlers)

    def get_all_handlers_with_named_arguments(cls) -> dict[str, Optional[dict[str, str]]]:
        def get_named_args(text: str) -> dict[str, str]:
            _named_args = {}
            named_args_index = text.find(cls.named_args_doc_identifier)
            next_line_index = text.find('\n', named_args_index)
            if named_args_index == -1:
                return _named_args
            gen = (line for line in text[next_line_index:].splitlines() if line)
            line = next(gen)
            while line.startswith('\t') or line.startswith(' ' * 4):
                line = line.strip()
                if not line:
                    continue
                if line in {"Returns:", "Args:"}:
                    break
                if line.strip().casefold == 'none':
                    return _named_args
                try:
                    name, description = line.split(':')
                    _named_args[name.strip()] = description.strip()
                except ValueError:
                    print(f"{line=}")
                line = next(gen, '')
            return _named_args

        instance = cls(AdvancedDict())
        _out = {}
        for handler_name, handler_obj in instance.handlers.items():
            doc_text = handler_obj.__doc__
            if doc_text is None:
                _out[handler_name] = {}
            else:
                _out[handler_name] = get_named_args(doc_text)
        return _out

    @property
    def handlers(self) -> dict[Hashable, Callable]:
        if self._inspect_lock.locked() is True:
            return
        if self._handlers is None:
            self._collect_handlers()
        return self._handlers

    def _collect_handlers(self) -> None:
        with self._inspect_lock:
            collected_handlers = {}
            for meth_name, meth_obj in inspect.getmembers(self, inspect.ismethod):

                match = self.handler_regex.match(meth_name)
                if match:
                    target = match.group('target')
                    if not target.strip():
                        continue
                    if target == 'default':
                        target = MiscEnum.DEFAULT
                        if self.default_handler is None:
                            self.default_handler = meth_obj

                    collected_handlers[target] = meth_obj
            if self._handlers is None:
                self._handlers = {}
            self._handlers |= collected_handlers
            self._handlers |= self.extra_handlers

    def _modify_value(self, value: Any) -> Any:
        return value

    def visit(self, key_path: tuple[str], value: Any) -> None:

        key_path = tuple(key_path)
        value_key = self._modify_value(value)

        handler = self.handlers.get(key_path, self.handlers.get(value_key, self.default_handler))
        if handler is None:
            return

        self.advanced_dict.set(key_path, handler(value))


RAW_KEYPATH_TYPE = Union[list[str], str, Hashable]
MODDIFIED_KEYPATH_TYPE = list[Hashable]

ResolveKeyPathResult = namedtuple("ResolveKeyPathResult", ["data", "last_key"], defaults=(None,))


class AdvancedDict(UserDict):
    empty_values = [[], "", set(), tuple(), frozenset(), dict(), b"", None]

    def __init__(self, data: Mapping = None,
                 keypath_separator: str = '.',
                 case_insensitive: bool = False,
                 convert_keys_to_str: bool = False,
                 auto_set_missing: bool = False,
                 empty_is_missing: bool = False,
                 extra_empty_values: Iterable[Any] = None,
                 visitor_class: BaseVisitor = None,
                 ** kwargs) -> None:
        self.keypath_separator = keypath_separator
        self._case_insensitive = case_insensitive
        self.auto_set_missing = auto_set_missing
        self.convert_keys_to_str = convert_keys_to_str
        self.empty_is_missing = empty_is_missing
        if extra_empty_values is not None:
            self.empty_values.extend(extra_empty_values)
        self.visitor = BaseVisitor(self) if visitor_class is None else visitor_class(self)
        super().__init__(data, **kwargs)

    @property
    def case_insensitive(self) -> bool:
        return self._case_insensitive

    def _modify_key(self, key: Hashable) -> Hashable:

        if self.convert_keys_to_str is True and not isinstance(key, str):
            key = str(key)
        if self.case_insensitive is True and isinstance(key, str):
            return key.casefold()
        if not is_hashable(key):
            # TODO: better custom error
            raise TypeError(f"unhashable key {key!r} in key_path.")
        return key

    def _handle_keypath(self, key_path: RAW_KEYPATH_TYPE) -> MODDIFIED_KEYPATH_TYPE:
        if not isinstance(key_path, (str, Iterable)):
            return [self._modify_key(key_path)]

        if isinstance(key_path, str):
            key_path = key_path.split(self.keypath_separator)

        return [self._modify_key(key) for key in key_path]

    def _resolve_key_path(self, key_path: MODDIFIED_KEYPATH_TYPE, *, hold_last: bool = False, check_auto_set: bool = False) -> ResolveKeyPathResult:
        data = self.data
        key_path = self._handle_keypath(key_path)
        last_key = None if hold_last is False else key_path.pop(-1)
        for key in key_path:
            try:
                if not isinstance(data, Mapping):
                    raise NotMappingError(key, data, key_path, 'get', last_key)
                data = data[key]
            except KeyError as error:
                if check_auto_set is True and self.auto_set_missing is True:
                    data[key] = {}
                    data = data[key]
                else:
                    raise KeyPathError(key, key_path, last_key) from error

        return ResolveKeyPathResult(data, last_key)

    def __getitem__(self, key_path: RAW_KEYPATH_TYPE) -> Any:
        result = self._resolve_key_path(key_path).data
        if self.empty_is_missing is True and result in self.empty_values:
            raise KeyPathError(key_path[-1], key_path)
        return result

    def __setitem__(self, key_path: RAW_KEYPATH_TYPE, value: Any) -> None:
        data, last_key = self._resolve_key_path(key_path, hold_last=True, check_auto_set=True)
        if not isinstance(data, Mapping):
            raise NotMappingError(last_key, data, self._handle_keypath(key_path), 'set')
        data[last_key] = value

    def set(self, key_path: RAW_KEYPATH_TYPE, value: Any) -> None:
        self.__setitem__(key_path=key_path, value=value)

    def __delitem__(self, key_path: RAW_KEYPATH_TYPE) -> None:
        data, last_key = self._resolve_key_path(key_path, hold_last=True)
        del data[last_key]

    def update(self, data: Mapping = None, **kwargs) -> None:
        data = {} if data is None else data
        update_data = {self._modify_key(key): value for key, value in data.items()}
        update_kwargs = {self._modify_key(key): value for key, value in kwargs.items()}
        super().update(update_data, **update_kwargs)

    # pylint: disable=arguments-renamed
    def get(self, key_path: Any, default: Any = None) -> Any:
        try:
            return self[key_path]
        except (KeyError, AdvancedDictError):
            return default

    def walk(self, temp_copy: bool = False) -> Generator[tuple[tuple[str], Any], None, None]:

        def _walk(data: dict[Hashable, Any], path: list[str] = None) -> Generator[tuple[tuple[str], Any], None, None]:
            path = [] if path is None else path
            for key, value in data.items():

                temp_path = path + [key]
                if isinstance(value, (self.__class__, dict, Mapping)):
                    yield from _walk(value, temp_path)
                else:

                    yield temp_path, value

        _data = self.data if temp_copy is False else self.data.copy()
        yield from _walk(_data)

    def visit(self, visitor: BaseVisitor = None) -> None:
        visitor = self.visitor if visitor is None else visitor

        for key_path, value in self.walk(temp_copy=True):
            visitor.visit(key_path, value)


        # region[Main_Exec]
if __name__ == '__main__':
    x = defaultdict(Lock)
    print(type(x["a"]))
    print(x)

# endregion[Main_Exec]
