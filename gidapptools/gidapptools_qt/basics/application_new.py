"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
from typing import Union, Iterable, Optional, Protocol
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
from yarl import URL

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtWidgets import QApplication

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_utility.version_item import VersionItem

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ApplicationInfo(Protocol):
    app_name: str
    app_author: str
    version: Optional[Union[str, VersionItem]]
    url: Optional[Union[str, URL]]


class GidBaseApplication(QApplication):

    def __init__(self, argv: Iterable[str] = None):
        super().__init__(argv or sys.argv)
        self.is_setup: bool = False

    @classmethod
    def is_ready(cls) -> bool:
        return cls.startingUp() is False and cls.instance().is_setup is True

    def setup(self,
              application_core_info: "ApplicationCoreInfo") -> "GidBaseApplication":
        ...
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
