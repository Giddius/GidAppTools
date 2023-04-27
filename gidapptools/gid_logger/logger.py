"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import re
import sys
import queue
import atexit
import logging
import traceback
import warnings
from typing import TYPE_CHECKING, Any, Union, Mapping, Callable, Iterable, Optional, TextIO, TypeAlias
from pathlib import Path
from types import ModuleType
from weakref import WeakValueDictionary
from contextlib import contextmanager
from logging.handlers import QueueHandler, QueueListener
import importlib
# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_logger.enums import LoggingLevel
from gidapptools.gid_logger.handler import GidBaseStreamHandler, GidBaseRotatingFileHandler
from gidapptools.gid_logger.formatter import GidLoggingFormatter, get_all_func_names, get_all_module_names
from gidapptools.general_helper.conversion import str_to_bool

import sys
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.gid_logger.records import LOG_RECORD_TYPES

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def is_dev() -> bool:
    is_dev_string = os.getenv("IS_DEV", '0').casefold()
    return str_to_bool(is_dev_string, strict=True) or sys.flags.dev_mode


class GidLogger(logging.Logger):
    main_pack_name: str = None

    def __init__(self, name: str, level: "logging._Level" = logging.NOTSET) -> None:
        super().__init__(name, level)
        self.que_listener: QueueListener = None
        self._que_handlers: WeakValueDictionary[str, logging.Handler] = WeakValueDictionary()

    @property
    def all_handlers(self) -> dict[str, tuple[logging.Handler]]:
        return {"handlers": tuple(self.handlers),
                "que_handlers": dict(self._que_handlers)}

    def set_que_listener(self, que_listener: QueueListener):
        def _determine_handler_name(in_handler: logging.Handler) -> str:
            if hasattr(in_handler, "name") and in_handler.name is not None:
                return in_handler.name
            return in_handler.__class__.__name__

        self.que_listener = que_listener
        for handler in que_listener.handlers:
            self._que_handlers[_determine_handler_name(handler)] = handler

    def makeRecord(self,
                   name: str,
                   level: int,
                   fn: str,
                   lno: int,
                   msg: object,
                   args: "logging._ArgsType",
                   exc_info: "logging._SysExcInfoType" = None,
                   func: str = None,
                   extra: Mapping[str, object] = None,
                   sinfo: str = None) -> "LOG_RECORD_TYPES":
        rv = super().makeRecord(name, level, fn, lno, msg, args=args, exc_info=exc_info, func=func, extra=extra, sinfo=sinfo)
        if not hasattr(rv, "extras"):
            setattr(rv, "extras", {})
        if extra is not None:
            rv.extras |= extra

        return rv

    def _log(self, level: int, msg: object, args: "logging._ArgsType", exc_info: "logging._ExcInfoType" = None, extra: Mapping[str, object] = None, stack_info: bool = False, stacklevel: int = 2) -> None:
        if extra is not None and extra.get("is_timing_decorator", False) is True:
            stacklevel += 0
        return super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


class MetaLogger(GidLogger):

    def _log(self, level: int, msg: object, args: "logging._ArgsType", exc_info: "logging._ExcInfoType" = None, extra: Mapping[str, object] = None, stack_info: bool = False, stacklevel: int = 2) -> None:
        extra = extra or {}
        extra["is_meta"] = True

        return super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


def make_library_logger(in_name: str) -> logging.Logger:
    logger = logging.getLogger(in_name)
    logger.addHandler(logging.NullHandler())
    return logger


@contextmanager
def switch_logger_klass(logger_klass: type[logging.Logger]):
    original_logger_klass = logging.getLoggerClass()
    try:
        logging.setLoggerClass(logger_klass)
        yield
    finally:
        logging.setLoggerClass(original_logger_klass)


def _modify_logger_name(name: str) -> str:
    if name == "__logging_meta__":
        return 'main.__logging_meta__'
    # name = 'main.' + '.'.join(name.split('.')[1:])
    if name.startswith("__main__"):
        return name.replace("__main__", "main")

    if GidLogger.main_pack_name is not None:

        return name.replace(GidLogger.main_pack_name, "main")

    return name


def get_main_logger() -> logging.Logger:
    return get_logger("__main__")


META_LOGGER_NAME = "__logging_meta__"


def get_meta_logger():
    main_logger = get_main_logger()
    with switch_logger_klass(MetaLogger):
        return main_logger.getChild(META_LOGGER_NAME)


def get_logger(name: str) -> Union[logging.Logger, GidLogger]:
    name = _modify_logger_name(name)
    with switch_logger_klass(GidLogger):
        return logging.getLogger(name)


def get_handlers(logger: Union[logging.Logger, GidLogger] = None) -> tuple[logging.Handler]:
    logger = logger or get_main_logger()
    handlers = logger.handlers
    all_handlers = []
    for handler in handlers:
        all_handlers.append(handler)
    return tuple(all_handlers)


class WarningItem:
    __slots__ = ("_message",
                 "category",
                 "_raw_filename",
                 "lineno",
                 "file",
                 "line",
                 "module",
                 "resolved_filename",
                 "func_name",
                 "_is_resolved")

    def __init__(self,
                 message: str,
                 category: type[Warning],
                 filename: str,
                 lineno: int,
                 file: Optional[TextIO] = None,
                 line: str = None) -> None:
        self._message = message
        self.category = category
        self._raw_filename = filename
        self.lineno = lineno
        self.file = file
        self.line = line

        self.module: Optional[ModuleType] = None
        self.resolved_filename: Optional[Path] = None
        self.func_name: Optional[str] = None
        self._is_resolved: bool = False

    @property
    def message(self) -> str:
        return str(self._message).rstrip("\n")

    @property
    def is_frozen_stdlib(self) -> bool:
        return self._raw_filename.startswith("<frozen ") and self._raw_filename.endswith(">")

    @property
    def filename(self) -> str:
        if self.resolved_filename is None:
            return self._raw_filename
        return str(self.resolved_filename)

    @property
    def file_path(self) -> Optional[Path]:
        if self.resolved_filename is not None:
            return self.resolved_filename
        return None

    @property
    def module_name(self) -> str:
        if self.module is not None:
            return self.module.__name__

        if self.is_frozen_stdlib is True:
            return self.filename.removeprefix("<frozen ").removesuffix(">").strip()

        return self.filename

    def _resolve_filename(self) -> None:
        if self._raw_filename.startswith("<frozen ") and self._raw_filename.endswith(">"):
            package_name, *sub_names = self._raw_filename.removeprefix("<frozen ").removesuffix(">").strip().rsplit(".", 1)
            package = sys.modules[package_name]
            module = package
            for sub_name in sub_names:
                module = getattr(module, sub_name)
            self.module = module
            self.resolved_filename = Path(module.__file__).resolve()

        elif os.path.isfile(self._raw_filename) is True:
            self.resolved_filename = Path(self._raw_filename).resolve()
            for _module in tuple(sys.modules.values()):
                if Path(_module.__name__).resolve() == self.resolved_filename:
                    self.module = _module
                    break

    def _resolve_line(self) -> None:
        if self.resolved_filename is None:
            return
        import linecache
        temp_lineno = self.lineno
        line = linecache.getline(str(self.resolved_filename), temp_lineno)
        if self.line is None:
            self.line = line.rstrip()

        while True:
            if match := func_pattern.search(line):
                self.func_name = match.group("func_name").strip()
                break
            temp_lineno -= 1
            if temp_lineno < 0:
                self.func_name = "module"
                break
            line = linecache.getline(str(self.resolved_filename), temp_lineno)

    def resolve(self) -> Self:
        if self._is_resolved is True:
            return
        self._resolve_filename()
        self._resolve_line()
        self._is_resolved = True
        return self

    def get_logging_params(self) -> dict[str, object]:
        _out = {}
        _out["name"] = self.module_name
        _out["level"] = logging.WARNING
        _out["fn"] = self.func_name
        _out["lno"] = self.lineno
        _out["msg"] = self.message
        _out["args"] = tuple()
        _out["exc_info"] = None
        _out["func"] = self.func_name

        return _out

    def __repr__(self) -> str:
        _out = self.__class__.__name__ + "("

        for attr_name in [i for i in self.__slots__ if not i.startswith("_")] + ["message", "filename", "is_frozen_stdlib"]:
            _out += f"{attr_name}={getattr(self, attr_name)!r}, "

        _out.removesuffix(", ")
        _out += ")"
        return _out

    def __str__(self) -> str:
        return self.message


func_pattern = re.compile(r"(^| )def (?P<func_name>[^\(\)\n\"\'\]\[]+)")


SHOW_WARNING_FUNC_TYPE: TypeAlias = Callable[[str, type[Warning], str, int, Optional[str], Optional[str]], None]


class WarningHandler:
    __slots__ = ("_old_show_warnings_func",)

    def __init__(self, old_show_warnings_func: Optional[SHOW_WARNING_FUNC_TYPE] = None) -> None:
        self._old_show_warnings_func = old_show_warnings_func or self._fallback_show_warning

    @property
    def meta_logger(self) -> logging.Logger:
        return get_meta_logger()

    def _fallback_show_warning(self, message: str, category: type[Warning], filename: str, lineno: int, file: Optional[TextIO] = None, line: Optional[str] = None) -> None:
        self.meta_logger.warning("%s - %s:%s:%r - %s", category.__name__, filename, lineno, line or "", message)

    def _show_warnings(self, message: str, category: type[Warning], filename: str, lineno: int, file: Optional[TextIO] = None, line: Optional[str] = None) -> None:
        try:
            warning_item = WarningItem(message=message, category=category, filename=filename, lineno=lineno, file=file, line=line).resolve()
            logger = get_logger(f"__main__.{warning_item.module_name}")
            record = logger.makeRecord(**warning_item.get_logging_params())
            logger.handle(record)
        except Exception as e:
            self.meta_logger.error(e, exc_info=True)
            self._old_show_warnings_func(message=message, category=category, filename=filename, lineno=lineno, line=line)

    def __call__(self, message: str, category: type[Warning], filename: str, lineno: int, file: Optional[TextIO] = None, line: str = None) -> None:
        self._show_warnings(message=message, category=category, filename=filename, lineno=lineno, file=file, line=line)


def setup_main_logger(name: str,
                      path: Path,
                      log_level: LoggingLevel = LoggingLevel.DEBUG,
                      formatter: Union[logging.Formatter, GidLoggingFormatter] = None,
                      extra_logger: Iterable[str] = tuple(),
                      *,
                      determine_max_module_len: bool = False,
                      determine_max_func_name_len: bool = False) -> Union[logging.Logger, GidLogger]:
    if determine_max_func_name_len:
        os.environ["MAX_FUNC_NAME_LEN"] = str(min([max(len(i) for i in get_all_func_names(path, True)), 20]))
    if determine_max_module_len:
        os.environ["MAX_MODULE_NAME_LEN"] = str(min([max(len(i) for i in get_all_module_names(path)), 20]))

    handler = GidBaseStreamHandler(stream=sys.stdout)

    que = queue.Queue(-1)
    que_handler = QueueHandler(que)
    listener = QueueListener(que, handler)
    formatter = GidLoggingFormatter() if formatter is None else formatter
    handler.setFormatter(formatter)
    _log = get_logger(name)
    for logger in [_log] + [logging.getLogger(l) for l in extra_logger]:
        logger.addHandler(que_handler)

        logger.setLevel(log_level)
    _log.addHandler(que_handler)
    _log.setLevel(log_level)
    listener.start()
    atexit.register(listener.stop)
    return _log


def setup_main_logger_with_file_logging(name: str,
                                        log_file_base_name: str,
                                        path: Path,
                                        log_level: LoggingLevel = LoggingLevel.DEBUG,
                                        formatter: Union[logging.Formatter, GidLoggingFormatter] = None,
                                        log_folder: Path = None,
                                        extra_logger: Iterable[str] = tuple(),
                                        max_func_name_length: int = None,
                                        max_module_name_length: int = None,
                                        *,
                                        log_to_file: bool = True,
                                        log_to_stdout: bool = True,
                                        main_pack_name: str = None) -> Union[logging.Logger, GidLogger]:
    GidLogger.main_pack_name = main_pack_name
    if is_dev() is True:
        log_folder = path.parent.joinpath('logs')

    os.environ["MAX_FUNC_NAME_LEN"] = str(max_func_name_length) if max_func_name_length is not None else str(min([max(len(i) for i in get_all_func_names(path, True)), 25]))
    os.environ["MAX_MODULE_NAME_LEN"] = str(max_module_name_length) if max_module_name_length is not None else str(min([max(len(i) for i in get_all_module_names(path)), 25]))

    que = queue.Queue()
    que_handler = QueueHandler(que)

    formatter = GidLoggingFormatter() if formatter is None else formatter
    endpoints = []
    if log_to_stdout is True:
        handler = GidBaseStreamHandler()
        handler.setFormatter(formatter)
        endpoints.append(handler)
    if log_to_file is True:
        file_handler = GidBaseRotatingFileHandler(base_name=log_file_base_name, log_folder=log_folder)

        file_handler.setFormatter(formatter)
        endpoints.append(file_handler)
    # storing_handler = GidStoringHandler(50)
    # storing_handler.setFormatter(formatter)
    # endpoints.append(storing_handler)

    listener = QueueListener(que, *endpoints)
    _log = get_logger(name)
    log_level = LoggingLevel(log_level)
    if "py.warnings" in extra_logger:
        logging.captureWarnings(True)
        warning_handler = WarningHandler(warnings.showwarning)
        warnings.showwarning = warning_handler
    for logger in [_log] + [logging.getLogger(l) for l in extra_logger]:
        logger.addHandler(que_handler)

        logger.setLevel(log_level)
    listener.start()
    atexit.register(listener.stop)
    _log.set_que_listener(listener)
    return _log


# region [Main_Exec]

if __name__ == '__main__':
    pass

# endregion [Main_Exec]
