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

import PySide6
from PySide6 import (QtCore, QtGui, QtWidgets, Qt3DAnimation, Qt3DCore, Qt3DExtras, Qt3DInput, Qt3DLogic, Qt3DRender, QtAxContainer, QtBluetooth,
                     QtCharts, QtConcurrent, QtDataVisualization, QtDesigner, QtHelp, QtMultimedia, QtMultimediaWidgets, QtNetwork, QtNetworkAuth,
                     QtOpenGL, QtOpenGLWidgets, QtPositioning, QtPrintSupport, QtQml, QtQuick, QtQuickControls2, QtQuickWidgets, QtRemoteObjects,
                     QtScxml, QtSensors, QtSerialPort, QtSql, QtStateMachine, QtSvg, QtSvgWidgets, QtTest, QtUiTools, QtWebChannel, QtWebEngineCore,
                     QtWebEngineQuick, QtWebEngineWidgets, QtWebSockets, QtXml)

from PySide6.QtCore import (QByteArray, QChildEvent, QDynamicPropertyChangeEvent, QCoreApplication, QDate, QDateTime, QEvent, QLocale, QMetaObject, QModelIndex, QModelRoleData, QMutex,
                            QMutexLocker, QObject, QPoint, QRect, QRecursiveMutex, QRunnable, QSettings, QSize, QThread, QThreadPool, QTime, QUrl,
                            QWaitCondition, Qt, QAbstractItemModel, QAbstractListModel, QAbstractTableModel, Signal, Slot)

from PySide6.QtGui import (QAction, QCloseEvent, QBrush, QColor, QConicalGradient, QInputMethodQueryEvent, QMouseEvent, QResizeEvent, QPaintEvent, QPlatformSurfaceEvent, QStatusTipEvent, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup)

from rich.console import Console as RichConsole
import pp
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class JsonOutputter:

    def __init__(self, target_folder: Path, file_stem_suffix: str = None) -> None:
        self.target_folder = target_folder
        self.specific_folder = self.target_folder.joinpath("event_specific_data")
        self.target_folder.mkdir(exist_ok=True, parents=True)
        if self.specific_folder.exists() is True:
            shutil.rmtree(self.specific_folder)
        self.specific_folder.mkdir(exist_ok=True, parents=True)
        self.file_stem_suffix = file_stem_suffix

    def __call__(self, data: dict):
        def _clean_event_name(_event: QEvent) -> str:
            parts = str(_event.type()).split('.')
            while parts[0].casefold() != "qevent":
                _ = parts.pop(0)
            name = '_'.join(parts)
            return name

        event = data.get("event")
        specific = {"event": data.get("event"), "specific": data.pop("specific")}
        file_name = _clean_event_name(event)
        print(file_name)
        if self.file_stem_suffix is not None:
            file_name += f"_{self.file_stem_suffix}"
        file_name += '.json'
        path = self.target_folder.joinpath(file_name)
        if path.is_file() is False:

            with path.open("w", encoding='utf-8', errors='ignore') as f:
                json.dump(data, f, default=str, sort_keys=False, indent=4)

        if specific["specific"]:
            specific_file_name = f"{path.stem}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')}.json"
            specific_path = self.specific_folder.joinpath(specific_file_name)
            with specific_path.open("w", encoding='utf-8', errors='ignore') as f:
                json.dump(specific, f, default=str, sort_keys=False, indent=4)


def _data_getter_class_name(obj: object) -> str:
    try:
        if inspect.isclass(obj):
            return obj.__name__
    except Exception as e:
        print(e)

    try:
        return obj.__class__.__name__
    except Exception as e:
        print(e)

    return "Not able to determine class Name".upper()


def _data_getter_all_subclasses(obj: object) -> tuple[type]:

    if inspect.isclass(obj):
        klass = obj
    else:
        klass = obj.__class__
    all_subclasses = []

    for subclass in klass.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(_data_getter_all_subclasses(subclass))

    return tuple(all_subclasses)


def _data_getter_all_subclasses_names(obj: object) -> tuple[str]:
    return tuple(i.__name__ for i in _data_getter_all_subclasses(obj))


def _data_getter_all_member_names(obj: object) -> tuple[str]:
    return tuple(name for name, obj in inspect.getmembers(obj))


def _data_getter_all_non_param_methods(obj: object) -> tuple[str]:
    meths = []
    for name, obj in inspect.getmembers(obj):
        try:
            if len(inspect.getfullargspec(obj)[0]) <= 1:
                meths.append(name)
        except TypeError:
            continue
    return tuple(meths)


DEFAULT_SPEC_DATA_TO_GET = {QChildEvent: ["polished"],
                            QDynamicPropertyChangeEvent: ["propertyName"],
                            QResizeEvent: ["size", "oldSize"],
                            QStatusTipEvent: ["tip"],
                            QInputMethodQueryEvent: ["queries"],
                            QPlatformSurfaceEvent: ["surfaceEventTypes"],
                            QPaintEvent: ["region", "rect"],
                            QMouseEvent: ["source", "flags"]}

DEFAULT_SPEC_DATA_TO_GET = {k.__name__: v for k, v in DEFAULT_SPEC_DATA_TO_GET.items()}


class EventAnalyzer:
    std_data_to_get: tuple[str] = ("type", "_data_getter_class_name", "_data_getter_all_non_param_methods", "_data_getter_all_subclasses_names", "_data_getter_all_member_names", "spontaneous", "isSinglePointEvent", "isPointerEvent", "isInputEvent")
    specific_data_to_get: dict[str, list] = defaultdict(list, DEFAULT_SPEC_DATA_TO_GET)
    data_getters: dict[str, Callable] = {f.__name__: f for f in [_data_getter_all_member_names, _data_getter_all_subclasses, _data_getter_class_name, _data_getter_all_subclasses_names, _data_getter_all_non_param_methods]}

    def __init__(self, output: Callable = print, output_data: bool = False, only: Iterable[str] = None, exclude: Iterable[str] = None):
        self.output = output
        self.output_data = output_data
        self.only = set(only) if only is not None else only
        self.exclude = set(exclude) if exclude is not None else set()

    def _get_event_data(self, event: QEvent) -> dict[str, Any]:
        std_data = {}
        specific_data = {}
        for to_get in self.std_data_to_get:
            if to_get.startswith("_data_getter_"):
                std_data[to_get.removeprefix("_data_getter_")] = self.data_getters[to_get](event)
            else:
                value = getattr(event, to_get)
                if callable(value):
                    value = value()
                std_data[to_get] = value
        std_data = {k: v for k, v in sorted(std_data.items(), key=lambda x: len(x[0]))}
        for spec_to_get in self.specific_data_to_get[event.__class__.__name__]:
            value = getattr(event, spec_to_get)
            if callable(value):
                value = value()
            specific_data[spec_to_get] = value
        specific_data = {k: v for k, v in sorted(specific_data.items(), key=lambda x: len(x[0]))}
        return {"event": event, "std": std_data, "specific": specific_data}

    def _render_to_string(self, data: dict[str, Any]):
        return pp.fmt(data)

    def analyze(self, event: QEvent) -> Optional[Union[str, dict]]:
        if self.only is not None and event.__class__.__name__ not in self.only:
            return
        if event.__class__.__name__ in self.exclude:

            return
        data = self._get_event_data(event)
        if self.output_data is True:
            return data
        return self._render_to_string(data)

    def __call__(self, event: QEvent) -> None:
        text_or_data = self.analyze(event)
        if text_or_data is not None:
            self.output(text_or_data)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
