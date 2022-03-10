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
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
from importlib.machinery import SourceFileLoader


import PySide6
from PySide6 import (QtCore, QtGui, QtWidgets, Qt3DAnimation, Qt3DCore, Qt3DExtras, Qt3DInput, Qt3DLogic, Qt3DRender, QtAxContainer, QtBluetooth,
                     QtCharts, QtConcurrent, QtDataVisualization, QtDesigner, QtHelp, QtMultimedia, QtMultimediaWidgets, QtNetwork, QtNetworkAuth,
                     QtOpenGL, QtOpenGLWidgets, QtPositioning, QtPrintSupport, QtQml, QtQuick, QtQuickControls2, QtQuickWidgets, QtRemoteObjects,
                     QtScxml, QtSensors, QtSerialPort, QtSql, QtStateMachine, QtSvg, QtSvgWidgets, QtTest, QtUiTools, QtWebChannel, QtWebEngineCore,
                     QtWebEngineQuick, QtWebEngineWidgets, QtWebSockets, QtXml)

from PySide6.QtCore import (QByteArray, QTimerEvent, QCoreApplication, QDate, QDateTime, QEvent, QLocale, QMetaObject, QModelIndex, QModelRoleData, QMutex,
                            QMutexLocker, QObject, QPoint, QRect, QRecursiveMutex, QRunnable, QSettings, QSize, QThread, QThreadPool, QTime, QUrl,
                            QWaitCondition, Qt, QAbstractItemModel, QAbstractListModel, QAbstractTableModel, Signal, Slot)

from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QFontMetrics, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QMovie, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)

from PySide6.QtWidgets import (QApplication, QBoxLayout, QCheckBox, QColorDialog, QColumnView, QComboBox, QDateTimeEdit, QDialogButtonBox,
                               QDockWidget, QDoubleSpinBox, QFontComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                               QLCDNumber, QLabel, QLayout, QLineEdit, QListView, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                               QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStackedLayout, QStackedWidget,
                               QStatusBar, QStyledItemDelegate, QSystemTrayIcon, QTabWidget, QTableView, QTextEdit, QTimeEdit, QToolBox, QTreeView,
                               QVBoxLayout, QWidget, QAbstractItemDelegate, QAbstractItemView, QAbstractScrollArea, QRadioButton, QFileDialog, QButtonGroup)

from gidapptools.data.gifs import get_gif

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BusySpinnerWidget(QLabel):
    default_gif_name: str = "busy_spinner_4.gif"
    default_spinner_size: tuple[int, int] = (75, 75)

    def __init__(self, parent: QWidget = None, spinner_gif: Union[QMovie, str] = None, spinner_size: QSize = None):
        super().__init__(parent)
        self.spinner_size = spinner_size or QSize(*self.default_spinner_size)
        self.spinner_gif = self.setup_spinner_gif(spinner_gif=spinner_gif)
        self.setAlignment(Qt.AlignCenter)

        self.running: bool = False

    def set_spinner_size(self, size: QSize) -> None:
        self.spinner_size = size
        self.spinner_gif.setScaledSize(self.spinner_size)

    def setup_spinner_gif(self, spinner_gif: Union[QMovie, str]) -> QMovie:
        if isinstance(spinner_gif, str):
            spinner_gif = get_gif(spinner_gif)

        spinner_gif = spinner_gif or get_gif(self.default_gif_name)
        spinner_gif.setScaledSize(self.spinner_size)
        spinner_gif.setCacheMode(QMovie.CacheAll)
        self.setMovie(spinner_gif)
        return spinner_gif

    def start(self):
        self.spinner_gif.start()
        self.running = True

    def stop(self):
        self.spinner_gif.stop()
        self.running = False


class BusyPushButton(QPushButton):
    _stop_signal = Signal(Future)

    def __init__(self,
                 parent: QWidget = None,
                 text: str = None,
                 spinner_gif: Union[QMovie, str] = None,
                 spinner_size: QSize = None,
                 disable_while_spinning: bool = True):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setLayout(QVBoxLayout())
        self.disable_while_spinning = disable_while_spinning
        self.text_widget = QLabel(self)
        self.text_widget.setScaledContents(True)
        self.text_widget.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.text_widget)
        self.busy_spinner_widget = BusySpinnerWidget(self, spinner_gif=spinner_gif, spinner_size=spinner_size or QSize(self.size().height(), self.size().height()))
        self.layout.addWidget(self.busy_spinner_widget)
        self.set_text(text)
        self.busy_spinner_widget.setVisible(False)
        self._stop_signal.connect(self.stop_spinner)

    @property
    def layout(self) -> QVBoxLayout:
        return super().layout()

    def resize(self, size: QSize):
        super().resize(size)
        self.set_spinner_size(QSize(self.size().height(), self.size().height()))

    def set_spinner_size(self, size: QSize):
        self.busy_spinner_widget.set_spinner_size(size)

    def set_text(self, text: str):
        text = text or ""
        self.text_widget.setText(text)

    def sizeHint(self) -> PySide6.QtCore.QSize:
        return self.layout.sizeHint()

    def hide_text(self):

        self.text_widget.setVisible(False)

    def show_text(self):

        self.text_widget.setVisible(True)

    def start_spinner(self):
        self.hide_text()
        self.busy_spinner_widget.setVisible(True)

        self.busy_spinner_widget.start()
        if self.disable_while_spinning is True:
            self.setEnabled(False)

    def stop_spinner(self, *args):
        if self.disable_while_spinning is True:
            self.setEnabled(True)
        self.busy_spinner_widget.stop()
        self.busy_spinner_widget.setVisible(False)
        self.show_text()

    def start_spinner_while_future(self, future: Future):
        self.start_spinner()

        future.add_done_callback(self._stop_signal.emit)

    def start_spinner_with_stop_signal(self, stop_signal: Signal):
        self.start_spinner()
        stop_signal.connect(self.stop_spinner)


# region[Main_Exec]
if __name__ == '__main__':
    app = QApplication()
    x = BusySpinnerWidget()
    x.show()
    app.exec()

# endregion[Main_Exec]
