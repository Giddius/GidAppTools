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

import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import (TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, ForwardRef, final, Callable,
                    no_type_check, no_type_check_decorator, NamedTuple, overload, get_type_hints, cast, Protocol, runtime_checkable, NoReturn, NewType, Literal, AnyStr, IO, BinaryIO, TextIO, Any)
from collections import Counter, ChainMap, deque, defaultdict
from collections.abc import (AsyncGenerator, AsyncIterable, AsyncIterator, Awaitable, ByteString, Callable, Collection, Container, Coroutine, Generator,
                             Hashable, ItemsView, Iterable, Iterator, KeysView, Mapping, MappingView, MutableMapping, MutableSequence, MutableSet, Reversible, Sequence, Set, Sized, ValuesView)
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property, cache
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, wait, as_completed, ALL_COMPLETED, FIRST_EXCEPTION, FIRST_COMPLETED


if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    ...

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def get_parent_class(in_class: type) -> Union[type, None]:
    try:
        return in_class.mro()[1]
    except IndexError:
        return None


def iter_all_child_classes(start_class: type) -> Generator[type, None, None]:
    for child_class in start_class.__subclasses__():
        yield child_class
        yield from iter_all_child_classes(child_class)


CLASS_TREE_NODE_KLASS_TYPE = TypeVar("CLASS_TREE_NODE_KLASS_TYPE", bound=type)


class ClassTreeNode(Generic[CLASS_TREE_NODE_KLASS_TYPE]):

    def __init__(self, klass: CLASS_TREE_NODE_KLASS_TYPE) -> None:
        self._klass = klass
        self._parent_node: Union["ClassTreeNode", None] = None
        self._child_nodes: tuple["ClassTreeNode"] = tuple()

    @property
    def klass(self) -> CLASS_TREE_NODE_KLASS_TYPE:
        return self._klass

    @property
    def parent_node(self) -> Union["ClassTreeNode", None]:
        return self._parent_node

    @property
    def child_nodes(self) -> tuple["ClassTreeNode"]:
        return self._child_nodes

    def set_parent_node(self, parent_node: "ClassTreeNode") -> None:
        self._parent_node = parent_node

    def add_child_node(self, child_node: "ClassTreeNode") -> None:
        self._child_nodes = self._child_nodes + (child_node,)

    def get_child_by_klass(self, klass: CLASS_TREE_NODE_KLASS_TYPE) -> "ClassTreeNode":
        result = next((child for child in self.child_nodes if child.klass is klass), None)
        if result is None:
            raise KeyError(f"{self!r} has no child_node for klass{klass!r}.")

        return result

    def get_child_by_klass_recursively(self, klass: CLASS_TREE_NODE_KLASS_TYPE) -> Union["ClassTreeNode", None]:

        def _iter_child_node_recursive(start_node: "ClassTreeNode") -> Generator["ClassTreeNode", None, None]:
            for _child_node in start_node.child_nodes:
                yield _child_node
                yield from _iter_child_node_recursive(_child_node)
        if klass is self.klass:
            return self
        for child_node in _iter_child_node_recursive(self):
            if child_node.klass is klass:
                return child_node

        raise KeyError(f"{self!r} has no child_node recursively for klass{klass!r}.")

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(klass={self.klass!r})'


class ClassTree:

    def __init__(self, start_class: CLASS_TREE_NODE_KLASS_TYPE) -> None:
        self.root: ClassTreeNode = ClassTreeNode(start_class)

    def _fill(self) -> None:
        for child_class in iter_all_child_classes(self.root.klass):

            parent_node = self.root.get_child_by_klass_recursively(get_parent_class(child_class))

            if parent_node is None:
                print("--------------------")
                print(f"{child_class=}")
                print(f"{get_parent_class(child_class)=}")
                print(f"{self.root.child_nodes=}")
                print("--------------------")
                # parent_node = self.root
            parent_node.add_child_node(ClassTreeNode(child_class))

            print("=============================")

    def draw(self, engine: str = "ASCII") -> None:
        print(f"{self.root.klass.__name__}")

        for child_node in self.root.child_nodes:
            print(f"    ├─{child_node.klass.__name__}")
            for sub_child_node in child_node.child_nodes:
                print(f"    │     ├─{sub_child_node.klass.__name__}")
            print("    │")


        # region [Main_Exec]
if __name__ == '__main__':
    import pp
    from gidapptools.errors import GidAppToolsBaseError
    xxx = ClassTree(GidAppToolsBaseError)
    xxx._fill()
    xxx.draw()

# endregion [Main_Exec]
