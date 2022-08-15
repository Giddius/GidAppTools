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
from threading import RLock
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QCloseEvent, Qt
from PySide6.QtWidgets import QWidget, QMainWindow, QApplication

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SecondaryWindow(QWidget):
    close_signal = Signal(QWidget)

    def __init__(self, parent: QWidget = None, f: Qt.WindowFlags = None, name: str = None) -> None:
        super().__init__(*[i for i in [parent, f] if i is not None])
        self.is_closed: bool = False
        if name is not None:
            self.setObjectName(name)
            self.setWindowTitle(name)

    @property
    def app(self) -> QApplication:
        return QApplication.instance()

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        self.close_signal.emit(self)
        self.is_closed = True

    def __repr__(self) -> str:

        return f'{self.__class__.__name__}'


class WindowReferenceKeeper:

    def __init__(self) -> None:
        self.lock = RLock()
        self._open_windows: list[SecondaryWindow] = []

    def show(self, window: SecondaryWindow) -> SecondaryWindow:
        if not isinstance(window, SecondaryWindow):
            raise TypeError(f"{self.__class__.__name__!r} can only handle windows that are a subclass of {SecondaryWindow.__name__!r}.")
        with self.lock:
            if window not in self._open_windows:
                self._open_windows.append(window)
            window.close_event.connect(self.on_window_close)
            window.show()
            return window

    def on_window_close(self, window: SecondaryWindow) -> None:
        with self.lock:
            try:
                self._open_windows.remove(window)
            except ValueError:
                pass

    def remove_already_closed(self) -> None:
        with self.lock:
            self._open_windows = [w for w in self._open_windows if w.is_closed is False]


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
