"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from enum import unique
from typing import TYPE_CHECKING, Union, AnyStr, Literal, Iterable, Callable
from hashlib import md5, sha256, blake2b, blake2s, sha3_512
from pathlib import Path
from threading import RLock

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import BaseGidEnum
from gidapptools.gid_signal.interface import get_signal
from gidapptools.general_helper.timing import get_dummy_profile_decorator_in_globals
from gidapptools.vendored.atomic_writes import atomic_write
from gidapptools.general_helper.conversion import human2bytes
from gidapptools.general_helper.concurrency.locks import GLOBAL_RLOCK_MANAGER

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.custom_types import PATH_TYPE

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]
get_dummy_profile_decorator_in_globals()
THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion [Constants]


READ_TYPE = Union[Literal["r"], Literal["rb"]]
WRITE_TYPE = Union[Literal["w"], Literal["wb"], Literal['a'], Literal['ab']]
ON_ERRORS_TYPE = Union[Literal['replace'], Literal['ignore'], AnyStr]
HASH_FUNC_TYPE = Union[blake2b, md5, sha256, sha3_512, blake2s]


class FileMixin(os.PathLike):
    _encoding = 'utf-8'
    _on_errors: ON_ERRORS_TYPE = 'ignore'

    hash_func: HASH_FUNC_TYPE = md5
    file_hash_size_threshold: int = human2bytes("100 mb")

    @ unique
    class ChangeParameter(BaseGidEnum):
        SIZE = "size"
        FILE_HASH = "file_hash"
        MTIME = "mtime"
        ALWAYS = "always"
        NEVER = "never"
        ALL = "all"

        def get_check_method(self, instance: "FileMixin") -> Callable[[], bool]:
            return getattr(instance, f"_on_{self.value}_changed_check")

    def __init__(self, file_path: "PATH_TYPE", changed_parameter: str = None, missing_ok: bool = True, **kwargs) -> None:
        self.file_path = Path(file_path)
        self.changed_parameter = self.ChangeParameter.SIZE if changed_parameter is None else self.ChangeParameter(changed_parameter)
        self.changed_check_func: Callable[[], bool] = self.changed_parameter.get_check_method(self)
        self.missing_ok = missing_ok
        self.read_mode: READ_TYPE = 'r'
        self.write_mode: WRITE_TYPE = 'w'
        self.last_size: int = None
        self.last_file_hash: str = None
        self.last_mtime: int = None
        self.changed_signal = get_signal(key=self.file_path)
        self.lock: RLock = GLOBAL_RLOCK_MANAGER.get_file_lock(self.file_path)
        self.file_was_created: bool = False
        self._check_handle_not_existing()
        super().__init__(**kwargs)

    @staticmethod
    def _generate_name_from_path(in_file_path: "PATH_TYPE", suffixes_to_remove: Iterable[str] = None) -> str:
        possible_suffixes_to_remove = tuple(suffixes_to_remove) if suffixes_to_remove is not None else tuple()
        in_file_path = Path(in_file_path)
        raw_name = in_file_path.stem
        name = raw_name.strip()
        for possible_suffix in possible_suffixes_to_remove:
            name = name.removesuffix(possible_suffix)
        return name.strip().strip("_")

    def set_changed_parameter(self, changed_parameter: Union["ChangeParameter", str]) -> None:
        if isinstance(changed_parameter, self.ChangeParameter):
            self.changed_parameter = changed_parameter
        else:
            self.changed_parameter = self.ChangeParameter(changed_parameter)

        self.changed_check_func = self.changed_parameter.get_check_method(self)

    def _check_handle_not_existing(self) -> None:
        with self.lock:
            if self.file_path.exists() is True:
                return
            if self.missing_ok is True:
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                self.file_path.touch(exist_ok=True)
                self._update_changed_data()
                self.file_was_created = True

            else:
                raise FileNotFoundError(f"file for {self.__class__.__name__!r} -> {self.file_path.as_posix()!r} does exist.")

    @ property
    def file_name(self) -> str:
        return self.file_path.name

    @ property
    def size(self) -> int:
        self._check_handle_not_existing()
        size = self.file_path.stat().st_size
        return size

    @ property
    def file_hash(self) -> str:
        self._check_handle_not_existing()
        with self.file_path.open('rb') as f:
            if self.size <= self.file_hash_size_threshold:

                return self.hash_func(f.read()).hexdigest()
            _file_hash = self.hash_func()
            for chunk in f:
                _file_hash.update(chunk)
            return _file_hash.hexdigest()

    @ property
    def mtime(self) -> int:
        self._check_handle_not_existing()
        return self.file_path.stat().st_mtime

    def _on_size_changed_check(self) -> bool:
        return self.last_size is None or self.last_size != self.size

    def _on_file_hash_changed_check(self) -> bool:
        return self.last_file_hash is None or self.last_file_hash != self.file_hash

    def _on_mtime_changed_check(self) -> bool:
        return self.last_mtime is None or self.last_mtime != self.mtime

    def _on_all_changed_check(self) -> bool:
        return any([self._on_size_changed_check(), self._on_file_hash_changed_check(), self._on_mtime_changed_check()])

    def _on_always_changed_check(self) -> bool:
        return True

    def _on_never_changed_check(self) -> bool:
        return False

    @ property
    def has_changed(self) -> bool:
        with self.lock:
            result = self.changed_check_func()
            if result is True:
                self.changed_signal.delayed_fire_and_forget(1, self)
        return result

    def _update_changed_data(self) -> None:

        def _update_size():
            self.last_size = self.size

        def _update_file_hash():
            self.last_file_hash = self.file_hash

        def _update_mtime():
            self.last_mtime = self.mtime

        def _update_all():
            _update_size()
            _update_file_hash()
            _update_mtime()
        update_table = {self.ChangeParameter.NEVER: lambda: ...,
                        self.ChangeParameter.ALWAYS: lambda: ...,
                        self.ChangeParameter.SIZE: _update_size,
                        self.ChangeParameter.FILE_HASH: _update_file_hash,
                        self.ChangeParameter.MTIME: _update_mtime,
                        self.ChangeParameter.ALL: _update_all}
        update_table[self.changed_parameter]()

    @ property
    def _read_kwargs(self) -> dict[str, str]:
        kwargs = {"mode": self.read_mode}
        if 'b' not in self.read_mode:
            kwargs['encoding'] = self._encoding
            kwargs['errors'] = self._on_errors
        return kwargs

    @ property
    def _write_kwargs(self) -> dict[str, str]:
        kwargs = {"mode": self.write_mode}
        if 'b' not in self.write_mode:
            kwargs['encoding'] = self._encoding
            kwargs['errors'] = self._on_errors
        return kwargs

    def read(self):
        self._check_handle_not_existing()
        with self.lock:
            self._update_changed_data()
            # pylint: disable=unspecified-encoding
            with self.file_path.open(**self._read_kwargs) as f:
                return f.read()

    def write(self, data) -> None:
        with self.lock:
            # pylint: disable=unspecified-encoding
            with atomic_write(self.file_path, overwrite=True, **self._write_kwargs) as f:
                f.write(data)

    def __fspath__(self) -> str:
        return str(self.file_path)

    def __str__(self) -> str:
        return self.__fspath__()
# region [Main_Exec]


if __name__ == '__main__':
    pass
# endregion [Main_Exec]
