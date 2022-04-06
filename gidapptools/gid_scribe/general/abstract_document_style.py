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

if TYPE_CHECKING:
    from gidapptools.gid_scribe.general.document import Document, Part, Image
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


@unique
class DispatchOn(Enum):
    DEFAULT = auto()
    IMAGE = auto()
    HEADLINE = auto()


DOCUMENT_STYLE_DISPATCH_TABLE_TYPE = Mapping[DispatchOn, Callable[["Part"], str]]


class DocumentStyleLanguage(ABC):

    def __init__(self, document: "Document", config: dict[str, Any]) -> None:
        self.document = document
        self.config = config
        self._dispatch_table: DOCUMENT_STYLE_DISPATCH_TABLE_TYPE = self._construct_dispatch_table()

    def _construct_dispatch_table(self) -> DOCUMENT_STYLE_DISPATCH_TABLE_TYPE:
        table = {DispatchOn.DEFAULT: self._fallback_generate,
                 DispatchOn.IMAGE: self._generate_image,
                 DispatchOn.HEADLINE: self._generate_image}

        return table

    def _fallback_generate(self, doc_part: "Part") -> str:
        return doc_part.raw_text

    @abstractmethod
    def _generate_image(self, doc_part: "Image") -> str:
        ...

    @abstractmethod
    def _generate_headline(self, doc_part: "Part") -> str:
        ...

    def generate_text(self, doc_part: "Part") -> str:
        _generator = self._dispatch_table.get(doc_part.dispatch_on, self._fallback_generate)
        return _generator(doc_part)

    @abstractmethod
    def format_text(self, text: str) -> str:
        ...


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
