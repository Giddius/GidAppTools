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
from typing import (TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, ForwardRef, final,
                    no_type_check, no_type_check_decorator, overload, get_type_hints, cast, Protocol, runtime_checkable, NoReturn, NewType, Literal, AnyStr, IO, BinaryIO, TextIO, Any)
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
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


import PySide6
from PySide6 import (QtCore, QtGui, QtWidgets, Qt3DAnimation, Qt3DCore, Qt3DExtras, Qt3DInput, Qt3DLogic, Qt3DRender, QtAxContainer, QtBluetooth,
                     QtCharts, QtConcurrent, QtDataVisualization, QtDesigner, QtHelp, QtMultimedia, QtMultimediaWidgets, QtNetwork, QtNetworkAuth,
                     QtOpenGL, QtOpenGLWidgets, QtPositioning, QtPrintSupport, QtQml, QtQuick, QtQuickControls2, QtQuickWidgets, QtRemoteObjects,
                     QtScxml, QtSensors, QtSerialPort, QtSql, QtStateMachine, QtSvg, QtSvgWidgets, QtTest, QtUiTools, QtWebChannel, QtWebEngineCore,
                     QtWebEngineQuick, QtWebEngineWidgets, QtWebSockets, QtXml)

from PySide6.QtCore import (QByteArray, QCoreApplication, QDate, QDateTime, QEvent, QLocale, QMetaObject, QModelIndex, QModelRoleData, QMutex,
                            QMutexLocker, QObject, QPoint, QRect, QRecursiveMutex, QRunnable, QSettings, QSize, QThread, QThreadPool, QTime, QUrl,
                            QWaitCondition, Qt, QAbstractItemModel, QAbstractListModel, QAbstractTableModel, Signal, Slot)

from PySide6.QtGui import (QAction, QBrush, QSyntaxHighlighter, QTextFormat, QTextCharFormat, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup)

from string import whitespace, punctuation
from gidapptools.gidapptools_qt.abc.abstract_syntax_highlighting_rule import AbstractSyntaxHighlightRule
from gidapptools.general_helper.color.color_item import Color
from gidapptools.general_helper.general_classes import DecorateAbleList
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

ALL_RULES: DecorateAbleList[type["AbstractSyntaxHighlightRule"]] = DecorateAbleList()


@ALL_RULES
class PunctuationHighlightRule(AbstractSyntaxHighlightRule):

    def __init__(self) -> None:
        self._pattern = re.compile(r"[" + re.escape(r".:,;#=<>|") + r"]")
        self._style_format = self._make_style_format()

    def _make_style_format(self) -> QTextCharFormat:
        style_format = QTextCharFormat()
        style_format.setForeground(Color.get_color_by_name("Orange").qcolor)
        return style_format


@ALL_RULES
class StringHighlightRule(AbstractSyntaxHighlightRule):

    def __init__(self) -> None:
        self._pattern = re.compile(r'(\"[^\"]*\")|(\'[^\']*\')')
        self._style_format = self._make_style_format()

    def _make_style_format(self) -> QTextCharFormat:
        style_format = QTextCharFormat()
        style_format.setForeground(Color.get_color_by_name("MidnightBlue").qcolor)
        return style_format


@ALL_RULES
class IntegerHighlightRule(AbstractSyntaxHighlightRule):
    def __init__(self) -> None:
        self._pattern = re.compile(r"\b\d+\b")
        self._style_format = self._make_style_format()

    def _make_style_format(self) -> QTextCharFormat:
        style_format = QTextCharFormat()
        style_format.setForeground(Color.get_color_by_name("DarkGreen").qcolor)
        return style_format


@ALL_RULES
class FloatHighlightRule(AbstractSyntaxHighlightRule):
    def __init__(self) -> None:
        self._pattern = re.compile(r"\b\d+\.\d+\b")
        self._style_format = self._make_style_format()

    def _make_style_format(self) -> QTextCharFormat:
        style_format = QTextCharFormat()
        style_format.setForeground(Color.get_color_by_name("DarkSalmon").qcolor)
        return style_format


@ALL_RULES
class HexHighlightRule(AbstractSyntaxHighlightRule):
    def __init__(self) -> None:
        self._pattern = re.compile(r"\#[\da-zA-Z]+")
        self._style_format = self._make_style_format()

    def _make_style_format(self) -> QTextCharFormat:
        style_format = QTextCharFormat()
        style_format.setForeground(Color.get_color_by_name("SaddleBrown").qcolor)
        return style_format


@ALL_RULES
class BracketHighlightRule(AbstractSyntaxHighlightRule):
    def __init__(self) -> None:
        self._pattern = re.compile(r"[" + re.escape("{([])}") + r"]")
        self._style_format = self._make_style_format()

    def _make_style_format(self) -> QTextCharFormat:
        style_format = QTextCharFormat()
        style_format.setForeground(Color.get_color_by_name("DimGray").qcolor)
        return style_format


@ALL_RULES
class PythonReprRule(AbstractSyntaxHighlightRule):
    def __init__(self) -> None:
        self._pattern = re.compile(r"[\w\.]*\(.*?\)")
        self._style_format = self._make_style_format()

    def _make_style_format(self) -> QTextCharFormat:
        style_format = QTextCharFormat()
        style_format.setForeground(Color.get_color_by_name("OliveDrab").qcolor)
        return style_format


@ALL_RULES
class PythonDefaultReprRule(AbstractSyntaxHighlightRule):
    def __init__(self) -> None:
        self._pattern = re.compile(r"\<[^\>]*?\>")
        self._style_format = self._make_style_format()

    def _make_style_format(self) -> QTextCharFormat:
        style_format = QTextCharFormat()
        style_format.setForeground(Color.get_color_by_name("DarkGoldenrod").qcolor)
        return style_format

# region [Main_Exec]


if __name__ == '__main__':
    pass

# endregion [Main_Exec]
