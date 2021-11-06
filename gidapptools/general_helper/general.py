"""
WiP.

Soon.
"""

# region [Imports]


from pathlib import Path
from typing import Any
import sys

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def defaultable_list_pop(in_list: list, idx: int, default: Any = None) -> Any:
    if in_list is None:
        return default
    try:
        return in_list.pop(idx)
    except IndexError:
        return default


def is_frozen() -> bool:
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
