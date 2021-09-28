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

import random

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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Literal
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
from collections import deque

from rich.console import Console as RichConsole, HighlighterType, RichCast, ConsoleRenderable
from rich.align import AlignMethod
from rich.text import TextType
from rich.rule import Rule
from rich.theme import Theme
from rich.style import StyleType, Style
from rich.emoji import EmojiVariant
from rich._log_render import FormatTimeCallable
import attr
from attr.converters import default_if_none
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

NEW_DEFAULT_CONSOLE_KWARGS = {'soft_wrap': True}


@ attr.s(auto_attribs=True, auto_detect=True)
class ExtraConsoleConfiguration:
    use_output_numbering: bool = attr.ib(converter=default_if_none(False))
    use_rule_seperator: bool = attr.ib(converter=default_if_none(False))
    use_extra_newline_pre: bool = attr.ib(converter=default_if_none(False))
    use_extra_newline_post: bool = attr.ib(converter=default_if_none(False))
    use_prefix: bool = attr.ib(converter=default_if_none(False))

    output_numbering_template: str = attr.ib(converter=default_if_none("Output No. {number}"))
    rule_seperator_char: str = attr.ib(converter=default_if_none('-'))
    prefix: str = attr.ib(converter=default_if_none('-->'))
    multiline_indent: int = attr.ib(converter=default_if_none(0))

    @property
    def actual_mutlitline_indent(self) -> int:
        return len(self.prefix) + 2 + self.multiline_indent

    @classmethod
    def from_console_kwargs(cls, console_kwargs: dict[str, Any]) -> tuple["ExtraConsoleConfiguration", dict[str, Any]]:
        extra_kwargs = {}
        for field in attr.fields(cls):
            extra_kwargs[field.name] = console_kwargs.pop(field.name, None)
        return cls(**extra_kwargs), console_kwargs

    def as_dict(self) -> dict[str, Any]:
        return attr.asdict(self)


class GidPrintFormater:
    output_number: int = 0

    def __init__(self, extra_config: ExtraConsoleConfiguration) -> None:
        self.extra_config = extra_config

    def increment_output_number(self):
        self.output_number += 1

    def _handle_multiline_item(self, text_part: Union[str, Rule]) -> Union[str, Rule]:
        if not isinstance(text_part, str):
            return text_part
        if '\n' not in text_part:
            return text_part
        _indent = ' ' * self.extra_config.actual_mutlitline_indent
        return _indent.join(sub_part for sub_part in text_part.splitlines(keepends=True))

    def format(self, *print_args) -> str:
        self.increment_output_number()

        text_parts = deque(print_args)

        if self.extra_config.use_prefix is True:
            text_parts = deque(self._handle_multiline_item(part) for part in text_parts)

            text_parts.appendleft(self.extra_config.prefix)

        if self.extra_config.use_extra_newline_pre is True:
            text_parts.appendleft('\n')
        if self.extra_config.use_extra_newline_post is True:
            text_parts.append('\n')

        title = ''
        if self.extra_config.use_output_numbering is True:
            title = self.extra_config.output_numbering_template.format(number=self.output_number)

        if self.extra_config.use_rule_seperator is True:
            rule = Rule(title=title, characters=self.extra_config.rule_seperator_char)
            text_parts.appendleft(rule)

        elif title != '':
            text_parts.appendleft('\n')
            text_parts.appendleft(title)

        return text_parts


class GidRichConsole(RichConsole):
    output_number: int = 0

    def __init__(self, **console_kwargs):
        console_kwargs = NEW_DEFAULT_CONSOLE_KWARGS | console_kwargs
        self.extra_config, console_kwargs = ExtraConsoleConfiguration.from_console_kwargs(console_kwargs)
        self.formatter = GidPrintFormater(self.extra_config)
        self.console_kwargs = console_kwargs

        super().__init__(**self.console_kwargs)

    def print(self, *args, **kwargs) -> None:
        text_parts = self.formatter.format(*args)
        super().print(*text_parts, **kwargs)

# region[Main_Exec]


if __name__ == '__main__':
    NEW_DEFAULT_CONSOLE_KWARGS |= {'use_output_numbering': True, 'use_rule_seperator': True, 'rule_seperator_char': ',', 'use_prefix': True, 'use_extra_newline_pre': True, 'use_extra_newline_post': True}
    x = GidRichConsole()
    x.print('wuff', 'druff')
    x.print('As I walk through\nthe valley\nof shadow and death')
# endregion[Main_Exec]
