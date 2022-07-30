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
import attrs
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.conversion.converter_grammar import ConverterSpecData, reverse_replace_value_words


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def converter_data_to_string(converter_data: "ConverterSpecData") -> str:
    text = converter_data["typus"]
    if converter_data["kw_arguments"]:
        sub_args = []
        for k, v in converter_data["kw_arguments"].items():
            sub_args.append(f"{k}={reverse_replace_value_words(v)}")

        text += "(" + ', '.join(sub_args) + ")"
    return text


class SpecItem:
    __slots__ = ("_section_name",
                 "_key_name",
                 "_converter_data",
                 "_verbose_name",
                 "_default",
                 "_short_description",
                 "_gui_visible",
                 "_implemented",
                 "_default_converter_data")

    def __init__(self,
                 section_name: str,
                 key_name: str,
                 converter_data: Union["ConverterSpecData", MiscEnum],
                 verbose_name: str = MiscEnum.NOTHING,
                 default: Union[None, str, MiscEnum] = MiscEnum.NOTHING,
                 short_description: str = MiscEnum.NOTHING,
                 gui_visible: bool = MiscEnum.NOTHING,
                 implemented: bool = MiscEnum.NOTHING,
                 default_converter_data: Union["ConverterSpecData", MiscEnum] = MiscEnum.NOTHING) -> None:
        self._section_name = section_name
        self._key_name = key_name
        self._converter_data = converter_data
        self._verbose_name = verbose_name
        self._default = default
        self._short_description = short_description
        self._gui_visible = gui_visible
        self._implemented = implemented
        self._default_converter_data = default_converter_data

    @property
    def is_section_default(self) -> bool:
        return self.key_name == "__default__"

    @property
    def section_name(self) -> str:
        return self._section_name

    @property
    def key_name(self) -> str:
        return self._key_name

    @property
    def converter_data(self) -> Union["ConverterSpecData", MiscEnum]:
        if self._converter_data is MiscEnum.NOTHING:
            return self._default_converter_data
        return self._converter_data

    @property
    def verbose_name(self) -> str:
        if self._verbose_name is MiscEnum.NOTHING:
            return self.key_name.replace("_", " ").title()
        return self._verbose_name

    @property
    def default(self) -> Union[None, str, MiscEnum]:
        return self._default

    @property
    def short_description(self) -> str:
        return self._short_description

    @property
    def gui_visible(self) -> bool:
        return self._gui_visible

    @property
    def implemented(self) -> bool:
        return self._implemented

    def __repr__(self) -> str:
        param_strings = []
        for attr_name in (n for n in self.__slots__ if n != "_default_converter_data"):

            name = attr_name.removeprefix("_")

            param_strings.append(f"{name}={getattr(self, name)!r}")

        params_text = ", ".join(param_strings)

        return f'{self.__class__.__name__}({params_text})'

    def to_json(self) -> dict[str, object]:
        _out = {}
        for attr_name in (n for n in self.__slots__ if n not in {"_default_converter_data", "_section_name", "_key_name"}):
            attr_value = getattr(self, attr_name)
            if attr_value is MiscEnum.NOTHING:
                continue

            if attr_name == "_converter_data":
                attr_name = "converter"
                attr_value = converter_data_to_string(attr_value)

            _out[attr_name.removeprefix("_")] = attr_value
        return _out


# region[Main_Exec]
if __name__ == '__main__':
    x = SpecItem("sec", "key", {})
    print(x)

# endregion[Main_Exec]
