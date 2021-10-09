"""
WiP.

Soon.
"""

# region [Imports]


import os


import platform


from pathlib import Path
from typing import Any, Callable, Optional
from datetime import datetime
from itertools import cycle
from gidapptools.errors import NotBaseInitFileError
from urlextract import URLExtract
import attr
import requests
from yarl import URL
from tzlocal import get_localzone
from gidapptools.utility.enums import OperatingSystem
from gidapptools.utility.helper import memory_in_use, handle_path, utc_now, make_pretty
from gidapptools.general_helper.conversion import bytes2human
from gidapptools.general_helper.date_time import DatetimeFmt
from gidapptools.types import PATH_TYPE
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem
# REMOVE_BEFORE_BUILDING_DIST
from gidapptools.utility._debug_tools import dprint

print = dprint

# end REMOVE_BEFORE_BUILDING_DIST


# endregion[Imports]

# region [TODO]

# - Make into a class

# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

def url_converter(in_url: str) -> Optional[URL]:
    if in_url is None:
        return in_url
    return URL(in_url)


@attr.s(auto_attribs=True, auto_detect=True, kw_only=True, frozen=True)
class MetaInfo(AbstractMetaItem):
    app_name: str = attr.ib(default=None)
    app_author: str = attr.ib(default=None)
    version: str = attr.ib(default=None)
    url: URL = attr.ib(converter=url_converter, default=None)
    pid: int = attr.ib(factory=os.getpid)
    os: OperatingSystem = attr.ib(factory=OperatingSystem.determine_operating_system)
    os_release: str = attr.ib(factory=platform.release)
    python_version: str = attr.ib(factory=platform.python_version)
    started_at: datetime = attr.ib(factory=utc_now)
    base_mem_use: int = attr.ib(default=memory_in_use())
    is_dev: bool = attr.ib(default=None, converter=attr.converters.default_if_none(False))
    is_gui: bool = attr.ib(default=None, converter=attr.converters.default_if_none(False))

    @classmethod
    @property
    def __default_configuration__(cls) -> dict[str, Any]:
        default_configuration = {}
        return default_configuration

    @property
    def pretty_base_mem_use(self) -> str:
        return bytes2human(self.base_mem_use)

    @property
    def pretty_started_at(self) -> str:
        return DatetimeFmt.STANDARD.strf(self.started_at)

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:

        if pretty is True:
            return make_pretty(self)
        return attr.asdict(self)

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    def clean_up(self, **kwargs) -> None:
        pass


    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
