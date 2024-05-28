"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from typing import ClassVar, Optional, Union
from pathlib import Path
import json
import sys
import re
# * Third Party Imports --------------------------------------------------------------------------------->
import attrs
from threading import Lock
import psutil
from math import ceil, floor
# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import ApplicationInstanceAlreadyRunningError, show_basic_error_pop_up
from gidapptools.custom_types import PATH_TYPE
from gidapptools.general_helper.path_helper import ensure_valid_file_stem
import sys
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


@attrs.define(frozen=True, slots=True)
class LockFileData:
    text_separator: ClassVar[str] = "|:|"
    app_name: str = attrs.field()
    pid: int = attrs.field()
    creation_time: float = attrs.field()

    @creation_time.default
    def _default_creation_time(self) -> float:
        return floor(self.get_process().create_time())

    def get_process(self) -> Union[None, psutil.Process]:
        try:
            process = psutil.Process(self.pid)

            if process.is_running() is False:
                return None

            return process

        except psutil.NoSuchProcess:
            return None

    @property
    def is_running(self) -> bool:
        process = self.get_process()

        if process is None:
            return False

        if floor(process.create_time()) != self.creation_time:
            return False

        return True

    @classmethod
    def from_file(cls, file_path: PATH_TYPE) -> "LockFileData":
        content = Path(file_path).resolve().read_text(encoding='utf-8', errors='ignore').strip()
        app_name, raw_pid, raw_creation_time = (p.strip() for p in content.split(cls.text_separator))
        pid = int(raw_pid)
        creation_time = floor(float(raw_creation_time))
        return cls(app_name=app_name, pid=pid, creation_time=creation_time)

    def to_text(self) -> str:
        return f"{self.app_name}{self.text_separator}{self.pid}{self.text_separator}{self.creation_time}"


_SAFETY_LOCK = Lock()


class SingleRunningInstanceRestrictor:
    _lock_file_suffix: str = ".running_instance"

    def __init__(self, storage_folder: PATH_TYPE, app_name: str) -> None:
        self._storage_folder = Path(storage_folder).resolve()
        self._app_name = app_name
        self._pid = os.getpid()
        self._current_process_lock_file_data = LockFileData(app_name=self._app_name, pid=self._pid)
        self._lock_file_path: Path = (self._storage_folder / (ensure_valid_file_stem(self._app_name, True, True) + self._lock_file_suffix)).resolve()
        self._lock_succeded: bool = False

    @property
    def lock_file_name(self) -> str:
        return self._lock_file_path.name

    @property
    def lock_file_path(self) -> Path:
        return self._lock_file_path

    @property
    def lock_file_exists(self) -> bool:
        return self.lock_file_path.is_file()

    def get_existing_lock_file_data(self) -> LockFileData:
        return LockFileData.from_file(self.lock_file_path)

    def store_in_lock_file(self) -> None:
        self.lock_file_path.parent.mkdir(exist_ok=True, parents=True)
        self.lock_file_path.write_text(self._current_process_lock_file_data.to_text(), encoding='utf-8', errors='ignore')
        self._lock_succeded = True

    def on_other_instance_running(self) -> None:
        other_instance_data = self.get_existing_lock_file_data()
        raise ApplicationInstanceAlreadyRunningError(app_name=other_instance_data.app_name, running_pid=other_instance_data.pid)

    def aquire(self):
        with _SAFETY_LOCK:
            if self.lock_file_exists is True:
                existing_instance_data = self.get_existing_lock_file_data()

                if existing_instance_data.is_running is True and existing_instance_data.app_name == self._app_name:
                    self.on_other_instance_running()
                else:

                    self.store_in_lock_file()
            else:
                self.store_in_lock_file()

    def release(self):
        with _SAFETY_LOCK:
            if self._lock_succeded is True:
                self.lock_file_path.unlink(missing_ok=True)

    def __enter__(self) -> Self:
        self.aquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not ApplicationInstanceAlreadyRunningError:
            self.release()

    def __del__(self) -> None:
        self.release()


class GUISingleRunningInstanceRestrictor(SingleRunningInstanceRestrictor):

    def on_other_instance_running(self):

        other_instance_data = self.get_existing_lock_file_data()
        show_basic_error_pop_up(f"A different instance of {self._app_name!r} is already running!")

        raise ApplicationInstanceAlreadyRunningError(app_name=other_instance_data.app_name, running_pid=other_instance_data.pid)


# region [Main_Exec]
if __name__ == '__main__':
    ...

# endregion [Main_Exec]
