"""
WiP.

Soon.
"""

# region [Imports]


from pathlib import Path
from typing import Any, Callable
from itertools import product, combinations
import attr
import requests
from yarl import URL
from tzlocal import get_localzone
from gidapptools.utility.enums import OperatingSystem, NamedMetaPath
from gidapptools.utility.helper import memory_in_use, handle_path, utc_now, PathLibAppDirs, mark_appdir_path, make_pretty
from gidapptools.general_helper.date_time import DatetimeFmt
from gidapptools.types import PATH_TYPE
from appdirs import AppDirs, user_data_dir, user_config_dir, user_cache_dir, user_log_dir
import orjson
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem
from gidapptools.meta_data.meta_print.console_implementations import GidRichConsole
# REMOVE_BEFORE_BUILDING_DIST
from gidapptools.utility._debug_tools import dprint

print = dprint

# end REMOVE_BEFORE_BUILDING_DIST

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MetaPrint(AbstractMetaItem, GidRichConsole):

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:
        return super().as_dict(pretty=pretty)

    def to_storager(self, storager: Callable = None) -> None:
        pass

    def clean_up(self, **kwargs) -> None:
        pass


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
