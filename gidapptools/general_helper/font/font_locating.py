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

import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import (TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, ForwardRef, final,
                    no_type_check, no_type_check_decorator, overload, get_type_hints, cast, Protocol, runtime_checkable, NoReturn, NewType, Literal, AnyStr, IO, BinaryIO, TextIO, Any)
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from collections.abc import (AsyncGenerator, AsyncIterable, AsyncIterator, Awaitable, ByteString, Callable, Collection, Container, Coroutine, Generator,
                             Hashable, ItemsView, Iterable, Iterator, KeysView, Mapping, MappingView, MutableMapping, MutableSequence, MutableSet, Reversible, Sequence, Set, Sized, ValuesView)
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property, cache
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, wait, as_completed, ALL_COMPLETED, FIRST_EXCEPTION, FIRST_COMPLETED
from fontTools import ttLib


if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    ...


# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


WINDOWS_FONT_FOLDER: tuple[Path] = (Path(os.getenv("WINDIR"), "Fonts"),
                                    Path(os.getenv("LOCALAPPDATA"), "Microsoft", "Windows", "Fonts"))


class FontFile:
    __slots__ = ("_file_path",
                 "_name",
                 "_family_name")

    def __init__(self, file_path: Union[str, os.PathLike, Path]) -> None:
        self._file_path = Path(file_path).resolve()
        self._name: str = None
        self._family_name: str = None

    @property
    def name(self) -> str:
        if self._name is None:
            self._name, self._family_name = self.get_name_and_family_name(self.get_font_obj())
        return self._name

    @property
    def family_name(self) -> str:
        if self._family_name is None:
            self._name, self._family_name = self.get_name_and_family_name(self.get_font_obj())
        return self._family_name

    @property
    def file_path(self) -> Path:
        return self._file_path

    def get_font_obj(self) -> ttLib.TTFont:
        return ttLib.TTFont(self.file_path)

    def __fspath__(self) -> str:
        return os.fspath(self.file_path)

    def __hash__(self) -> int:
        return hash(self.name) + hash(self.family_name)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name!r}, family={self.family_name!r})'

    @staticmethod
    def get_name_and_family_name(font_item) -> tuple[str, str]:
        """Get the short name from the font's names table"""
        FONT_SPECIFIER_NAME_ID = 4
        FONT_SPECIFIER_FAMILY_ID = 1

        name = ""
        family = ""
        for record in font_item['name'].names:
            if b'\x00' in record.string:
                name_str = record.string.decode('utf-16-be', errors="ignore")
            else:
                name_str = record.string.decode('utf-8', errors="ignore")
            if record.nameID == FONT_SPECIFIER_NAME_ID and not name:
                name = name_str
            elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family:
                family = name_str
            if name and family:
                break
        return name, family


def iter_all_fonts() -> Generator["FontFile", None, None]:
    for font_folder in WINDOWS_FONT_FOLDER:

        for file in font_folder.iterdir():
            if file.is_dir():
                continue

            if file.suffix != ".ttf":
                continue

            yield FontFile(file)


def list_all_fonts() -> list["FontFile"]:
    return list(iter_all_fonts())


class _Font_Cache:

    def __init__(self) -> None:
        self._all_fonts: set["FontFile"] = None
        self._name_data: dict[str, "FontFile"] = {}
        self._family_and_name_data: dict[tuple[str, str], "FontFile"] = {}
        self._file_path_data: dict[Path, "FontFile"] = {}

    @property
    def all_fonts(self) -> set["FontFile"]:
        if self._all_fonts is None:
            self._all_fonts = set(iter_all_fonts())
        return self._all_fonts

    def _load_by_name(self, name: str) -> Optional["FontFile"]:
        return next((font for font in self.all_fonts if font.name == name), None)

    def _load_by_family_and_name(self, name: str, family_name: str) -> Optional["FontFile"]:
        return next((font for font in self.all_fonts if font.family_name == family_name and font.name == name), None)

    def _load_by_path(self, path: Path) -> Optional["FontFile"]:
        if path.exists() is True:
            return FontFile(path)

    def store_font(self, font: "FontFile") -> None:
        self._name_data[font.name] = font
        self._family_and_name_data[(font.family_name, font.name)] = font
        self._file_path_data[font.file_path] = font

    def __getitem__(self, key: Union[str, tuple[str, str], Path]) -> "FontFile":
        if isinstance(key, Path):
            try:
                font = self._file_path_data[key]
            except KeyError as e:
                font = self._load_by_path(key)
                if font is None:
                    raise e
                self.store_font(font)

        elif isinstance(key, tuple):
            try:
                font = self._family_and_name_data[key]
            except KeyError as e:
                font = self._load_by_family_and_name(family_name=key[0], name=key[1])
                if font is None:
                    raise e
                self.store_font(font)

        elif isinstance(key, str):
            try:
                font = self._name_data[key]
            except KeyError as e:
                font = self._load_by_name(key)
                if font is None:
                    raise e
                self.store_font(font)

        return font


FONT_STORAGE = _Font_Cache()

# region [Main_Exec]


if __name__ == '__main__':
    from pympler.asizeof import asizeof
    from gidapptools.general_helper.conversion import bytes2human

    # for i in iter_all_fonts():
    #     print(i)

    print(FONT_STORAGE["Viking Squad Halftone"])
    print(FONT_STORAGE["Viking Squad Halftone"])

    print(FONT_STORAGE[('Source Sans Pro Black', 'Source Sans Pro Black')])

# endregion [Main_Exec]
