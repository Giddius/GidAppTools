"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
from typing import TYPE_CHECKING, Union, TypeVar
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
from frozendict import frozendict
from gidapptools.gid_logger.logger import get_logger

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.gid_database.orm_peewee.sqlite.apsw_database import GidAPSWDatabase

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
log = get_logger(__name__)

# endregion [Constants]

x = {'analysis_limit': 100000,
     'application_id': 0,
     'auto_vacuum': 2,
     'automatic_index': 1,
     'busy_timeout': 0,
     'cache_size': -128000,
     'cache_spill': 30971,
     'cell_size_check': 0,
     'checkpoint_fullfsync': 0,
     'collation_list': 0,
     'data_version': 2,
     'database_list': 0,
     'defer_foreign_keys': 0,
     'encoding': 'UTF-8',
     'foreign_keys': 1,
     'freelist_count': 0,
     'fullfsync': 0,
     'hard_heap_limit': 0,
     'ignore_check_constraints': 0,
     'journal_mode': 'wal',
     'journal_size_limit': 1073741824,
     'legacy_alter_table': 0,
     'locking_mode': 'normal',
     'max_page_count': 1073741823,
     'mmap_size': 0,
     'page_count': 39215,
     'page_size': 4096,
     'query_only': 0,
     'read_uncommitted': 0,
     'recursive_triggers': 0,
     'reverse_unordered_selects': 0,
     'secure_delete': 0,
     'soft_heap_limit': 0,
     'synchronous': 0,
     'temp_store': 0,
     'threads': 8,
     'trusted_schema': 1,
     'user_version': 5,
     'wal_autocheckpoint': 0}


_ONLY_EXECUTABLE_PRAGMA_NAMES: tuple[str] = ("foreign_key_check",
                                             "optimize",
                                             "integrity_check",
                                             "quick_check",
                                             "wal_checkpoint",
                                             "incremental_vacuum",
                                             "shrink_memory")

_DEPRECATED_PRAGMA_NAMES: tuple[str] = ("count_changes",
                                        "data_store_directory",
                                        "default_cache_size",
                                        "empty_result_callbacks",
                                        "full_column_names",
                                        "short_column_names",
                                        "temp_store_directory",
                                        "pragma_list")

_TESTING_ONLY_PRAGMA_NAMES: tuple[str] = ("stats",
                                          "writable_schema")

_NON_QUERYABLE_PRAGMA_NAMES: tuple[str] = ("schema_version",
                                           "case_sensitive_like",
                                           "foreign_key_list",
                                           "index_info",
                                           "index_list",
                                           "index_xinfo",
                                           "table_info",
                                           "table_xinfo")

_MULTIPLE_VALUE_PRAGMAS: tuple[str] = ("table_list", "function_list", "module_list", "compile_options", "database_list")

_GET_DEFAULT_TYPE = TypeVar("_GET_DEFAULT_TYPE")


class PragmaInfo:
    _pragma_names_to_exclude: set[str] = set(_ONLY_EXECUTABLE_PRAGMA_NAMES + _DEPRECATED_PRAGMA_NAMES + _TESTING_ONLY_PRAGMA_NAMES + _NON_QUERYABLE_PRAGMA_NAMES + _MULTIPLE_VALUE_PRAGMAS)

    def __init__(self, database: "GidAPSWDatabase") -> None:
        self.database = database
        self._all_pragma_names: tuple[str] = None
        self._pragma_data: frozendict[str, Union[str, int]] = None
        self._compile_options: frozendict[str, object] = None
        self._module_list: tuple[str] = None

    @property
    def all_pragma_names(self) -> tuple[str]:
        if self._all_pragma_names is None:
            self._all_pragma_names = self._get_all_pragma_names()
        return self._all_pragma_names

    @property
    def pragma_data(self) -> frozendict[str, Union[str, int]]:
        if self._pragma_data is None:
            self._pragma_data = self._get_pragma_data()
        return self._pragma_data

    @property
    def compile_options(self) -> frozendict[str, object]:
        if self._compile_options is None:
            self._compile_options = self._get_compile_options()
        return self._compile_options

    @property
    def module_list(self) -> tuple[str]:
        if self._module_list is None:
            self._module_list = self._get_module_list()
        return self._module_list

    def _get_all_pragma_names(self) -> tuple[str]:
        return tuple(i[0] for i in self.database.connection().execute("PRAGMA pragma_list"))

    def _get_pragma_data(self) -> frozendict[str, Union[str, int]]:
        _out = {}
        pragma_names_to_query = (name for name in self.all_pragma_names if name not in self._pragma_names_to_exclude)

        for pragma_name in pragma_names_to_query:
            try:
                _out[pragma_name] = self.database.connection().execute(f"PRAGMA {pragma_name}").fetchone()[0]
            except TypeError:
                _out[pragma_name] = None
        return frozendict(_out)

    def _get_compile_options(self) -> frozendict[str, object]:
        _out = {}
        for option_entry in [i[0] for i in self.database.connection().execute("PRAGMA compile_options")]:

            if "=" in option_entry:
                name, value = (i.strip() for i in option_entry.split("=", 1))
            else:
                name = option_entry.strip()
                value = "NO_VALUE"

            _out[name] = value
        return frozendict(_out)

    def _get_module_list(self) -> tuple[str]:
        return tuple(i[0].strip() for i in self.database.connection().execute("PRAGMA module_list"))

    def fill_with_data(self) -> Self:
        self._all_pragma_names = self._get_all_pragma_names()
        self._pragma_data = self._get_pragma_data()
        self._compile_options = self._get_compile_options()
        self._module_list = self._get_module_list()
        log.info("finished filling %r with data", self)
        return self

    def reset(self) -> Self:
        self._all_pragma_names = None
        self._pragma_data = None
        self._compile_options = None
        self._module_list = None
        log.info("reset %r", self)
        return self

    def __getitem__(self, key: str) -> Union[str, int]:
        return self.pragma_data[key]

    def get(self, key: str, default: _GET_DEFAULT_TYPE = None) -> Union[_GET_DEFAULT_TYPE, int, str]:
        try:
            self[key]
        except KeyError:
            return default

    def on_pragma_set(self, pragma_name: str, value: Union[str, int, None]) -> None:
        if pragma_name in self.pragma_data:
            self._pragma_data[pragma_name] = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(database={self.database!r})'


# region [Main_Exec]
if __name__ == '__main__':
    pass
# endregion [Main_Exec]
