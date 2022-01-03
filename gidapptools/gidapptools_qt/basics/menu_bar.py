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

from PySide6.QtCore import QCoreApplication, QDate, QDateTime, QLocale, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QGradient, QIcon, QImage, QKeySequence,
                           QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import QApplication, QGridLayout, QMainWindow, QMenu, QMenuBar, QSizePolicy, QDialog, QStatusBar, QWidget, QMessageBox

from gidapptools.utility._debug_tools import obj_inspection

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseMenuBar(QMenuBar):

    def __init__(self, parent: Optional[QWidget] = None, auto_connect_standard_actions: bool = True) -> None:
        super().__init__(parent=parent)
        self.auto_connect_standard_actions = auto_connect_standard_actions
        self.about_dialog: QMessageBox = None
        self.setup_menus()

    def setup_default_menus(self) -> None:
        self.file_menu = self.add_new_menu("File")
        self.exit_action = self.add_new_action(self.file_menu, "Exit")
        if self.parent() is not None and self.auto_connect_standard_actions is True:
            self.exit_action.triggered.connect(self.parent().close)

        self.edit_menu = self.add_new_menu("Edit")

        self.view_menu = self.add_new_menu("View")

        self.settings_menu = self.add_new_menu("Settings")

        self.help_menu = self.add_new_menu("Help")
        self.help_menu.addSeparator()
        self.about_action = self.add_new_action(self.help_menu, "About")
        self.about_qt_action = self.add_new_action(self.help_menu, "About Qt®")
        if self.auto_connect_standard_actions is True:
            self.about_action.triggered.connect(self.app.show_about)
            self.about_qt_action.triggered.connect(self.app.show_about_qt)

    @property
    def app(self) -> QApplication:
        return QApplication.instance()

    def setup_menus(self) -> None:
        self.setup_default_menus()

    def add_new_menu(self, menu_title: str, icon: QIcon = None, add_before=None) -> QMenu:
        menu = QMenu(self)
        menu.setTitle(menu_title)
        if icon is not None:
            menu.setIcon(icon)
        if add_before is not None:
            if isinstance(add_before, QMenu):
                add_before = add_before.menuAction()
            self.insertMenu(add_before, menu)
        else:
            self.addMenu(menu)
        return menu

    def add_new_action(self, menu: QMenu, action_name: str, action_title: str = None):
        action_title = action_title or action_name
        action_name = action_name.casefold().replace(' ', '_')
        action = QAction(parent=menu)

        action.setText(action_title)
        menu.addAction(action)

        if not hasattr(menu, action_name + '_action'):
            setattr(menu, action_name + '_action', action)
        return action


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
