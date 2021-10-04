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
import click
from rich.console import Console as RichConsole
from rich.table import Table
from rich import box
from rich.markup import escape
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
CONSOLE = RichConsole(soft_wrap=True)
# endregion[Constants]


@click.group(name="appmeta")
def appmeta_cli():
    ...


@appmeta_cli.command(help="Lists all available Plugins")
def plugins():
    from gidapptools.meta_data.interface import app_meta
    table = Table(title="[b u light_steel_blue3]AVAILABLE APPMETA-PLUGINS[/b u light_steel_blue3]")
    table.add_column("Plugin Item", style="i chartreuse2 on grey15", header_style="b white on grey37", justify="center", no_wrap=True)
    table.add_column('Module', style="b light_slate_blue on grey15", header_style="b white on grey37", justify="center", no_wrap=True)
    table.add_column('File', style="u dark_khaki on grey15", header_style="b white on grey37", justify="center", no_wrap=True)

    for data in app_meta.plugin_data:
        table.add_row(data.get("product_name"), data.get("module"), f":open_file_folder: [link file://{data.get('file')}]{escape(data.get('file'))}")
    CONSOLE.print("")
    CONSOLE.print(table)


@appmeta_cli.command()
def base_settings():
    from gidapptools.meta_data.interface import app_meta
    CONSOLE.print(app_meta.default_base_configuration)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
