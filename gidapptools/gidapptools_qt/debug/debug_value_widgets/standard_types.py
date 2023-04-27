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
from decimal import Decimal
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

from PySide6.QtGui import (QAction, QBrush, QClipboard, QMouseEvent, QTextBlock, QTextBlockFormat, QTextCharFormat, QSyntaxHighlighter, QTextOption, QTextCursor, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup)

from gidapptools.gidapptools_qt.helper.syntax_highlighting.rules import ALL_RULES
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    from gidapptools.gidapptools_qt.abc.abstract_syntax_highlighting_rule import AbstractSyntaxHighlightRule

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class DebugValueHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.rules: dict[str:"AbstractSyntaxHighlightRule"] = {}

    def add_rule(self, rule: "AbstractSyntaxHighlightRule"):
        self.rules[rule.name] = rule

    def highlightBlock(self, text: str) -> None:
        for rule in self.rules.values():

            for _format in rule.apply(text, self):

                self.setFormat(*_format)


class DefaultValueWidget(QTextEdit):
    determine_value_widget_func: Callable[[object], QWidget] = None
    value_types: tuple[type] = tuple()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.highlighter: QSyntaxHighlighter = None
        self.is_setup: bool = False

    def setup(self) -> Self:
        if self.is_setup is True:
            return self

        self.highlighter = DebugValueHighlighter(self)
        self.setup_highlighter()
        self.setFontFamily("Lucida Console")
        new_point_size = self.font().pointSize() * 1.25

        self.setFontPointSize(new_point_size)
        self.setReadOnly(True)
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)

        self.is_setup = True
        return self

    def set_data(self, data: object) -> None:
        self.setText(pformat(data))
        text_cursor = self.textCursor()
        block_format = QTextBlockFormat()

        block_format.setLineHeight(5, QTextBlockFormat.LineHeightTypes.LineDistanceHeight.value)

        text_cursor.clearSelection()
        text_cursor.select(QTextCursor.Document)
        text_cursor.mergeBlockFormat(block_format)
        self.setToolTip(str(data.__class__))

    def setData(self, data: object) -> None:
        self.set_data(data=data)

    def setup_highlighter(self):
        if self.highlighter is None:
            return
        for rule in ALL_RULES:
            self.highlighter.add_rule(rule())
        self.highlighter.setDocument(self.document())


class TextValueWidget(QTextEdit):
    determine_value_widget_func: Callable[[object], QWidget] = None
    value_types: tuple[type] = (str,)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.is_setup: bool = False

    def setup(self) -> Self:
        if self.is_setup is True:
            return self

        self.setFontFamily("Lucida Console")
        new_point_size = self.font().pointSize() * 1.25

        self.setFontPointSize(new_point_size)
        self.setReadOnly(True)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)

        self.is_setup = True
        return self

    def set_data(self, data: str) -> None:
        self.setText(data)
        text_cursor = self.textCursor()
        block_format = QTextBlockFormat()

        block_format.setLineHeight(5, QTextBlockFormat.LineHeightTypes.LineDistanceHeight.value)

        text_cursor.clearSelection()
        text_cursor.select(QTextCursor.Document)
        text_cursor.mergeBlockFormat(block_format)
        self.setToolTip(str(data.__class__))

    def setData(self, data: object) -> None:
        self.set_data(data=data)


# class NumberValueWidget(QLineEdit):
#     determine_value_widget_func: Callable[[object], QWidget] = None
#     value_types: tuple[type] = (int, float)

#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         self.is_setup: bool = False

#     def setup(self) -> Self:
#         if self.is_setup is True:
#             return self
#         self.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         font = self.font()
#         font.setFamily("Lucida Console")
#         font.setPointSize(int(font.pointSize() * 1.25))
#         self.setFont(font)
#         self.setReadOnly(True)

#         self.is_setup = True
#         return self

#     def set_data(self, data: Union[int, float]) -> None:
#         self.setText(str(data))
#         self.setToolTip(str(data.__class__))

#     def setData(self, data: object) -> None:
#         self.set_data(data=data)


class NumberValueWidget(QLCDNumber):
    determine_value_widget_func: Callable[[object], QWidget] = None
    value_types: tuple[type] = (int, float, Decimal)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._raw_data: Union[int, float] = None
        self.is_setup: bool = False

    def setup(self) -> Self:
        if self.is_setup is True:
            return self
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setFrameShape(QFrame.Shape.Box)
        self.setSegmentStyle(self.SegmentStyle.Flat)
        self.setFixedHeight(150)

        copy_action = QAction("copy", self)
        copy_action.triggered.connect(self.on_copy)
        self.addAction(copy_action)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.setSmallDecimalPoint(True)
        self.is_setup = True
        return self

    def set_data(self, data: Union[int, float]) -> None:
        self._raw_data = data
        digit_amount = len(str(self._raw_data).replace(".", ""))

        self.setDigitCount(digit_amount)
        if isinstance(data, Decimal):
            data = float(data)

        self.display(f"{data!s}")
        self.setToolTip(str(data.__class__))

    def setData(self, data: object) -> None:

        self.set_data(data=data)

    def on_copy(self, checked: bool):
        clipboard = QApplication.clipboard()
        value = str(self._raw_data)
        clipboard.setText(value)


# region [Main_Exec]
if __name__ == '__main__':
    pass

# endregion [Main_Exec]
