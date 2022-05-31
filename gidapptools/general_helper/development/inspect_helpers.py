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
from importlib.metadata import metadata
from pkg_resources import DistributionNotFound
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader, ModuleSpec, FileFinder
from types import ModuleType
import typing

import attrs
import pkgutil
import ast
import gidapptools
from importlib import import_module
from gidapptools.errors import MissingOptionalDependencyError

with MissingOptionalDependencyError.try_import("gidapptools"):
    import isort
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ClassNameFinder(ast.NodeVisitor):

    def __init__(self) -> None:
        super().__init__()
        self.class_names: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.class_names.append(node.name)
        self.generic_visit(node)

    def get_unique_class_names(self) -> tuple[str]:
        class_names = set(self.class_names)
        return tuple(sorted(class_names, key=lambda x: (not x.startswith("Q"), x.casefold())))


@attrs.define(frozen=True, slots=True)
class SubModule:
    name: str
    qualname: str
    package: str
    module_info: pkgutil.ModuleInfo = attrs.field(default=None)

    @classmethod
    def from_module_info(cls, in_module_info: pkgutil.ModuleInfo) -> "SubModule":
        name = in_module_info.name.split('.')[-1]
        qualname = in_module_info.name
        package = in_module_info.name.split('.')[0]

        return cls(name=name, qualname=qualname, module_info=in_module_info, package=package)

    @property
    def doc(self) -> str:
        doc = self.module.__doc__
        if doc is None and self.path.suffix == ".pyd":
            typing_file = self.path.with_suffix(".pyi")
            if typing_file.is_file() is True:
                tree = ast.parse(typing_file.read_text(encoding='utf-8', errors='ignore'))
                doc = ast.get_docstring(tree)

        if doc is not None:
            doc = inspect.cleandoc(doc)
        return doc

    @property
    def meta_data(self) -> dict[str, Any]:
        return dict(metadata(self.package))

    @property
    def path(self) -> Path:
        return Path(self.module.__file__)

    @property
    def module(self) -> ModuleType:
        return import_module(self.qualname, self.package)

    @property
    def import_string(self) -> str:
        import_path = self.qualname.rsplit('.', 1)[0]
        return f"from {import_path} import {self.name}"

    @property
    def all_members_import_string(self) -> str:
        text = f"from {self.qualname} import ({', '.join(self.member_names)})"

        return isort.code(text, line_length=200).strip()

    @property
    def member_names(self) -> list[str]:

        def _check(_name: str, _obj: object) -> bool:
            return not any([
                getattr(_obj, "__module__", None) != self.module.__name__,
                inspect.ismodule(_obj),
                inspect.isbuiltin(_obj),
                _name.startswith("_"),
                _name.endswith("__")
            ])

        def _sort_key(in_name: str) -> tuple:
            norm_name = in_name.casefold()
            has_upper_q_prefix = in_name.startswith("Q")
            has_lower_q_prefix = in_name.startswith("q")

            return (not has_upper_q_prefix, not has_lower_q_prefix, norm_name, len(norm_name))

        _out = set()
        for name, obj in inspect.getmembers(self.module):
            if _check(name, obj) is False:
                continue

            _out.add(name)

        return tuple(sorted(_out, key=_sort_key))

    def to_dict(self, for_json: bool = False) -> dict[str, Any]:

        def _std_serialize(inst: "SubModule", field_name: str, value: Any) -> Any:
            match value:
                case pkgutil.ModuleInfo:
                    raise RuntimeError("Module info should not hit this")
            return value

        def _json_serialize(inst: "SubModule", field_name: str, value: Any) -> Any:
            match value:

                case Path():
                    return value.as_posix()

                case float():
                    return str(value)

                case tuple():
                    return [_json_serialize(inst, field_name, i) for i in value]

                case set():
                    return [_json_serialize(inst, field_name, i) for i in value]

                case ModuleType():
                    _out = {'name': value.__name__,
                            "file": value.__file__,
                            "package": value.__package__}
                    if _out["file"] is not None:
                        _out["file"] = Path(_out["file"]).as_posix()
                    return _out

                case str():
                    return value

                case list():
                    return [_json_serialize(inst, field_name, i) for i in value]

                case dict():
                    return {_json_serialize(inst, field_name, k): _json_serialize(inst, field_name, v) for k, v in value.items()}

                case int():
                    return value

                case None:
                    return value

                case _:
                    return str(value)

        def _filter(field_name: str, value: Any) -> bool:
            match field_name:
                case "module_info":
                    return False

            return True

        _out = {}

        attrs_attribute_names = [field.name for field in attrs.fields(self.__class__)]
        extra_attribute_names = ["path", "doc", "module", "import_string", "all_members_import_string", "member_names"]

        attribute_names = attrs_attribute_names + extra_attribute_names

        _serialize = _std_serialize if for_json is False else _json_serialize

        for name in attribute_names:
            value = getattr(self, name)
            if _filter(name, value) is False:
                continue
            serialized_value = _serialize(self, name, value)
            _out[name] = serialized_value
        return _out


def get_all_sub_modules(in_module: ModuleType) -> dict[str, SubModule]:
    _out = {}
    for info in pkgutil.walk_packages(in_module.__path__, in_module.__package__ + '.'):
        sub_module = SubModule.from_module_info(info)
        _out[sub_module.name] = sub_module
    return {k: v for k, v in sorted(_out.items(), key=lambda x: (x[0].startswith("_"), x[1].qualname, len(x[1].qualname)))}


# region[Main_Exec]
if __name__ == '__main__':
    pass


# endregion[Main_Exec]
