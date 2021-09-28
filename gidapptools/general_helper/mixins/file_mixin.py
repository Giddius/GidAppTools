"""
WiP.

Soon.
"""

# region [Imports]


from enum import auto, unique
from pathlib import Path
from typing import AnyStr, Literal, Union
from contextlib import nullcontext
from collections import defaultdict
from threading import Lock
from _thread import LockType
from gidapptools.general_helper.enums import BaseGidEnum
from hashlib import blake2b, md5, sha256, sha3_512, blake2s
from gidapptools.general_helper.timing import time_func
from gidapptools.general_helper.conversion import human2bytes, bytes2human
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]


@unique
class ChangeParameter(BaseGidEnum):
    SIZE = auto()
    FILE_HASH = auto()
    TIME = auto()
    ALWAYS = auto()
    NEVER = auto()
    ALL = auto()


READ_TYPE = Union[Literal["r"], Literal["rb"]]
WRITE_TYPE = Union[Literal["w"], Literal["wb"], Literal['a'], Literal['ab']]
ON_ERRORS_TYPE = Union[Literal['replace'], Literal['ignore'], AnyStr]
HASH_FUNC_TYPE = Union[blake2b, md5, sha256, sha3_512, blake2s]


class FileMixin:
    hash_func: HASH_FUNC_TYPE = md5
    file_hash_size_threshold: int = human2bytes("100 mb")
    path_locks: defaultdict[Path, Lock] = defaultdict(Lock)

    def __init__(self, file_path: Path) -> None:
        self.file_path = Path(file_path)
        self.changed_parameter = ChangeParameter.SIZE
        self.last_size: int = None
        self.last_file_hash: str = None
        self.last_changed_time: int = None
        self._read_mode: READ_TYPE = 'r'
        self._write_mode: WRITE_TYPE = 'w'
        self._encoding: str = 'utf-8'
        self._on_errors: ON_ERRORS_TYPE = 'ignore'
        self.ensure: bool = False

    @property
    def lock(self) -> Lock:
        lock = self.path_locks[self.file_path]
        return lock

    @property
    def size(self) -> int:
        size = self.file_path.stat().st_size
        return size

    @property
    def file_hash(self) -> str:
        with self.file_path.open('rb') as f:
            if self.size <= self.file_hash_size_threshold:

                return self.hash_func(f.read()).hexdigest()
            _file_hash = self.hash_func()
            for chunk in f:
                _file_hash.update(chunk)
            return _file_hash.hexdigest()

    @property
    def changed_time(self) -> int:
        return self.file_path.stat().st_mtime

    @property
    def has_changed(self) -> bool:
        def on_size() -> bool:
            return self.last_size is None or self.last_size != self.size

        def on_file_hash() -> bool:
            return self.last_file_hash is None or self.last_file_hash != self.file_hash

        def on_time() -> bool:
            return self.last_changed_time is None or self.last_changed_time != self.changed_time

        def on_all() -> bool:
            return any([on_size(), on_file_hash(), on_time()])

        def on_always() -> bool:
            return True

        def on_never() -> bool:
            return False
        checks = {ChangeParameter.SIZE: on_size,
                  ChangeParameter.FILE_HASH: on_file_hash,
                  ChangeParameter.TIME: on_time,
                  ChangeParameter.ALL: on_all,
                  ChangeParameter.ALWAYS: on_always,
                  ChangeParameter.NEVER: on_never}
        return checks[self.changed_parameter]()

    @property
    def _read_kwargs(self) -> dict[str, str]:
        kwargs = {"mode": self._read_mode}
        if 'b' not in self._read_mode:
            kwargs['encoding'] = self._encoding
            kwargs['errors'] = self._on_errors
        return kwargs

    @property
    def _write_kwargs(self) -> dict[str, str]:
        kwargs = {"mode": self._write_mode}
        if 'b' not in self._write_mode:
            kwargs['encoding'] = self._encoding
            kwargs['errors'] = self._on_errors
        return kwargs

    def create(self, *, inside_lock: bool = False) -> None:
        possible_lock = self.lock if inside_lock is False else nullcontext()
        with possible_lock:
            self.file_path.touch()

    def read(self, *, inside_lock: bool = False):
        possible_lock = self.lock if inside_lock is False else nullcontext()

        with possible_lock:
            try:
                self.last_size = self.size
                self.last_file_hash = self. file_hash
                self.last_changed_time = self.changed_time
                # pylint: disable=unspecified-encoding
                with self.file_path.open(**self._read_kwargs) as f:
                    return f.read()
            except FileNotFoundError:
                if self.ensure is True:
                    if isinstance(possible_lock, LockType):
                        inside_lock = True
                    self.create(inside_lock=inside_lock)
                    return self.read(inside_lock=inside_lock)
                else:
                    raise

    def write(self, data, *, inside_lock: bool = False) -> None:
        possible_lock = self.lock if inside_lock is False else nullcontext()

        with possible_lock:
            # pylint: disable=unspecified-encoding
            with self.file_path.open(**self._write_kwargs) as f:
                f.write(data)
# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
