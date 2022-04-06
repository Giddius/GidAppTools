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
from textwrap import dedent
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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr
from collections.abc import Mapping
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
import mdformat
from tabulate import tabulate
from gidapptools.gid_scribe.general.abstract_document_style import DocumentStyleLanguage, DispatchOn
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class Part:
    dispatch_on: DispatchOn = None

    def __init__(self) -> None:
        self._document: "Document" = None
        self._parent: "Part" = None

    @property
    def style_language(self) -> "DocumentStyleLanguage":
        return self.document.style_language

    @property
    def document(self) -> "Document":
        if self._document is not None:
            return self._document
        if isinstance(self._parent, Document):
            return self._parent

        return self._parent.document

    @document.setter
    def document(self, document: "Document") -> None:
        self.set_document(document)

    def set_document(self, document: "Document") -> None:
        self._document = document

    @property
    def raw_text(self) -> str:
        return ""

    @property
    def text(self) -> str:
        return self.style_language.generate_text(self)

    def render(self) -> str:
        text = self.text
        return text


class ContainablePart(Part):

    def __init__(self) -> None:
        super().__init__()
        self._parts: list["Part"] = []

    @property
    def document(self) -> "Document":
        return super().document

    @document.setter
    def document(self, document: "Document") -> None:
        self._document = document
        for part in self._parts:
            part.document = self.document

    def render(self) -> str:
        text = super().render()
        for part in self._parts:
            text += '\n' + part.render()
        return text

    def add_part(self, part: "Part") -> None:
        part._parent = self
        self._parts.append(part)


class Image(Part):
    dispatch_on: DispatchOn = DispatchOn.IMAGE

    def __init__(self, file_path: os.PathLike, alt_text: str = None, title_text: str = None, center: bool = False) -> None:
        super().__init__()
        self.center = center
        self.raw_file_path = Path(file_path)
        self.alt_text = alt_text or "image"
        self._title_text = title_text or ""

    @property
    def title_text(self) -> str:
        if self._title_text:
            return f'"{self._title_text}"'

        return ""

    @property
    def file_path(self) -> Path:
        if self.document.output_file:
            return self.raw_file_path.relative_to(self.document.output_file.parent)
        return self.raw_file_path

    @property
    def text(self) -> str:
        if self.center is False:
            return f"![{self.alt_text}]({self.file_path.as_posix()} {self.title_text})"
        elif self.center is True:
            return dedent(f"""
                    <center>
                        <img src="{self.file_path.as_posix()}" title="{self.title_text.strip('"')}" alt="{self.alt_text}">
                    </center>
                    """).strip()


class Headline(ContainablePart):
    dispatch_on: DispatchOn = DispatchOn.HEADLINE

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    @property
    def raw_text(self) -> str:
        return self._text


class Document:
    default_config: dict[str, Any] = {}

    def __init__(self,
                 style_language_class: type["DocumentStyleLanguage"],
                 output_file: os.PathLike = None,
                 top_headline: str = None,
                 top_image: Path = None,
                 **config_kwargs) -> None:
        self.style_language_class = style_language_class
        self.config: dict[str, Any] = self.default_config | config_kwargs
        self.style_language: "DocumentStyleLanguage" = self.style_language_class(self, self.config)
        self.parts: list = []
        self.output_file = Path(output_file).resolve() if output_file else None
        self.top_headline = top_headline
        self._top_image = top_image

    def render(self) -> str:
        text = ""
        if self.top_headline is not None:
            text += dedent(f"""
                    <center>
                        <h1>{self.top_headline}</h1>
                    </center>
                    """).strip() + '\n'
        if self._top_image is not None:
            part = Image(self._top_image, center=True, title_text=self.top_headline or "")
            part.set_document(self)
            text += part.text + "\n\n"

        for part in self.parts:
            text += part.render() + '\n\n'
        return self.style_language.format_text(text)

    def to_file(self, file_path: os.PathLike = None) -> None:
        if file_path is not None:
            self.output_file = Path(file_path).resolve()
        self.output_file.write_text(self.render(), encoding='utf-8', errors='ignore')

    def add_part(self, part: "Part") -> None:
        part._parent = self
        self.parts.append(part)


# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
