"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
from typing import Union, Iterable, Optional, Protocol, TYPE_CHECKING
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
from yarl import URL

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtWidgets import QApplication

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_utility.version_item import VersionItem
import sys
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
if TYPE_CHECKING:
    from gidapptools.meta_data.meta_info.meta_info_item import MetaInfo

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


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

    def setup_from_meta_info(self,
                             meta_info: "MetaInfo") -> Self:
        ...

    def setup(self,
              app_name: str = None,
              app_author: str = None,
              version: Union[str, "VersionItem"] = None,
              url: Union[URL, str] = None) -> Self:
        ...
# region [Main_Exec]


if __name__ == '__main__':
    pass

# endregion [Main_Exec]
