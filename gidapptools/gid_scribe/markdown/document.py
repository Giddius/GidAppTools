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
import mdformat

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MarkdownPart:

    def __init__(self) -> None:
        self._document: "MarkdownDocument" = None
        self._parent: "MarkdownPart" = None

    @property
    def document(self) -> "MarkdownDocument":
        if self._document is None:
            if isinstance(self._parent, MarkdownDocument):
                return self._parent
            return self._parent.document
        return self._document

    @document.setter
    def document(self, document: "MarkdownDocument") -> None:
        self.set_document(document)

    def set_document(self, document: "MarkdownDocument") -> None:
        self._document = document

    @property
    def text(self) -> str:
        return ""

    def render(self) -> str:
        text = self.text + '\n\n'
        return text


class MarkdownContainablePart(MarkdownPart):

    def __init__(self) -> None:
        super().__init__()
        self._parts: list["MarkdownPart"] = []

    @property
    def document(self) -> "MarkdownDocument":
        return super().document

    @document.setter
    def document(self, document: "MarkdownDocument") -> None:
        self._document = document
        for part in self._parts:
            part.document = self.document

    def render(self) -> str:
        text = super().render()
        for part in self._parts:
            text += part.render() + '\n\n'
        return text

    def add_part(self, part: "MarkdownPart") -> None:
        part._parent = self
        self._parts.append(part)


class MarkdownHeadline(MarkdownContainablePart):

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text
        self.level: int = None

    def _determine_level(self) -> None:
        header_parent = self
        while True:
            header_parent = header_parent._parent
            if isinstance(header_parent, MarkdownHeadline):
                self.level = header_parent.level + 1
                break
            elif isinstance(header_parent, MarkdownDocument):
                self.level = 1 if header_parent.top_headline is None else 2
                break

    @property
    def text(self) -> str:
        self._determine_level()
        return f"{'#'*self.level} {self._text}\n"


class MarkdownRawText(MarkdownPart):

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    @property
    def text(self) -> str:
        return self._text + "\n"


class MarkdownCodeBlock(MarkdownPart):

    def __init__(self, code_text: str, language: str = "") -> None:
        super().__init__()
        self.code_text = code_text
        self.language = language

    @property
    def text(self) -> str:
        return f"```{self.language}\n{self.code_text}\n```\n"


class MarkdownImage(MarkdownPart):

    def __init__(self, file_path: os.PathLike, alt_text: str = None, title_text: str = None) -> None:
        super().__init__()
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
        return f"![{self.alt_text}]({self.file_path.as_posix()} {self.title_text})"


class MarkdownSimpleList(MarkdownPart):

    def __init__(self, ordered: bool = True, name: str = None) -> None:
        super().__init__()
        self.entries = []
        self.name = name
        self.ordered = ordered

    def add_entry(self, entry: Union[str, "MarkdownPart"]):
        self.entries.append(entry)

    @property
    def text(self) -> str:
        return self.name or ""

    def render(self) -> str:
        text = self.text + '\n'
        prefix = "\t" if self.name is not None else ""
        for idx, item in enumerate(self.entries):
            if self.ordered is True:
                text += f"{prefix}{idx+1}. {item}\n"
            else:
                text += f"{prefix}- {item}\n"
        return text


class MarkdownDocument:
    default_config: dict[str, Any] = {}

    def __init__(self, output_file: os.PathLike = None, top_headline: str = None, top_image: Path = None, ** config_kwargs) -> None:
        self.config: dict[str, Any] = self.default_config | config_kwargs
        self.parts: list = []
        self.output_file = Path(output_file).resolve() if output_file else None
        self.top_headline = top_headline
        self._top_image = top_image

    def render(self) -> str:
        text = ""
        if self.top_headline is not None:
            text += f"# {self.top_headline}\n\n"
        if self._top_image is not None:
            part = MarkdownImage(self._top_image)
            part.set_document(self)
            text += part.text + "\n\n"

        for part in self.parts:
            text += part.render() + '\n\n'
        return mdformat.text(text)

    def to_file(self, file_path: os.PathLike = None) -> None:
        if file_path is not None:
            self.output_file = Path(file_path).resolve()
        self.output_file.write_text(self.render(), encoding='utf-8', errors='ignore')

    def add_part(self, part: "MarkdownPart") -> None:
        part._parent = self
        self.parts.append(part)


# region[Main_Exec]


if __name__ == '__main__':
    d = MarkdownDocument(output_file=r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\blah.md", top_headline="this is it", top_image=r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\gidapptools\data\images\placeholder.png")
    t = MarkdownHeadline("hi")
    d.add_part(t)
    i = MarkdownImage(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tools\reports\coverage\html\favicon_32.png", title_text="woooohoooo")
    t.add_part(i)
    cc = MarkdownCodeBlock("a ='alpha'", "python")
    t.add_part(cc)

    ll = MarkdownSimpleList(ordered=False)
    _ = [ll.add_entry(e) for e in ["first", "second", "third"]]
    t.add_part(ll)
    d.to_file()
# endregion[Main_Exec]
