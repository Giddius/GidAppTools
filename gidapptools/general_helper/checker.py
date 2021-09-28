"""
WiP.

Soon.
"""

# region [Imports]


from pathlib import Path
from typing import Any


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def is_hashable(obj: Any) -> bool:
    try:
        hash(obj)
        return True
    except TypeError as error:
        if 'unhashable' in str(error).casefold():
            return False
        raise


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
