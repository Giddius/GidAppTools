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

import pyparsing as pp
import pyparsing.common as ppc
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


class Token:

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" + ', '.join(f"{k}={v!r}" for k, v in vars(self).items()) + ')'


class IniToken(Token, metaclass=ABCMeta):
    spec_data = None

    def add_comment(self, comment: "Comment") -> None:
        self.comments.append(comment.content)


class Comment(Token):
    def __init__(self, content: str) -> None:
        self.content = content.strip()

    def __str__(self) -> str:
        return self.content


class Section(IniToken):

    def __init__(self, name: str) -> None:
        self.name = name
        self.comments = []
        self.entries = {}

    def add_entry(self, entry: "Entry") -> None:
        self.entries[entry.key] = entry

    def get(self, key, default=None) -> Any:
        try:
            return self.entries[key].get_value()
        except KeyError:
            return default

    def as_dict(self) -> dict[str, dict[str, str]]:
        data = {self.name: {}}
        for entry in self.entries.values():
            data[self.name] |= entry.as_dict()
        return data


class Entry(IniToken):

    def __init__(self, key: str, value: str) -> None:
        self.key = key.strip()
        self.value = value.lstrip()
        self.comments = []

    def get_value(self) -> Any:
        return self.value

    def as_dict(self) -> dict[str, str]:
        return {self.key: self.value}


class TokenFactory:

    def __init__(self, token_map: dict[str, type] = None) -> None:
        self.token_map = {'comment': Comment,
                          'section_name': Section,
                          'entry': Entry}
        if token_map is not None:
            self.token_map |= token_map

    def parse_action(self, tokens: pp.ParseResults) -> Token:
        name = tokens.get_name()
        token_class = self.token_map[name]
        return token_class(*tokens)

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
