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

from PySide6.QtCore import (QByteArray, QCoreApplication, QDate, QDateTime, QEvent, QLocale, QMetaObject, QModelIndex, QModelRoleData, QMutex,
                            QMutexLocker, QObject, QPoint, QRect, QRecursiveMutex, QRunnable, QSettings, QSize, QThread, QThreadPool, QTime, QUrl,
                            QWaitCondition, Qt, QAbstractItemModel, QAbstractListModel, QAbstractTableModel, Signal, Slot)

from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QStyleOptionMenuItem, QWidgetAction, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup)

from gidapptools.errors import ApplicationNotExistingError

if TYPE_CHECKING:
    from gidapptools.gidapptools_qt.basics.application import GidQtApplication
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MenuTitle(QFrame):

    def __init__(self, text: str = None, icon: Union[QIcon, QPixmap] = None, parent=None):
        super().__init__(parent=parent)
        self.setup_styling()

        self.setLayout(QHBoxLayout())
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.text_label = QLabel()

        if text:
            self.set_text(text)
        self.text_label.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel()

        if icon:
            self.set_icon(icon)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)
        self.widget_action = QWidgetAction(self)
        self.widget_action.setDefaultWidget(self)

    def setup_styling(self):
        self.setVisible(False)

        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setMidLineWidth(1)
        self.setLineWidth(1)
        font = self.font()

        font.setPointSize(int(font.pointSize() * 0.9))
        font.setBold(True)

        font.setLetterSpacing(font.AbsoluteSpacing, 2)
        self.setFont(font)

    @property
    def layout(self) -> QHBoxLayout:
        return super().layout()

    @property
    def icon_size(self) -> QSize:
        if self.text_label.text():
            fm = self.fontMetrics()
            fm.horizontalAdvance(self.text_label.text())
            size = int(fm.height() * 0.9)
            return QSize(size, size)
        return QSize(20, 20)

    def set_text(self, text: str):
        self.text_label.setText(text)
        self.setVisible(True)

    def set_icon(self, icon: Union[QIcon, QPixmap]):
        if isinstance(icon, QIcon):
            icon = icon.pixmap(self.icon_size)

        else:
            icon = icon.scaled(self.icon_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.icon_label.setPixmap(icon)
        self.setVisible(True)


class GidBaseSysTray(QSystemTrayIcon):

    def __init__(self, icon: Union[QIcon, QPixmap], title: str = None, tooltip: str = None, parent: Optional[QObject] = None):
        super().__init__(icon, parent=parent)
        self.setToolTip(tooltip)
        self.menu: QMenu = QMenu()
        self.setContextMenu(self.menu)
        self.menu_title = MenuTitle(title)
        self.actions: dict[str, QAction] = {}

    def setup(self) -> "GidBaseSysTray":
        if self.app is None:
            raise ApplicationNotExistingError(f"Setting up {self} before the application has been instantiated is forbidden.")
        self.menu.addAction(self.menu_title.widget_action)
        self.menu.addSeparator()

        self.setup_custom_actions()
        self.setup_standard_actions()
        self.menu.repaint()
        return self

    def setup_custom_actions(self):
        pass

    def setup_standard_actions(self):
        self.add_action("Close", self.app.quit)
        self.add_action("Hide")

    def set_title(self, title: str):
        self.menu_title.set_text(title)

    def add_action(self, text: str, connect_to: Callable = None, icon: QIcon = None, enabled: bool = True):
        action = QAction(text, self.menu)
        action.setIconText(text)
        if icon:
            action.setIcon(icon)
        action.setEnabled(enabled)
        self.actions[text.casefold()] = action
        self.menu.addAction(action)
        if connect_to:
            action.triggered.connect(connect_to)

    @property
    def app(self) -> "GidQtApplication":
        return QApplication.instance()

    @property
    def title(self) -> Optional[str]:
        return self.menu_title.text()

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
