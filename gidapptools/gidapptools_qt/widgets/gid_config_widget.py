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

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QPalette, QTextOption, QBrush, QMouseEvent, QTextCharFormat, QSyntaxHighlighter, QPainter
from PySide6.QtCore import Qt, Slot, Signal, QTimerEvent, QSize, QAbstractTableModel, QItemSelection
from PySide6.QtWidgets import (QLabel, QDialogButtonBox, QWidget, QFormLayout, QStyle, QScrollBar, QLineEdit, QScrollArea, QApplication, QTableView, QFrame, QVBoxLayout, QStyleOption, QStyleOptionViewItem, QComboBox, QSizePolicy, QGroupBox,
                               QTextEdit, QStackedWidget, QFormLayout, QStyledItemDelegate, QGridLayout, QRadioButton, QCheckBox, QHBoxLayout, QPushButton, QSpacerItem, QTableView,
                               QTableWidget, QTableWidgetItem, QAbstractItemView)


from gidapptools.data.images import get_image
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    from gidapptools.gid_config.interface import GidIniConfig

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR: Path = Path(__file__).parent.absolute().resolve()

# endregion [Constants]


class CategoryPicture(QFrame):

    _DEFAULT_CATEGORY_IMAGE_FILE = get_image("default_config_category_image")
    clicked = Signal(int)

    def __init__(self, text: str, picture: QPixmap, category_page_number: int, parent=None) -> None:
        super().__init__(parent=parent)
        self.text: QLabel = None
        self.picture: QLabel = None
        self.category_page_number = category_page_number
        self.base_style = QFrame.Raised | QFrame.Panel
        self._default_category_image: QPixmap | None = None
        self.setup(text, picture)

    @property
    def default_category_image(self) -> QPixmap:
        if self._default_category_image is None:
            self._default_category_image = QPixmap(self._DEFAULT_CATEGORY_IMAGE_FILE.path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

        return self._default_category_image

    def setup(self, text: str, picture: QPixmap):
        self.setLayout(QVBoxLayout(self))
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 1)
        self.setFrameStyle(self.base_style)
        self.setMidLineWidth(3)
        self.setLineWidth(3)
        self.setToolTip(text)

        self.setup_text(text)
        self.setup_picture(picture)

    def setup_text(self, text: str):
        self.text = QLabel(text=text, parent=self)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        self.text.setTextFormat(Qt.TextFormat.AutoText)

        self.layout.addWidget(self.text)

    def setup_picture(self, picture: QPixmap):
        self.picture = QLabel(self)
        self.picture.setPixmap(picture)
        self.picture.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.picture)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.setFrameStyle(QFrame.Sunken | QFrame.Panel)
        self.clicked.emit(self.category_page_number)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.setFrameStyle(self.base_style)

    @property
    def layout(self) -> QVBoxLayout:
        return super().layout()

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}'


class PictureCategorySelector(QGroupBox):

    def __init__(self, content_widget: QStackedWidget, parent: QStackedWidget = None, ):
        super().__init__(parent=parent)
        self.content_widget = content_widget
        self.setLayout(QHBoxLayout(self))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFlat(True)
        self.setTitle("Categories")
        self.categories: dict[str, any] = {}

    @property
    def layout(self) -> QHBoxLayout:
        return super().layout()


class GidConfigContentStackedwidget(QStackedWidget):

    def __init__(self,
                 parent: Optional[PySide6.QtWidgets.QWidget] = None,
                 config: Optional["GidIniConfig"] = None
                 ) -> None:
        super().__init__(parent=parent)
        self._config: Optional["GidIniConfig"] = config
        self.sections: dict[str, QWidget] = {}
        self.setFrameShape(QFrame.WinPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(2)
        self.setMidLineWidth(2)
        self.setMinimumSize(750, 250)

    @property
    def config(self) -> Optional["GidIniConfig"]:
        return self._config

    def addSection(self, w: Any) -> int:
        self.sections[w.section_name] = w
        return super().addWidget(w)

    @Slot()
    def on_config_changed(self,
                          config: Optional["GidIniConfig"] = None) -> None:

        self.clear()
        self._config = config
        self.build_content()

    def clear(self) -> None:
        for section in self.sections.values():

            section.deleteLater()

        self.sections.clear()

    def build_content(self) -> None:
        ...

    def __repr__(self) -> str:

        return f'{self.__class__.__name__}(config={self.config!r})'


class GidConfigWidget(QWidget):

    config_changed = Signal(object)

    _DEFAULT_WINDOW_TITLE: str = "Settings"

    _DEFAULT_ICON_IMAGE = get_image("settings_default_icon")

    def __init__(self,
                 parent=None,
                 config: Optional["GidIniConfig"] = None,
                 section_image_map: Optional[dict[str, QPixmap]] = None):

        super().__init__(parent, Qt.WindowType.Dialog)

        self._config: Optional["GidIniConfig"] = config

        self._section_image_map = section_image_map or {}

        self.main_layout: QGridLayout = QGridLayout()

        self.content_widget: GidConfigContentStackedwidget = GidConfigContentStackedwidget(self)

    @property
    def config(self) -> Optional["GidIniConfig"]:
        return self._config

    def finalize_config(self) -> None:
        ...

    def set_config(self, config: Optional["GidIniConfig"]) -> None:
        if self._config is not None:
            self.finalize_config()

        self._config = config

        self.config_changed.emit()

    def setup(self) -> Self:

        self.setWindowTitle(self._DEFAULT_WINDOW_TITLE)
        self.setWindowIcon(self._DEFAULT_ICON_IMAGE.as_qicon())

        self.setLayout(self.main_layout)
        self.setup_buttons()
        self.setup_content_widget()
        self.setup_selection_box()
        return self

    def setup_selection_box(self) -> None:
        self.selection_box = PictureCategorySelector(self.content_widget)

        self.main_layout.addWidget(self.selection_box, 0, 0, 1, 1, Qt.AlignmentFlag.AlignTop)

    def setup_content_widget(self) -> None:
        self.content_widget: GidConfigContentStackedwidget = GidConfigContentStackedwidget(self, config=self.config)
        self.config_changed.connect(self.content_widget.on_config_changed)
        self.main_layout.addWidget(self.content_widget, 1, 0, 1, 1)

    def setup_buttons(self) -> None:
        self.buttons = QDialogButtonBox(self)
        self.buttons.setOrientation(Qt.Orientation.Horizontal)
        self.buttons.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.main_layout.addWidget(self.buttons, 2, 0, 1, 1, Qt.AlignmentFlag.AlignBottom)
        self.buttons.rejected.connect(self.on_cancelled)
        self.buttons.accepted.connect(self.on_accepted)

    def on_accepted(self):
        self.close()

    def on_cancelled(self):
        self.close()

    def close(self):
        self.config_changed.disconnect(self.content_widget.on_config_changed)
        return super().close()

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}(config={self.config!r})'


# region [Main_Exec]
if __name__ == '__main__':
    x = QApplication()
    y = GidConfigWidget().setup()
    y.show()

    x.exec()

# endregion [Main_Exec]
