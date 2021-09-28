"""
WiP.

Soon.
"""

# region [Imports]


from enum import Enum, auto, unique
from pathlib import Path
from gidapptools.utility.enums import BaseGidEnum

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


@unique
class MiscEnum(Enum):
    NOTHING = auto()
    ALL = auto()
    DEFAULT = auto()
    NOT_FOUND = auto()

    def __repr__(self) -> str:
        return self.name


class StringCase(BaseGidEnum):
    SNAKE = auto()
    SCREAMING_SNAKE = auto()
    CAMEL = auto()
    PASCAL = auto()
    KEBAP = auto()
    SPLIT = auto()
    TITLE = auto()
    UPPER = auto()
    # aliases
    CLASS = PASCAL


class FileTypus(BaseGidEnum):
    TXT = auto()
    MD = auto()
    INI = auto()
    JSON = auto()
    PY = auto()
    TOML = auto()
    YAML = auto()
    EXE = auto()
    BAT = auto()
    PS1 = auto()

    # aliases
    CMD = BAT
    YML = YAML
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
