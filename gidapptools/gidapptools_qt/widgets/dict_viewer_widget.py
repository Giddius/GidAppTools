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
from math import floor, ceil

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
from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtGui import QFont, QColor, QPalette, QTextOption, QBrush, QMouseEvent, QTextCharFormat, QSyntaxHighlighter, QPainter
from PySide6.QtCore import Qt, Slot, Signal, QTimerEvent, QSize, QAbstractTableModel, QItemSelection
from PySide6.QtWidgets import (QLabel, QWidget, QFormLayout, QStyle, QScrollBar, QLineEdit, QScrollArea, QApplication, QTableView, QFrame, QVBoxLayout, QStyleOption, QStyleOptionViewItem, QComboBox, QSizePolicy, QGroupBox,
                               QTextEdit, QFormLayout, QStyledItemDelegate, QGridLayout, QRadioButton, QCheckBox, QHBoxLayout, QPushButton, QSpacerItem, QTableView,
                               QTableWidget, QTableWidgetItem, QAbstractItemView)

from pygments import highlight
from pygments.lexers import PythonLexer, JsonLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name, get_all_styles

from pygments.style import Style as PygmentsStyle
from pygments.lexer import Lexer as PygmentsLexer
from pygments.formatter import Formatter as PygmentsFormatter
from pygments import token as pygments_token
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

THIS_FILE_DIR: Path = Path(__file__).parent.absolute().resolve()

# endregion [Constants]


def _get_style_foreground_color(style: PygmentsStyle) -> str:

    foreground_color = None

    for possible_attr_name in ("foreground", "FOREGROUND"):
        foreground_color = getattr(style, possible_attr_name, None)
        if foreground_color is not None:
            break

    if foreground_color is None:
        foreground_color = style.style_for_token(pygments_token.Token)["color"]

    if foreground_color is None:
        foreground_color = "#ffffff"

    foreground_color = "#" + foreground_color.strip().removeprefix("#")
    return foreground_color


class TextDictViewerWidget(QWidget):

    def __init__(self,
                 data: dict[object, object] | None = None,
                 highlight_style: str | None = None,
                 parent: QWidget | None = None):

        super().__init__(parent)
        self._highlight_style: str | None = highlight_style
        self._data = data.copy()
        self.setLayout(QVBoxLayout())
        self._options_box = QGroupBox()
        options_box_layout = QFormLayout()
        self._style_selector = QComboBox()

        options_box_layout.addRow("Highlight Style", self._style_selector)

        self._options_box.setLayout(options_box_layout)

        self._text_box = QTextEdit()

        self.layout.addWidget(self._options_box, 0)
        self.layout.addWidget(self._text_box, 2)

    @property
    def layout(self) -> QVBoxLayout:
        return super().layout()

    def _setup_font(self):
        _font = self._text_box.font()
        _font.setStyleHint(QFont.Monospace)
        _font.setFamily("Consolas")
        _font.setPointSize(ceil(_font.pointSize() * 1.25))

        self._text_box.setFont(_font)

    def _get_sub_pat_text(self, sub_path: str):
        _path_keys = sub_path.split(".")

        _data = self._data.copy()

        for _key in _path_keys:
            _data = _data[_key]

        return json.dumps(_data, default=str, indent=4)

    def _setup_content(self, only_sub_path: str = None):
        self._text_box.clear()
        self._text_box.setAcceptRichText(True)
        self._text_box.setReadOnly(True)
        self._text_box.setStyleSheet("")

        if only_sub_path is not None:
            text = self._get_sub_pat_text(only_sub_path)
        else:
            text = json.dumps(self._data, default=str, indent=4)

        if self._highlight_style is not None:
            pygment_style = get_style_by_name(self._highlight_style)
            pygment_lexer = JsonLexer()
            pygment_formatter_kwargs = {"noclasses": True,
                                        "style": pygment_style,
                                        "lineseparator": "<br>"}
            _background_color = pygment_style.background_color if pygment_style.background_color else '#808080'
            if _background_color.casefold() == "#ffffff":
                _background_color = "#D3D3D3"
            pygment_style.background_color = _background_color
            pygment_formatter = HtmlFormatter(**pygment_formatter_kwargs)

            self._text_box.setStyleSheet("QTextEdit {background-color: " + _background_color + "; color: " + _get_style_foreground_color(pygment_style) + ";}")

            text = highlight(text, pygment_lexer, pygment_formatter)

        self._text_box.setText(text)

    def _setup_style_selector(self):
        self._style_selector.clear()
        self._style_selector.setDuplicatesEnabled(False)
        self._style_selector.setEditable(False)
        self._style_selector.addItem("NO HIGHLIGHT"),

        self._style_selector.addItems(list(get_all_styles()))
        try:
            self._style_selector.setCurrentText(self._highlight_style or "NO HIGHLIGHT")
        except Exception:
            pass
        self._style_selector.currentTextChanged.connect(self.on_highlight_style_changed)
        self._style_selector.setMaxVisibleItems(10)
        self._style_selector.setStyleSheet("combobox-popup: 0;")

    def setup(self) -> Self:

        self._setup_font()
        self._setup_content()
        self._setup_style_selector()

        return self

    @Slot()
    def on_highlight_style_changed(self, new_style: str) -> None:
        if new_style == "NO HIGHLIGHT":
            new_style = None

        self._highlight_style = new_style

        self._setup_content()

# region [Main_Exec]


if __name__ == '__main__':
    pass

# endregion [Main_Exec]
