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
from rich import print as rprint, inspect as rinspect
from rich.console import Console as RichConsole, ConsoleOptions
from rich.tree import Tree
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
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


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
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
