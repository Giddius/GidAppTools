"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Any
from pathlib import Path
from threading import Event

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BlockingEvent(Event):

    def __init__(self) -> None:
        super().__init__()
        self.set()

    @profile
    def __enter__(self) -> None:
        self.clear()

    @profile
    def __exit__(self, exception_type: type = None, exception_value: BaseException = None, traceback: Any = None) -> None:
        self.set()

    @profile
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(state={self.is_set()!r})'

    @profile
    def wait(self, timeout: float | None = None) -> bool:
        return super().wait(timeout)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
