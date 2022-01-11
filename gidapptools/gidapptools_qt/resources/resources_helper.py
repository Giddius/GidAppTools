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
from threading import Lock, RLock
from PySide6.QtGui import QPixmap, QIcon, QImage, QMovie
from PySide6.QtCore import QFile, QSize, Qt, QByteArray

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def make_ressource_name(in_item_name: str, in_section_name: str = None) -> str:
    item_name = in_item_name.rsplit('.', 1)[0]
    if in_section_name:
        return f":/{in_section_name}/{item_name}"
    return f":/{item_name}"


class ResourceTypus(Flag):
    MISC = auto()
    PIXMAP = auto()
    MOVIE = auto()

    @classmethod
    def from_file_path(cls, file_path: Path) -> "ResourceTypus":
        suffix = file_path.suffix.casefold().strip('.')
        if suffix in {"bmp", "jpg", "jpeg", "png", "pbm", "pgm", "ppm", "xbm", "xpm", "svg"}:
            return cls.PIXMAP
        if suffix in {"gif"}:
            return cls.MOVIE
        return cls.MISC


class ResourceItem:
    cache_lock = RLock()
    _cache = {}

    def __init__(self, file_path: str, qt_path: str) -> None:
        self.file_path = Path(file_path)
        self.qt_path = qt_path
        self.prefixes, self.name = self._get_qt_path_parts()

    def get_from_cache(self, key):
        with self.cache_lock:
            return self._cache.get(key, None)

    def store_in_cache(self, key, value):
        with self.cache_lock:
            self._cache[key] = value

    def _get_qt_path_parts(self) -> str:
        as_path = Path(self.qt_path)
        _, *prefixes, name = as_path.parts
        return tuple(prefixes), name.rsplit('.')[0]

    def get_as_file(self) -> QFile:
        from_cache = self.get_from_cache(("file", self.name))
        if from_cache is not None:
            return from_cache

        _out = QFile(self.qt_path)
        self.store_in_cache(("image", self.name), _out)
        return _out

    @classmethod
    def clear_cache(cls):
        with cls.cache_lock:
            cls._cache.clear()


class MiscResourceItem(ResourceItem):
    ...


class PixmapResourceItem(ResourceItem):

    def get_as_pixmap(self, width=None, height=None) -> QPixmap:
        from_cache = self.get_from_cache(("pixmap", self.name, width, height))
        if from_cache is not None:
            return from_cache

        pixmap = QPixmap(self.qt_path)
        if any([width is None, height is None]):
            _out = pixmap
        else:
            _out = pixmap.scaled(QSize(width, height), Qt.KeepAspectRatioByExpanding)
        self.store_in_cache(("pixmap", self.name, width, height), _out)
        return _out

    def get_as_icon(self) -> QIcon:
        from_cache = self.get_from_cache(("icon", self.name))
        if from_cache is not None:
            return from_cache
        _out = QIcon(self.qt_path)
        self.store_in_cache(("icon", self.name), _out)
        return _out

    def get_as_image(self, **kwargs) -> QImage:
        from_cache = self.get_from_cache(("image", self.name))
        if from_cache is not None:
            return from_cache
        _out = QImage(self.qt_path, **kwargs)
        self.store_in_cache(("image", self.name), _out)
        return _out


class MovieRessourceItem(ResourceItem):

    def get_as_movie(self) -> QMovie:
        from_cache = self.get_from_cache(("movie", self.name))
        if from_cache is not None:
            return from_cache
        _out = QMovie(self.qt_path, QByteArray())
        self.store_in_cache(("movie", self.name), _out)
        return _out


_ressource_item_factory_class_table = {ResourceTypus.MISC: MiscResourceItem,
                                       ResourceTypus.PIXMAP: PixmapResourceItem,
                                       ResourceTypus.MOVIE: MovieRessourceItem}


def ressource_item_factory(file_path: str, qt_path: str) -> Union[MiscResourceItem, PixmapResourceItem]:
    file_path = Path(file_path)
    typus = ResourceTypus.from_file_path(file_path)
    return _ressource_item_factory_class_table[typus](file_path=file_path, qt_path=qt_path)


class AllResourceItemsMeta(type):

    def __getattr__(cls, name: str) -> "ResourceItem":
        if any(name.casefold().endswith(f"_{cat}") for cat in cls.categories):
            cat_name = name.split('_')[-1].casefold()
            cls.missing_items[cat_name].add(name)
            return cls.placeholder_image
        raise AttributeError(f"{cls.__name__} has not attribute {name!r}")

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
