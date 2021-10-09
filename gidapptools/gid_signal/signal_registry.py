"""
[summary]

[extended_summary]
"""

# region [Imports]
import json
from pathlib import Path, PurePath, PurePosixPath
import os
from typing import Union, Optional, Iterable, Mapping, Any, Callable, TYPE_CHECKING, AsyncContextManager

import asyncio

from weakref import WeakSet, WeakValueDictionary, WeakMethod, ref
from abc import ABC, ABCMeta, abstractmethod

import inspect
if TYPE_CHECKING:
    from gidapptools.gid_signal.signals.abstract_signal import AbstractSignal
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [AppUserData]


# endregion [AppUserData]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(os.path.dirname(__file__)).absolute()

# endregion[Constants]


class SignalRegistry(WeakValueDictionary):

    def register(self, signal: "AbstractSignal"):
        key = signal.key
        self[key] = signal

    def unregister(self, signal: Union[str, "AbstractSignal"]):
        signal_key = signal.key if isinstance(signal, AbstractSignal) else signal
        self.pop(signal_key)

    def get(self, key: str, default=None) -> "AbstractSignal":
        return super().get(key=key, default=default)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(signals={list(self.data)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(signals={list(self.data)})"

    def clear(self) -> None:
        for key in list(self):
            del self[key]


signal_registry = SignalRegistry()


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
