"""
WiP.

Soon.
"""

# region [Imports]


from enum import Enum, auto
from pathlib import Path
from gidapptools.general_helper.enums import BaseGidEnum

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SpecialTypus(Enum):
    AUTO = auto()
    RAW = auto()
    DELAYED = auto()


class SpecAttribute(BaseGidEnum):
    CONVERTER = "converter"
    DESCRIPTION = "description"
    SHORT_DESCRIPTION = "short_description"


# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
