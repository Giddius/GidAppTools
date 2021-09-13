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

from gidapptools.utility import NamedMetaPath, MiscEnum
from gidapptools.errors import NotSetupError, NoFactoryFoundError, MetaItemNotFoundError
from gidapptools.meta_data.config_kwargs import ConfigKwargs
from gidapptools.types import general_path_type

from gidapptools.meta_data.meta_info import MetaInfoFactory, MetaInfo
from gidapptools.meta_data.meta_paths import MetaPathsFactory, MetaPaths
from gidapptools.abstract_classes.abstract_meta_factory import AbstractMetaFactory

# REMOVE_BEFORE_BUILDING_DIST
from gidapptools.utility._debug_tools import dprint

print = dprint

# end REMOVE_BEFORE_BUILDING_DIST

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

META_FACTORY_TYPE = Union[MetaInfoFactory, MetaPathsFactory]

META_ITEMS_TYPE = Any


class AppMeta:
    factories: dict[str, META_FACTORY_TYPE] = {'meta_info': MetaInfoFactory,
                                               'meta_paths': MetaPathsFactory}

    default_base_configuration = {}

    def __init__(self) -> None:
        self.meta_info: MetaInfo = None
        self.meta_paths: MetaPaths = None
        self.other_items: dict[str, Any] = {}
        self.is_setup = False

    @property
    def all_item_names(self) -> list[str]:
        all_item_names = ['meta_info', 'meta_paths'] + list(self.other_items.values())
        return all_item_names

    @property
    def all_items(self) -> list[META_ITEMS_TYPE]:
        return [self.meta_info, self.meta_paths] + list(self.other_items.values())

    def check_is_setup(self):
        if self.is_setup is False:
            raise NotSetupError(f'{self.__class__.__name__!r} has to set up from the base_init_file first!')

    @classmethod
    def set_meta_info_factory(cls, factory) -> None:
        if not isinstance(factory, AbstractMetaFactory):
            raise TypeError(f"'factory' needs to be a subclass of {AbstractMetaFactory.__name__!r}")
        cls.factories['meta_info'] = factory

    @classmethod
    def set_meta_paths_factory(cls, factory) -> None:
        if not isinstance(factory, AbstractMetaFactory):
            raise TypeError(f"'factory' needs to be a subclass of {AbstractMetaFactory.__name__!r}")
        cls.factories['meta_paths'] = factory

    @classmethod
    def register(cls, name: str, factory: object) -> None:
        cls.factories[name] = factory

    def __getitem__(self, item_name) -> META_ITEMS_TYPE:
        self.check_is_setup()
        if item_name in {'meta_info', 'meta_paths'}:
            return getattr(self, item_name)

        _out = self.other_items.get(item_name)
        if _out is None:
            raise MetaItemNotFoundError(item_name, self.all_item_names)
        return _out

    def get(self, item_name: str = None) -> META_ITEMS_TYPE:
        if item_name is None:
            self.check_is_setup()
            return {'meta_info': self.meta_info, 'meta_paths': self.meta_paths} | self.other_items.copy()
        return self[item_name]

    def __contains__(self, item_name: str) -> bool:
        return item_name in self.all_item_names

    def _initialize_other_app_meta_items(self, config_kwargs: ConfigKwargs) -> None:
        other_app_meta_items = config_kwargs.get('other_app_meta_items', [])
        for other_item_name in other_app_meta_items:
            if other_item_name not in self.factories:
                raise NoFactoryFoundError(other_item_name)
            self.other_items[other_item_name] = self.factories.get(other_item_name).build(config_kwargs=config_kwargs)

    def _initialize_data(self, config_kwargs: ConfigKwargs) -> None:
        self.meta_info = self.factories['meta_info'].build(config_kwargs=config_kwargs)
        self.meta_paths = self.factories['meta_paths'].build(config_kwargs=config_kwargs)

    def setup(self, init_path: general_path_type, **kwargs) -> None:
        base_configuration = self.default_base_configuration.copy() | {'init_path': init_path}
        config_kwargs = ConfigKwargs(base_configuration=base_configuration, **kwargs)

        self._initialize_data(config_kwargs=config_kwargs)
        self._initialize_other_app_meta_items(config_kwargs=config_kwargs)

        self.is_setup = True

    def clean_up(self, **kwargs) -> None:
        """
        possible kwargs:
            remove_all_paths: bool, default=False, remove all paths that were created by meta_paths
            dry_run:bool, default=False, only prints a message, and does not do actuall clean up
        """

        for item in self.all_items:
            item.clean_up(**kwargs)


app_meta = AppMeta()


def setup_meta_data(init_path: general_path_type, **kwargs) -> None:
    app_meta.setup(init_path=Path(init_path), **kwargs)


def get_meta_item(item_name: str = None) -> Union[dict[str, META_ITEMS_TYPE], META_ITEMS_TYPE]:
    return app_meta.get(item_name)


def get_meta_info() -> MetaInfo:
    return app_meta['meta_info']


def get_meta_paths() -> MetaPaths:
    return app_meta['meta_paths']


    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
