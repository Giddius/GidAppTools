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
from gidapptools.gid_config.parser.tokens import Section, Entry, Comment, TokenFactory, Token
from gidapptools.gid_config.parser.grammar import BaseIniGrammar
from gidapptools.gid_config.parser.config_data import ConfigData
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseIniParser:
    comment_regex = re.compile(r'#.*')

    def __init__(self,
                 config_data_item: ConfigData,
                 grammar_class: BaseIniGrammar = None,
                 token_factory: TokenFactory = None,
                 value_separator: str = '=',
                 comment_indicator: str = '#',
                 remove_comments: bool = False) -> None:
        self.config_data = config_data_item
        grammar_class = BaseIniGrammar if grammar_class is None else grammar_class

        self.grammar_item = grammar_class(value_separator=value_separator, comment_indicator=comment_indicator, token_factory=token_factory)
        self.remove_comments = remove_comments

        self.grammar: pp.ParserElement = None

    def _strip_comments(self, text: str) -> str:
        text = self.comment_regex.sub('', text)
        return text

    def pre_process(self, text: str) -> str:
        if self.remove_comments is True:
            text = self._strip_comments(text)
        return text

    def _parse(self, text: str) -> list[Token]:
        temp_comments = []
        temp_sections = []
        self.config_data.clear_sections()

        for tokens in self.grammar.search_string(text):

            token = tokens[0]

            if isinstance(token, Section):
                token.comments += temp_comments
                temp_comments = []
                temp_sections.append(token)
                self.config_data.add_section(token)

            elif isinstance(token, Entry):
                token.comments += temp_comments
                temp_comments = []
                temp_sections[-1].entries.append(token)

            elif isinstance(token, Comment):
                temp_comments.append(token)

        return self.config_data

    def parse(self, text: str) -> dict[str, str]:
        if self.grammar is None:
            self.grammar = self.grammar_item.get_grammar()
        text = self.pre_process(text)
        return self._parse(text)


# region[Main_Exec]


if __name__ == '__main__':

    x = BaseIniParser(remove_comments=False)
    yy = x.parse(Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Gid_Scratches\gid_scratch\check_w_comments.ini").read_text(encoding='utf-8'))
    pprint(yy)
# endregion[Main_Exec]
