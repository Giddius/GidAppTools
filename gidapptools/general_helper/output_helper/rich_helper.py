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
import types
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from string import printable, ascii_letters
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from rich import print as rprint, inspect as rinspect
from rich.console import Console as RichConsole, ConsoleOptions
from rich.tree import Tree
from tempfile import TemporaryFile, TemporaryDirectory, gettempdir
from rich.table import Table
from rich.panel import Panel
from rich.markup import escape
from rich.box import Box
from rich.style import Style, StyleStack
from rich.styled import Styled
from rich.progress import Progress
from rich.pretty import pprint as rpprint, pretty_repr, Pretty as RichPretty
from rich.layout import Layout
from rich.highlighter import Highlighter, NullHighlighter, RegexHighlighter, ReprHighlighter
from rich.text import Text
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.status import Status
from rich.terminal_theme import TerminalTheme
from rich.screen import Screen
from rich.segment import Segment
from rich.rule import Rule
from rich.region import Region
from rich.palette import Palette
from rich.color import Color
from rich.json import JSON
from rich.control import Control
from rich.bar import Bar
from rich.traceback import Trace, Traceback
from rich.tabulate import tabulate_mapping
from gidapptools.general_helper.path_helper import find_file
from tzlocal import get_localzone
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

MY_TERMINAL_THEME = TerminalTheme(
    (40, 40, 40),
    (102, 255, 50),
    [
        (0, 0, 0),
        (15, 140, 220),
        (86, 216, 86),
        (255, 215, 0),
        (98, 96, 180),
        (18, 255, 156),
        (25, 128, 128),
        (192, 192, 192),
    ],
    [
        (128, 128, 128),
        (150, 25, 25),
        (200, 200, 100),
        (150, 150, 25),
        (25, 25, 150),
        (0, 176, 255),
        (213, 121, 255),
        (150, 150, 150),
    ],
)


def dict_to_rich_tree(label: str, in_dict: dict) -> Tree:
    base_tree = Tree(label=label)

    def _handle_sub_dict(in_sub_dict: dict, attach_node: Tree):
        for k, v in in_sub_dict.items():
            key_node = attach_node.add(k)
            if isinstance(v, dict):
                _handle_sub_dict(v, key_node)
            elif isinstance(v, list):
                key_node.add(Panel(',\n'.join(f"{i}" for i in v)))
            else:
                key_node.add(f"{v}")

    _handle_sub_dict(in_dict, base_tree)
    return base_tree


def inspect_object_with_html(obj: object,
                             show_all: bool = False,
                             show_methods: bool = False,
                             show_dunder: bool = False,
                             show_private: bool = False,
                             show_docs: bool = True,
                             show_help: bool = False):

    def _make_title(_obj: Any) -> str:

        title_str = (
            str(_obj)
            if (isinstance(_obj, type) or callable(_obj) or isinstance(_obj, types.ModuleType))
            else str(type(_obj))
        )
        if hasattr(obj, "name") and obj.name != str(_obj):
            title_str += f' -| {_obj.name!r} |-'

        return title_str

    def sanitize_name(name: str) -> str:

        return re.sub(r"\.\s\-\?\!\,\(\)\[\]\<\>\|\:\;\'\"\&\%\$\§\\", '_', name)

    def make_file_name(_obj) -> str:
        if hasattr(_obj, 'name'):
            text = _obj.name

        elif hasattr(_obj, '__name__'):
            text = _obj.__name__
        else:
            text = ''.join(random.choices(ascii_letters, k=random.randint(5, 10)))

        return sanitize_name(text) + '.html'

    with StringIO() as throw_away_file:
        console = RichConsole(soft_wrap=True, record=True, file=throw_away_file)
        title = None
        try:
            title = _make_title(obj)
        except Exception as e:
            print(e)
            title = None
        rinspect(obj=obj,
                 title=title,
                 help=show_help,
                 methods=show_methods,
                 docs=show_docs,
                 private=show_private,
                 dunder=show_dunder,
                 all=show_all,
                 console=console)
        with TemporaryDirectory() as temp_directory:
            out_file = Path(temp_directory).joinpath(make_file_name(obj))

            console.save_html(out_file, theme=MY_TERMINAL_THEME)
            firefox = shutil.which("firefox.exe")
            cmd = f'"{firefox}" -new-window "{str(out_file)}"'

            _cmd = subprocess.run(cmd, check=True, text=True)
            sleep(0.5)


# region[Main_Exec]

if __name__ == '__main__':
    # inspect_object_with_html(, show_all=True, show_help=True),
    pass
# endregion[Main_Exec]
