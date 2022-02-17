"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import sys
from contextlib import contextmanager
import queue
import atexit
from weakref import WeakSet, WeakValueDictionary
import logging
from typing import Union, Iterable, Mapping, TYPE_CHECKING, Any, Optional
from pathlib import Path
from logging.handlers import QueueHandler, QueueListener

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_logger.enums import LoggingLevel
from gidapptools.gid_logger.handler import GidBaseRotatingFileHandler, GidBaseStreamHandler, GidStoringHandler
from gidapptools.gid_logger.formatter import GidLoggingFormatter, get_all_func_names, get_all_module_names

if TYPE_CHECKING:
    from gidapptools.gid_logger.records import LOG_RECORD_TYPES

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidLogger(logging.Logger):

    def __init__(self, name: str, level: "logging._Level" = logging.NOTSET) -> None:
        super().__init__(name, level)
        self.que_listener: QueueListener = None
        self._que_handlers = WeakSet()

    @property
    def all_handlers(self) -> dict[str, tuple[logging.Handler]]:
        return {"handlers": tuple(self.handlers),
                "que_handlers": tuple(self._que_handlers)}

    def set_que_listener(self, que_listener: QueueListener):
        self.que_listener = que_listener
        for handler in que_listener.handlers:
            self._que_handlers.add(handler)

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
        rv = super().makeRecord(name, level, fn, lno, msg, args=args, exc_info=exc_info, func=func, extra=None, sinfo=sinfo)
        if not hasattr(rv, "extras"):
            setattr(rv, "extras", {})
        if extra is not None:
            rv.extras |= extra

        return rv


@contextmanager
def switch_logger_klass(logger_klass: type[logging.Logger]):
    original_logger_klass = logging.getLoggerClass()
    try:
        logging.setLoggerClass(logger_klass)
        yield
    finally:
        logging.setLoggerClass(original_logger_klass)


def _modify_logger_name(name: str) -> str:
    if name == "__main__":
        return 'main'
    name = 'main.' + '.'.join(name.split('.')[1:])
    return name


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


def setup_main_logger(name: str, path: Path, log_level: LoggingLevel = LoggingLevel.DEBUG, formatter: Union[logging.Formatter, GidLoggingFormatter] = None, extra_logger: Iterable[str] = tuple()) -> Union[logging.Logger, GidLogger]:
    os.environ["MAX_FUNC_NAME_LEN"] = str(min([max(len(i) for i in get_all_func_names(path, True)), 20]))
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
                                        stream=sys.stdout) -> Union[logging.Logger, GidLogger]:
    if os.getenv('IS_DEV', "false") != "false":
        log_folder = path.parent.joinpath('logs')

    os.environ["MAX_FUNC_NAME_LEN"] = str(max_func_name_length) if max_func_name_length is not None else "25"
    os.environ["MAX_MODULE_NAME_LEN"] = str(max_module_name_length) if max_module_name_length is not None else "25"

    que = queue.Queue(-1)
    que_handler = QueueHandler(que)

    formatter = GidLoggingFormatter() if formatter is None else formatter
    endpoints = []
    if stream is not None:
        handler = GidBaseStreamHandler(stream=stream)
        handler.setFormatter(formatter)
        endpoints.append(handler)

    file_handler = GidBaseRotatingFileHandler(base_name=log_file_base_name, log_folder=log_folder)
    file_handler.setFormatter(formatter)
    endpoints.append(file_handler)
    storing_handler = GidStoringHandler()
    storing_handler.setFormatter(formatter)
    endpoints.append(storing_handler)
    listener = QueueListener(que, *endpoints)
    _log = get_logger(name)
    log_level = LoggingLevel(log_level)
    if "py.warnings" in extra_logger:
        logging.captureWarnings(True)
    for logger in [_log] + [logging.getLogger(l) for l in extra_logger]:
        logger.addHandler(que_handler)

        logger.setLevel(log_level)
    listener.start()
    atexit.register(listener.stop)
    _log.set_que_listener(listener)
    return _log


def get_main_logger():
    return get_logger("__main__")
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
