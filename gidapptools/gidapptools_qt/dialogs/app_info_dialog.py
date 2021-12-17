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
from PySide6.QtWidgets import QApplication, QGridLayout, QMainWindow, QMenu, QMenuBar, QSizePolicy, QStatusBar, QWidget, QDialog, QLabel, QLineEdit, QBoxLayout, QVBoxLayout

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AppInfoDialog(QDialog):

    def __init__(self) -> None:
        super().__init__()

        self.label_font = self.create_label_font()
        self.parts = []
        self.setup()

    def create_label_font(self) -> QFont:
        font = QFont()
        font.setPointSize(19)
        font.setBold(True)
        return font

    def create_new_part(self, label_text: str, data_text: str) -> None:
        label = QLabel(self)
        label.setText(label_text)
        label.setFont(self.label_font)
        label.setAlignment(Qt.AlignCenter)

        data = QLineEdit(self)
        data.setReadOnly(True)
        data.setText(data_text)
        data.setAlignment(Qt.AlignCenter)

        self.parts.append((label, data))

    def setup(self):
        self.resize(400, 100)
        self.setMaximumSize(QSize(400, 100))
        self.verticalLayout = QVBoxLayout(self)

        for label, data in self.parts:
            self.verticalLayout.addWidget(label)
            self.verticalLayout.addWidget(data)


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
