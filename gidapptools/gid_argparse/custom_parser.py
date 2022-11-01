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
import inspect

from typing import TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, Protocol, runtime_checkable, NoReturn, NewType, Literal, AnyStr, IO, BinaryIO, TextIO, Any
from collections.abc import Hashable, Iterable, Mapping, Sequence, MutableMapping, MutableSet, MutableSequence, Callable, Generator, Collection, Container, Coroutine
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import argparse
from gidapptools.general_helper.import_helper import import_from_name, meta_data_from_module
if TYPE_CHECKING:
    ...

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def url_sorter(in_name_and_url: tuple[str, str]):
    order = ("homepage",
             "home-page",
             "documentation",
             "wiki",
             "changelog",
             "changes"
             "source",
             "github",
             "repository",
             "source code",
             "source",
             "download-url")
    name = in_name_and_url[0]
    try:

        return order.index(name.casefold())

    except ValueError:
        return 999


class GidArgumentParser(argparse.ArgumentParser):

    def __init__(self,
                 prog: str = None,
                 usage: str = None,
                 description: str = None,
                 epilog: str = None,
                 parents: Sequence[argparse.ArgumentParser] = None,
                 formatter_class: "argparse._FormatterClass" = argparse.HelpFormatter,
                 prefix_chars: str = '-',
                 fromfile_prefix_chars: str = None,
                 argument_default: Any = None,
                 conflict_handler: str = 'error',
                 add_help: bool = True,
                 allow_abbrev: bool = True,
                 exit_on_error: bool = True,
                 version: str = None,
                 urls: Union[str, Mapping[str, str]] = None) -> None:

        super().__init__(prog=prog,
                         usage=usage,
                         description=description,
                         epilog=epilog,
                         parents=parents or [],
                         formatter_class=formatter_class,
                         prefix_chars=prefix_chars,
                         fromfile_prefix_chars=fromfile_prefix_chars,
                         argument_default=argument_default,
                         conflict_handler=conflict_handler,
                         add_help=add_help,
                         allow_abbrev=allow_abbrev,
                         exit_on_error=exit_on_error)

        self.version = version
        self._urls = urls
        self.standard_arguments: dict[str, argparse.Action] = {}

    @property
    def urls(self) -> dict[str, str]:
        if self._urls is None:
            return {}
        if isinstance(self._urls, str):
            return {"Homepage", self._urls}

        return dict(self._urls)

    def setup_standard_arguments(self) -> Self:
        if self.version:
            self._add_to_standard_arguments(self.add_argument("-v", "--version", action=argparse._VersionAction))

        return self

    def _add_to_standard_arguments(self, action: argparse.Action):
        for opt_string in action.option_strings:
            name = opt_string.strip(self.prefix_chars)
            self.standard_arguments[name] = action

    def format_help(self):
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)
        for url_name, url in sorted(self.urls.items(), key=url_sorter):
            formatter.add_text(f"{url_name}: {url}")

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        if self.epilog:
            formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()

    @classmethod
    def from_meta_data(cls, package_name: str, pretty_name: str = None, **kwargs) -> "GidArgumentParser":
        package_module = import_from_name(package_name)
        meta_data = meta_data_from_module(package_module)
        init_kwargs = {}
        init_kwargs["version"] = getattr(package_module, "__version__", meta_data["version"])
        init_kwargs["prog"] = pretty_name or meta_data["name"]
        init_kwargs["description"] = meta_data.get("summary") or (inspect.getdoc(package_module) or "")
        init_kwargs["urls"] = meta_data.all_urls

        init_kwargs = init_kwargs | kwargs
        return cls(**init_kwargs)
# region[Main_Exec]


if __name__ == '__main__':
    x = import_from_name("gidapptools")
    y = meta_data_from_module(x)
    pprint(y)

# endregion[Main_Exec]
