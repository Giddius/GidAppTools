"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import logging.handlers
import re
import traceback
import logging
from time import perf_counter
import sys
from threading import Lock, RLock
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Union, Literal, Callable
from pathlib import Path
from datetime import datetime, timezone
from collections import deque
from logging.handlers import BaseRotatingHandler
from frozendict import frozendict
# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.conversion import human2bytes
from gidapptools.general_helper.regex.datetime_regex import datetime_format_to_regex

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.custom_types import PATH_TYPE
    from gidapptools.gid_logger.records import LOG_RECORD_TYPES

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


DEFAULT_MAX_BYTES = human2bytes("5 mb")


class BaseFileNameTemplate(ABC):

    def __init__(self, base_name: str, suffix: str = ".log") -> None:
        self.base_name = base_name
        self.suffix = suffix

    @abstractmethod
    def format(self) -> str:
        ...

    @abstractmethod
    def make_backup_file_path(self, in_name: str, backup_folder: Path) -> Path:
        ...

    @abstractmethod
    def is_same_kind_log_file(self, other_file: Path) -> bool:
        ...

    @abstractmethod
    def is_backup_log_file(self, other_file: Path) -> bool:
        ...


class TimestampFileNameTemplate(BaseFileNameTemplate):
    format_template: str = "{base_name}_{timestamp}{suffix}"

    def __init__(self, base_name: str, suffix: str = ".log", time_zone: timezone = None, timestamp_format: str = None) -> None:
        super().__init__(base_name=base_name, suffix=suffix)
        self.time_zone = time_zone
        self.timestamp_format = timestamp_format or self._get_default_timestamp_format()
        self.timestamp_regex = datetime_format_to_regex(self.timestamp_format, re.IGNORECASE)

    def _get_default_timestamp_format(self) -> str:
        return "%Y-%m-%d_%H-%M-%S_%Z" if self.time_zone is not None else "%Y-%m-%d_%H-%M-%S"

    def get_timestamp(self) -> str:
        now = datetime.now(tz=self.time_zone)
        return now.strftime(self.timestamp_format)

    def format(self) -> str:
        return self.format_template.format(base_name=self.base_name, timestamp=self.get_timestamp(), suffix=self.suffix)

    def make_backup_file_path(self, in_name: str, backup_folder: Path) -> Path:
        return backup_folder.joinpath(in_name)

    def is_same_kind_log_file(self, other_file: Path) -> bool:
        if other_file.suffix != self.suffix:
            return False

        date_time_match = self.timestamp_regex.search(other_file.stem)
        if not date_time_match:
            return False
        base_name = other_file.stem[:date_time_match.start()].rstrip("_")

        if base_name == self.base_name:
            return True

        return False

    def is_backup_log_file(self, other_file: Path) -> bool:
        return self.is_same_kind_log_file(other_file=other_file)


class GidBaseRotatingFileHandler(BaseRotatingHandler):

    def __init__(self,
                 base_name: str,
                 log_folder: "PATH_TYPE",
                 file_name_template: Union[str, Any] = None,
                 backup_amount_limit: int = 10) -> None:
        self.base_name = base_name
        self.file_name_template = TimestampFileNameTemplate(self.base_name) if file_name_template is None else file_name_template
        self.log_folder = Path(log_folder)
        self.backup_amount_limit = backup_amount_limit
        self.full_file_path: Path = self._construct_full_file_path()
        self.first_record_emited: bool = False
        super().__init__(self.full_file_path, "a", encoding="utf-8", delay=True, errors="ignore")

    def emit(self, record) -> None:
        with self.lock:
            if self.first_record_emited is False:
                self.on_start_rotation()
                self.first_record_emited = True

        return super().emit(record)

    def _construct_full_file_path(self) -> Path:
        name = self.file_name_template.format()
        full_path = self.log_folder.joinpath(name)

        return full_path

    def _get_old_logs(self) -> tuple[Path]:
        def _is_old_log(_in_file: Path) -> bool:
            return _in_file.is_file() and self.file_name_template.is_same_kind_log_file(_in_file)

        _out = tuple(file for file in tuple(self.log_folder.iterdir()) if _is_old_log(file) is True)

        return _out

    def _get_backup_logs(self) -> list[Path]:

        def _is_old_backup(_in_file: Path) -> bool:
            return _in_file.is_file() and self.file_name_template.is_backup_log_file(_in_file)

        _out = sorted((file for file in self.log_folder.iterdir() if _is_old_backup(file)), key=lambda x: x.stat().st_mtime)
        return _out

    def on_start_rotation(self) -> None:
        try:
            self.acquire()
            self.log_folder.mkdir(exist_ok=True, parents=True)
            self.remove_excess_backup_files()

        finally:
            self.release()

    def remove_excess_backup_files(self) -> None:
        if self.backup_amount_limit is None:
            return
        backup_logs = self._get_backup_logs()
        while len(backup_logs) > self.backup_amount_limit:
            to_delete: Path = backup_logs.pop(0)
            to_delete.unlink(missing_ok=True)

    def shouldRollover(self, record: logging.LogRecord) -> bool:
        return False


class GidBaseStreamHandler(logging.StreamHandler):

    def __init__(self, stream=None):
        super().__init__(stream=stream)


LOG_DEQUE_TYPE = deque["LOG_RECORD_TYPES"]


class GidStoringHandler(logging.Handler):
    # TODO: Redo with less deques and a way to not delete error messages except when explicitly requested

    def __init__(self,
                 max_storage_size: int = 500,
                 level: int = 0) -> None:
        super().__init__(level=level)
        self._max_storage_size: int = max_storage_size
        self._callbacks: frozendict[str, set[Callable[[Union["LOG_RECORD_TYPES", None]], None]]] = frozendict({"ALL": set(),
                                                                                                               "DEBUG": set(),
                                                                                                               "INFO": set(),
                                                                                                               "WARNING": set(),
                                                                                                               "CRITICAL": set(),
                                                                                                               "ERROR": set()})
        self.debug_messages: "LOG_DEQUE_TYPE" = deque(maxlen=self._max_storage_size)
        self.info_messages: "LOG_DEQUE_TYPE" = deque(maxlen=self._max_storage_size)
        self.warning_messages: "LOG_DEQUE_TYPE" = deque(maxlen=self._max_storage_size)
        self.critical_messages: "LOG_DEQUE_TYPE" = deque(maxlen=self._max_storage_size)
        self.error_messages: "LOG_DEQUE_TYPE" = deque(maxlen=self._max_storage_size)
        self.other_messages: "LOG_DEQUE_TYPE" = deque(maxlen=self._max_storage_size)

        self._all_messages: "LOG_DEQUE_TYPE" = deque(maxlen=self._max_storage_size * 6 if self._max_storage_size else None)

        self.table = frozendict({'CRITICAL': self.critical_messages,
                                 'FATAL': self.critical_messages,
                                 'ERROR': self.error_messages,
                                 'WARN': self.warning_messages,
                                 'WARNING': self.warning_messages,
                                 'INFO': self.info_messages,
                                 'DEBUG': self.debug_messages,
                                 "OTHER": self.other_messages,
                                 "ALL": self._all_messages})

    @property
    def all_deques(self) -> tuple["LOG_DEQUE_TYPE"]:
        with self.lock:
            return tuple({k: v for k, v in self.table.items() if k not in {"FATAL", "WARN"}}.values())

    def add_callback(self, typus: Literal["ALL", "DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"], callback: Callable[[Union["LOG_RECORD_TYPES", None]], None]):
        callback_list = self._callbacks[typus]

        callback_list.add(callback)

    def remove_callback(self, typus: Literal["ALL", "DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"], callback: Callable[[Union["LOG_RECORD_TYPES", None]], None]):
        try:
            self._callbacks[typus].remove(callback)
        except KeyError:
            pass

    def send_to_callbacks(self, typus: Literal["ALL", "DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"], record: Union["LOG_RECORD_TYPES", None]):
        for callback in self._callbacks.get(typus, []):
            callback(record)

    def set_max_storage_size(self, max_storage_size: int = None):
        if max_storage_size == self._max_storage_size:
            return
        with self.lock:
            for store in self.table.values():
                store.maxlen = max_storage_size
            self._max_storage_size = max_storage_size

    def handle(self, record: "LOG_RECORD_TYPES"):

        _out = super().handle(record)
        self.send_to_callbacks(typus="ALL", record=record)

        self.send_to_callbacks(typus=re.sub(r"^(FATAL)|(WARN)$", lambda m: "CRITICAL" if m.group() == "FATAL" else "WARNING", record.levelname.upper()), record=record)
        return _out

    def emit(self, record: "LOG_RECORD_TYPES") -> None:

        self.format(record=record)

        with self.lock:
            _deque = self.table.get(record.levelname, self.other_messages)

            _deque.append(record)
            self._all_messages.append(record)

        self.send_to_callbacks(typus="ALL", record=record)

        self.send_to_callbacks(typus=re.sub(r"^(FATAL)|(WARN)$", lambda m: "CRITICAL" if m.group() == "FATAL" else "WARNING", record.levelname.upper()), record=record)

    def get_stored_messages(self) -> dict[str, tuple["LOG_RECORD_TYPES"]]:
        with self.lock:
            return {k: tuple(v) for k, v in self.table.items() if k not in {"FATAL", "WARN"}}

    def get_all_messages(self, formatted: bool = False) -> tuple["LOG_RECORD_TYPES"]:
        with self.lock:
            all_messages = tuple(self._all_messages)
        if formatted is True:
            list(self.format(r) for r in all_messages)

        return all_messages

    def get_formated_messages(self) -> dict[str, tuple[str]]:
        with self.lock:
            _out = {}
            for level, store in self.table.items():
                if level == "FATAL":
                    level = "CRITICAL"
                elif level == "WARN":
                    level = "WARNING"
                _out[level] = tuple(self.format(r) for r in store)
        return _out

    def __len__(self) -> int:
        with self.lock:
            return len(self._all_messages)

    def clear(self, typus: None | Literal["debug", "info", "warning", "critical", "error", "other"] = None):
        if typus is not None:

            with self.lock:

                _deque: "LOG_DEQUE_TYPE" = getattr(self, f"{typus.casefold()}_messages")
                _deque.clear()

                for record in [r for r in self._all_messages if r.levelname.casefold() == typus]:
                    try:
                        self._all_messages.remove(record)
                    except ValueError as e:
                        continue

            self.send_to_callbacks(typus=typus.upper(), record=None)

        else:
            with self.lock:
                self.debug_messages.clear()
                self.info_messages.clear()
                self.warning_messages.clear()
                self.critical_messages.clear()
                self.error_messages.clear()
                self.other_messages.clear()
                self._all_messages.clear()

            self.send_to_callbacks(typus="ALL", record=None)


class AlternativeGidStoringHandler(logging.Handler):

    def __init__(self,
                 max_storage_size: int = 100,
                 level: int = 0) -> None:
        super().__init__(level=level)
        self._max_storage_size: int = max_storage_size
        self._callbacks: frozendict[str, set[Callable[[Union["LOG_RECORD_TYPES", None]], None]]] = frozendict({"ALL": set(),
                                                                                                               "DEBUG": set(),
                                                                                                               "INFO": set(),
                                                                                                               "WARNING": set(),
                                                                                                               "CRITICAL": set(),
                                                                                                               "ERROR": set()})
        self._error_messages: deque[tuple[int, "LOG_RECORD_TYPES"]] = deque(maxlen=self._max_storage_size * 4)
        self._non_error_messages: deque[tuple[int, "LOG_RECORD_TYPES"]] = deque(maxlen=self._max_storage_size)

        self._current_position_number: int = 0

    def _get_next_position_number(self) -> int:
        self._current_position_number += 1
        return self._current_position_number

    def add_callback(self, typus: Literal["ALL", "DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"], callback: Callable[[Union["LOG_RECORD_TYPES", None]], None]):
        callback_list = self._callbacks[typus]

        callback_list.add(callback)

    def remove_callback(self, typus: Literal["ALL", "DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"], callback: Callable[[Union["LOG_RECORD_TYPES", None]], None]):
        try:
            self._callbacks[typus].remove(callback)
        except KeyError:
            pass

    def send_to_callbacks(self, typus: Literal["ALL", "DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"], record: Union["LOG_RECORD_TYPES", None]):
        for callback in self._callbacks.get(typus, []):
            try:
                callback(record)
            except Exception as error:
                if sys.stderr:
                    traceback.print_exception(error.__class__, error)

    def set_max_storage_size(self, max_storage_size: int = None):
        if max_storage_size == self._max_storage_size:
            return
        with self.lock:
            self._max_storage_size = max_storage_size
            self._non_error_messages = deque(self._non_error_messages, self._max_storage_size)

    def handle(self, record: "LOG_RECORD_TYPES"):

        _out = super().handle(record)
        self.send_to_callbacks(typus="ALL", record=record)

        self.send_to_callbacks(typus=re.sub(r"^(FATAL)|(WARN)$", lambda m: "CRITICAL" if m.group() == "FATAL" else "WARNING", record.levelname.upper()), record=record)
        return _out

    def emit(self, record: "LOG_RECORD_TYPES") -> None:

        self.format(record=record)

        with self.lock:
            position_number = self._get_next_position_number()

            if record.levelno == logging.ERROR:
                _deque = self._error_messages

            else:
                _deque = self._non_error_messages

            _deque.append((position_number, record))

        self.send_to_callbacks(typus="ALL", record=record)

        self.send_to_callbacks(typus=re.sub(r"^(FATAL)|(WARN)$", lambda m: "CRITICAL" if m.group() == "FATAL" else "WARNING", record.levelname.upper()), record=record)

    def get_stored_messages(self) -> dict[str, tuple["LOG_RECORD_TYPES"]]:
        with self.lock:
            _messages = {"ERROR": tuple(message[1] for message in self._error_messages)}
            for level_no, level_name in logging._levelToName.items():
                _messages[level_name.upper()] = tuple(message[1] for message in self._non_error_messages if message[1].levelno == level_no)

        return _messages

    def get_all_messages(self, formatted: bool = False) -> tuple["LOG_RECORD_TYPES"]:
        with self.lock:
            all_messages = tuple(message[1] for message in sorted(tuple(self._non_error_messages) + tuple(self._error_messages), key=lambda x: x[0]))
        if formatted is True:
            list(self.format(r) for r in all_messages)

        return all_messages

    def get_formated_messages(self) -> dict[str, tuple[str]]:
        with self.lock:
            _stored_messages = self.get_stored_messages()
            _out = {}

            for key, value in _stored_messages.items():
                _out[key] = tuple(self.format(message) for message in value)
        return _out

    def __len__(self) -> int:
        with self.lock:
            return len(self._non_error_messages) + len(self._error_messages)

    def clear(self, typus: None | Literal["debug", "info", "warning", "critical", "error"] = None):
        if typus is None:
            with self.lock:
                self._error_messages.clear()
                self._non_error_messages.clear()
                self._current_position_number = 0

            self.send_to_callbacks(typus="ALL", record=None)

        elif typus.casefold() == "error":
            with self.lock:

                self._error_messages.clear()

                self.send_to_callbacks(typus=typus.upper(), record=None)

        else:

            with self.lock:

                level_no = logging._nameToLevel[typus.upper()]

                for value in tuple(i for i in self._non_error_messages if i[1].levelno == level_no):
                    self._non_error_messages.remove(value)

            self.send_to_callbacks(typus=typus.upper(), record=None)


# region [Main_Exec]


if __name__ == '__main__':
    ...

# endregion [Main_Exec]
