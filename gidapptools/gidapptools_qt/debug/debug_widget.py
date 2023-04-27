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
from math import sqrt
import subprocess
import inspect
from decimal import Decimal

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from types import ModuleType
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

from PySide6.QtGui import (QAction, QTextBlockFormat, QTextCursor, QBrush, QTextOption, QSyntaxHighlighter, QCloseEvent, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QStyleOptionGroupBox, QScrollArea, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QLayoutItem, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup)

import shiboken6
from gidapptools.gidapptools_qt.widgets.separator_lines import HorizontalSeparatorLine, VerticalSeparatorLine
from gidapptools.general_helper.string_helper import shorten_string, StringCaseConverter, StringCase
from gidapptools.gidapptools_qt._data.images import get_image
from gidapptools.gidapptools_qt.layouts.sorted_layout import SortedVBoxLayout

import pp
import distinctipy
from pygments import lexers
from pygments.lexer import Lexer
from pygments import formatters
from pygments import filters
from pygments.filter import Filter
from pygments.formatter import Formatter
from pygments import highlight, token

from gidapptools.gidapptools_qt.debug.debug_value_widgets import determine_value_widget
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class DebugContentWidget(QWidget):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

    @property
    def layout(self) -> QVBoxLayout:
        return super().layout()


class DebugDialog(QScrollArea):

    def __init__(self,
                 title: str,
                 key_text: str,
                 category: "DebugCategoryBox") -> None:
        super().__init__(parent=None)

        self.setWindowTitle(title)
        self.key_text = key_text
        self.value_data: object = None
        self.category = category
        self.content_widget = DebugContentWidget()

        self.key_text_widget: QTextEdit = self._make_key_text_widget()

        self.separator_line = HorizontalSeparatorLine(self)

        self._value_widget = None
        self.is_setup: bool = False
        # self._setup()

    @property
    def value_widget(self) -> QWidget:
        if self._value_widget is None:
            self._value_widget = self._make_value_widget()
        return self._value_widget

    def _make_key_text_widget(self) -> QTextEdit:

        key_text_widget = QLabel()
        key_text_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = key_text_widget.font()
        font.setBold(True)
        font.setPointSize(int(font.pointSize() * 1.5))
        key_text_widget.setFont(font)
        return key_text_widget

    def _make_value_widget(self) -> QWidget:
        value_widget = determine_value_widget(self.value_data)(self)
        try:
            value_widget = value_widget.setup()
        except AttributeError:
            pass
        return value_widget

    def _setup_scrollbar(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)

    def _setup_widgets(self) -> None:
        self.content_widget.layout.insertWidget(0, self.key_text_widget, 0)
        self.content_widget.layout.insertWidget(1, self.separator_line, 0)

        self.key_text_widget.setText(self.key_text)
        self.key_text_widget.adjustSize()

    def setup(self) -> Self:
        if self.is_setup is True:
            return
        self.setWidget(self.content_widget)

        self._setup_widgets()
        self._setup_scrollbar()
        self.resize(1000, 600)

        self.is_setup = True
        return self

    def set_data(self, data: object):
        self.value_data = data
        self.content_widget.layout.insertWidget(2, self.value_widget, 1)

        self.content_widget.layout.addStretch()
        self.value_widget.set_data(self.value_data)
        # self.repaint()

    def show(self):

        super().show()

    def closeEvent(self, event: QCloseEvent) -> None:
        if event.isAccepted():
            self.category.result_window_closed.emit(self)

        return super().closeEvent(event)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(title={self.windowTitle()!r})"


class ShowAttrButton(QPushButton):

    def __init__(self, attr_name: str, obj: Union[object, type, ModuleType], parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ShowAttrButton")
        self.attr_name = attr_name
        self.obj = obj
        if inspect.isclass(self.obj) or inspect.ismodule(self.obj):
            self.obj_name = obj.__name__
        else:
            self.obj_name = obj.__class__.__name__

        self.category_name = self.obj_name

        self.setText(f"Show {self.obj_name}.{self.attr_name}")

        self.clicked.connect(self.show_info_box)
        self.setStyleSheet("""

        ShowAttrButton {
            background-color: rgba(173, 216, 230, 34%);
        }

        """)

    def show_info_box(self):
        title = self.attr_name

        attr_value = getattr(self.obj, self.attr_name)
        if callable(attr_value):
            attr_value = attr_value()

        # key_text = f"Attribute <i><b>{self.attr_name!r}</b></i> of object <i><b>{self.obj!r}</b></i> is:"
        key_text = f"Attribute {self.attr_name!r} of object {self.obj!r} is:"

        dialog = DebugDialog(title=title, key_text=key_text, category=self.parent()).setup()
        dialog.set_data(attr_value)
        self.parent().result_window_created.emit(dialog)
        dialog.show()


class ShowFunctionResultButton(QPushButton):
    def __init__(self, category_name: str, function: Callable, parent=None, **kwargs):
        super().__init__(parent=parent)
        self.setObjectName("ShowFunctionResultButton")

        self.category_name = category_name
        self.function = function
        self.kwargs = kwargs
        self._text = self.function.__name__
        if kwargs:
            self._text += " with " + ', '.join(f"{k}=>{shorten_string(repr(v),50,split_on=r'any')}" for k, v in self.kwargs.items())

        self.setText(f"show result for {self._text}")
        self.clicked.connect(self.show_info_box)
        if getattr(self.function, "is_disabled", False) is True:
            self.setEnabled(False)
        self.setStyleSheet("""

        ShowFunctionResultButton {
            background-color: rgba(153, 229, 153, 34%);
        }

        """)

    @property
    def app(self) -> Optional[QApplication]:
        return QApplication.instance()

    def show_info_box(self):
        title = f"Result for {self.function.__name__}"
        value = self.function(**self.kwargs)
        if inspect.isgenerator(value):
            value = tuple(value)
        # key_text = f"Result for <i><b>{self._text}</b></i> is:"
        key_text = f"Result for {self._text} is:"

        dialog = DebugDialog(title=title, key_text=key_text, category=self.parent()).setup()
        dialog.set_data(value)
        self.parent().result_window_created.emit(dialog)

        dialog.show()


class DebugCategoryBox(QGroupBox):
    result_window_created = Signal(QWidget)
    result_window_closed = Signal(QWidget)

    def __init__(self, name: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DebugCategoryBox")

        self.name = name
        self.setTitle(" " + self.name + ' ')
        self.setLayout(QVBoxLayout())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widgets: dict[str, QWidget] = {}
        self._mod_font()
        self.setCheckable(True)

        self.toggled.connect(self.on_toggled)

    def _mod_font(self) -> None:
        font = self.font()
        font.setBold(True)
        font.setPointSize(int(font.pointSize() * 1.25))
        self.setFont(font)

    def on_toggled(self, value: bool):
        for child_idx in range(self.layout.count()):
            child = self.layout.itemAt(child_idx)
            child.widget().setVisible(value)

    @ property
    def layout(self) -> QVBoxLayout:
        return super().layout()

    def add_widget(self, name: str, widget: QWidget):
        if name in self.widgets:
            raise ValueError(f"Name {name!r} already registered in category {self!r}.")
        self.layout.addWidget(widget)
        widget.setParent(self)
        self.widgets[name] = widget


def layout_sort_func(in_item: QLayoutItem):
    try:
        name = in_item.widget().name.casefold()
    except AttributeError:
        name = in_item.widget().objectName().casefold()

    general_pos = 0
    if name.endswith("-attribute"):
        general_pos = 1

    return general_pos, name.removeprefix("show ")


class DebugWidget(QDockWidget):

    def __init__(self, inject_app: bool = False, func_injects: dict[str, object] = None, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.inject_app = inject_app
        self.func_injects = func_injects or {}
        self.scroll_area = QScrollArea()

        self.content_widget = QWidget(self)
        self.content_widget.setLayout(SortedVBoxLayout(layout_sort_func))
        # self.content_widget.setLayout(QVBoxLayout())
        # self.content_widget.layout().setContentsMargins(25, 25, 25, 25)
        self.setWindowTitle("Debug")
        self.setWindowIcon(QPixmap(get_image("debugging_icon.png").path))

        self.categories: dict[str, DebugCategoryBox] = {}
        self._current_result_window: QWidget = None

    @property
    def app(self) -> Optional[QApplication]:
        return QApplication.instance()

    def set_current_result_window(self, window: QWidget) -> None:
        if self._current_result_window is not None:
            self._current_result_window.close()

        self._current_result_window = window

    def unset_current_result_window(self, window: QWidget) -> None:
        if self._current_result_window is None:
            return

        elif self._current_result_window is not window:
            return

        else:

            self._current_result_window = None

    def setup(self) -> Self:
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.content_widget)

        self.scroll_area.verticalScrollBar().setSingleStep(2)

        self.setWidget(self.scroll_area)

        self.setMinimumSize(QSize(300, 300))

        self.resize(600, 600)
        return self

    def get_category_box(self, name: str) -> DebugCategoryBox:
        try:
            return self.categories[name.strip().casefold()]
        except KeyError:
            category = DebugCategoryBox(name=name)
            category.result_window_created.connect(self.set_current_result_window)
            category.result_window_closed.connect(self.unset_current_result_window)
            self.content_widget.layout().addWidget(category)
            self.categories[name.strip().casefold()] = category
            return category

    def _modify_func_globals(self, func: Callable) -> None:
        if not hasattr(func, "__globals__"):
            return
        for k, v in self.func_injects.items():
            if k not in func.__globals__:
                func.__globals__[k] = v

        if self.inject_app is True and "app" not in func.__globals__:
            func.__globals__["app"] = self.app

    def add_widget(self, name: str, category: str, widget: QWidget):
        category_box = self.get_category_box(category)
        category_box.add_widget(name=name, widget=widget)

    def add_show_attr_button(self, attr_name: str, obj: object):
        button = ShowAttrButton(attr_name=attr_name, obj=obj, parent=self)
        self.add_widget(button.text(), button.category_name, button)

    def add_show_func_result_button(self, function: Callable, category_name: str, **kwargs):
        self._modify_func_globals(func=function)
        button = ShowFunctionResultButton(category_name=category_name, function=function, **kwargs)
        self.add_widget(button.text(), button.category_name, button)

    def closeEvent(self, event: QCloseEvent) -> None:
        if event.isAccepted():
            if self._current_result_window is not None:

                self._current_result_window.close()
        super().closeEvent(event)

    def show(self) -> None:
        return super().show()
# region [Main_Exec]


def stupid_function():
    return "aaaaa", 13, 14.5, ["a", "list", "not", "a", "tuple"], {"dog": "cat", "woof": 1337}


def stupid_function_2():
    return "woof"


def stupid_function_3():
    return 3


def stupid_function_4():
    return sqrt(2)


def stupid_function_5():
    return Decimal(2).sqrt()


def get_all_lexers():
    _out = []
    for name, *_ in lexers.get_all_lexers():
        _out.append(name)

    return tuple(_out)


def inspect_filter(name: str):
    _filter: Filter = filters.get_filter_by_name(name)
    return {"name": _filter.__class__.__qualname__,
            "module": _filter.__module__,
            "options": _filter.options,
            "doc": _filter.__doc__,
            "dict": _filter.__dict__}


def inspect_all_filter():
    for filter_name in filters.get_all_filters():
        yield inspect_filter(filter_name)


if __name__ == '__main__':
    app = QApplication()
    x = DebugWidget().setup()
    x.add_show_func_result_button(function=stupid_function, category_name="stupid")
    x.add_show_func_result_button(function=stupid_function_2, category_name="stupid")
    x.add_show_func_result_button(function=stupid_function_3, category_name="stupid")

    x.add_show_func_result_button(function=QApplication.screens, category_name="Qt")
    x.add_show_func_result_button(function=stupid_function_4, category_name="stupid")

    x.add_show_attr_button("__dict__", app)
    x.add_show_attr_button("__dict__", QDockWidget)
    x.add_show_attr_button("argv", sys)
    x.add_show_attr_button("path", sys)
    x.add_show_attr_button("base_prefix", sys)
    x.add_show_attr_button("base_exec_prefix", sys)
    x.add_show_attr_button("builtin_module_names", sys)
    x.add_show_attr_button("exec_prefix", sys)
    x.add_show_attr_button("exc_info", sys)
    x.add_show_attr_button("flags", sys)
    x.add_show_func_result_button(get_all_lexers, "pygments")
    x.add_show_func_result_button(formatters.get_all_formatters, "pygments")
    x.add_show_func_result_button(filters.get_all_filters, "pygments")
    x.add_show_func_result_button(inspect_all_filter, "pygments")
    x.add_show_func_result_button(function=stupid_function_5, category_name="stupid")

    x.add_show_attr_button("cwd", Path())

    x.show()
    app.exec()
# endregion [Main_Exec]
