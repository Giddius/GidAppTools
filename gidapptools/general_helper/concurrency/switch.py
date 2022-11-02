"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
from typing import TYPE_CHECKING
from pathlib import Path
from threading import RLock

if sys.version_info >= (3, 11):
    pass
else:
    pass
# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    ...

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class Switch:
    __slots__ = ("_lock", "_state")

    def __init__(self, initial_state: bool = False) -> None:
        self._lock = RLock()
        self._state = initial_state

    @property
    def state(self) -> bool:
        with self._lock:
            return self._state

    @property
    def is_true(self) -> bool:
        with self._lock:
            return self.state is True

    @property
    def is_false(self) -> bool:
        with self._lock:
            return self.state is False

    def switch_to(self, new_state: bool) -> None:
        with self._lock:
            self._state = new_state

    def switch(self) -> bool:
        with self._lock:
            self.switch_to(not self.state)
            return self.state

    def __bool__(self) -> bool:
        return self.state

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.state!r})"

# region[Main_Exec]


if __name__ == '__main__':
    pass


# endregion[Main_Exec]
