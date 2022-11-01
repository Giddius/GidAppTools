"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import sys
from typing import TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Generator, Union, Optional, Protocol, runtime_checkable, NoReturn, NewType, Literal

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from statistics import mean
from collections.abc import Mapping, Iterable, Callable
from pathlib import Path
from datetime import datetime
from enum import Enum, unique, auto
from time import sleep, perf_counter
from concurrent.futures import ThreadPoolExecutor
# * Third Party Imports --------------------------------------------------------------------------------->
from frozendict import frozendict
from functools import partial
import peewee
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.reflection import introspect
from playhouse.apsw_ext import APSWDatabase
from gidapptools.gid_database.orm_peewee.sqlite.constants import STD_DEFAULT_EXTENSIONS, STD_DEFAULT_PRAGMAS, MEMORY_DB_PATH
from gidapptools.general_helper.conversion import ns_to_s, number_to_pretty
from gidapptools.gid_database.orm_peewee.sqlite.pragma_info import PragmaInfo
import apsw
from threading import RLock
import inspect
from pprint import pprint
import pp
# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.custom_types import PATH_TYPE

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

# region [Types]

WAL_HOOK_TYPE: TypeAlias = Optional[Callable[["GidAPSWDatabase", apsw.Connection, str, int], int]]

PROFILE_HOOK_TYPE: TypeAlias = Optional[Callable[["GidAPSWDatabase", str, int], None]]

UPDATE_HOOK_TYPE: TypeAlias = Optional[Callable[["GidAPSWDatabase", int, str, str, int], None]]

ROLLBACK_HOOK_TYPE: TypeAlias = Optional[Callable[["GidAPSWDatabase"], None]]

COMMIT_HOOK_TYPE: TypeAlias = Optional[Callable[["GidAPSWDatabase"], None]]

ALL_HOOK_TYPES: TypeAlias = Union[WAL_HOOK_TYPE, PROFILE_HOOK_TYPE, UPDATE_HOOK_TYPE, ROLLBACK_HOOK_TYPE, COMMIT_HOOK_TYPE]

# endregion [Types]


def _ensure_string_db_path(in_db_path: Union["PATH_TYPE", Literal[":memory:"]]) -> str:
    """
    Returns the provided path resolved and as a String so APSW can understand it.

    Peewee ( or APSW) seems to not follow the `os.PathLike`- Protocol.

    :param in_db_path: _description_
    :type in_db_path: Union["PATH_TYPE", Literal[":memory:"]]
    :return: _description_
    :rtype: str
    """
    if in_db_path == MEMORY_DB_PATH:
        return MEMORY_DB_PATH
    db_path = Path(in_db_path).resolve()
    return os.fspath(db_path)


def data_setup_noop(db: "GidAPSWDatabase") -> None:
    ...


def migration_noop(db: "GidAPSWDatabase") -> None:
    ...


class DatabaseSetupStatus(Enum):
    NOT_SETUP = auto()
    SETUP_RUNNING = auto()
    OPERATIONAL = auto()
    SHUTDOWN = auto()


@unique
class APSWHooks(Enum):
    WAL_HOOK = ("_wal_hook", "setwalhook")
    PROFILE_HOOK = ("_profile_hook", "setprofile")
    UPDATE_HOOK = ("_update_hook", "setupdatehook")
    ROLLBACK_HOOK = ("_rollback_hook", "setrollbackhook")
    COMMIT_HOOK = ("_commit_hook", "setcommithook")

    @property
    def attribute_name(self) -> str:
        return self.value[0]

    @property
    def setter_name(self) -> str:
        return self.value[1]

    @classmethod
    def _missing_(cls, value: object) -> "APSWHooks":
        if isinstance(value, str):
            for name, item in cls.__members__.items():

                if name == value.upper() or value.casefold() in item.value or value.casefold() in [i.removeprefix("_") for i in item.value]:
                    return item

        return super()._missing_(value)


WRAP_WITH_DB_TYPEVAR = TypeVar("WRAP_WITH_DB_TYPEVAR", WAL_HOOK_TYPE, PROFILE_HOOK_TYPE, UPDATE_HOOK_TYPE, ROLLBACK_HOOK_TYPE, COMMIT_HOOK_TYPE, None)


class APSWHookManager:
    __slots__ = ("database", "_wal_hook", "_profile_hook", "_update_hook", "_rollback_hook", "_commit_hook")

    def __init__(self,
                 database: "GidAPSWDatabase",
                 wal_hook: WAL_HOOK_TYPE = None,
                 profile_hook: PROFILE_HOOK_TYPE = None,
                 update_hook: UPDATE_HOOK_TYPE = None,
                 rollback_hook: ROLLBACK_HOOK_TYPE = None,
                 commit_hook: COMMIT_HOOK_TYPE = None) -> None:
        self.database = database
        self._wal_hook = wal_hook
        self._profile_hook = profile_hook
        self._update_hook = update_hook
        self._rollback_hook = rollback_hook
        self._commit_hook = commit_hook

    def _wrap_with_db(self, orig_func: WRAP_WITH_DB_TYPEVAR) -> WRAP_WITH_DB_TYPEVAR:
        if orig_func is not None:
            return partial(orig_func, self.database)

        return orig_func

    def apply(self, connection: apsw.Connection) -> None:
        for hook_info in APSWHooks.__members__.values():
            getattr(connection, hook_info.setter_name)(self._wrap_with_db(getattr(self, hook_info.attribute_name, None)))

    def set(self, typus: Union[str, APSWHooks], value: WRAP_WITH_DB_TYPEVAR) -> WRAP_WITH_DB_TYPEVAR:
        typus = APSWHooks(typus)
        setattr(self, typus.attribute_name, value)
        if not self.database.is_closed():
            getattr(self.database.connection(), typus.setter_name)(self._wrap_with_db(getattr(self, typus.attribute_name, None)))
        return value

    def set_wal_hook(self, value: WAL_HOOK_TYPE) -> WAL_HOOK_TYPE:
        self.set(typus=APSWHooks.WAL_HOOK, value=value)
        return value

    def set_profile_hook(self, value: PROFILE_HOOK_TYPE) -> PROFILE_HOOK_TYPE:
        self.set(typus=APSWHooks.PROFILE_HOOK, value=value)
        return value

    def set_update_hook(self, value: UPDATE_HOOK_TYPE) -> UPDATE_HOOK_TYPE:
        self.set(typus=APSWHooks.UPDATE_HOOK, value=value)
        return value

    def set_rollback_hook(self, value: ROLLBACK_HOOK_TYPE) -> ROLLBACK_HOOK_TYPE:
        self.set(typus=APSWHooks.ROLLBACK_HOOK, value=value)
        return value

    def set_commit_hook(self, value: COMMIT_HOOK_TYPE) -> COMMIT_HOOK_TYPE:
        self.set(typus=APSWHooks.COMMIT_HOOK, value=value)
        return value


class GidAPSWDatabase(APSWDatabase):
    setup_lock = RLock()
    default_pragmas: Mapping[str, object] = frozendict(**STD_DEFAULT_PRAGMAS)
    default_extensions: Mapping[str, bool] = frozendict(**STD_DEFAULT_EXTENSIONS)

    def __init__(self,
                 database_path: Union["PATH_TYPE", Literal[":memory:"]],
                 backup_folder: "PATH_TYPE" = None,
                 thread_safe: bool = True,
                 autoconnect: bool = True,
                 autorollback: bool = None,
                 timeout: Union[Callable[[int], bool], float, None] = 100,
                 pragmas: Mapping = None,
                 extensions: Mapping = None,
                 hooks: dict[str, ALL_HOOK_TYPES] = None):
        self.setup_status: DatabaseSetupStatus = DatabaseSetupStatus.NOT_SETUP
        self._backup_folder = Path(backup_folder).resolve() if backup_folder is not None else None
        self.hook_manager: APSWHookManager = APSWHookManager(self, **(hooks or {}))
        self.pragma_info: PragmaInfo = None
        super().__init__(database=_ensure_string_db_path(database_path),
                         autoconnect=autoconnect,
                         autorollback=autorollback,
                         thread_safe=thread_safe,
                         timeout=timeout,
                         pragmas=dict(self.default_pragmas | (pragmas or {})),
                         **dict(self.default_extensions | (extensions or {})))

    def init(self, database, pragmas=None, timeout=5, returning_clause=None, **kwargs):
        pp(kwargs)
        super().init(database, pragmas, timeout, returning_clause, **kwargs)
        self.timeout = timeout

    @property
    def db_file_name(self) -> str:
        if self.database == MEMORY_DB_PATH:
            return MEMORY_DB_PATH
        return self.db_path.name

    @property
    def db_path(self) -> Optional[Path]:
        if self.database == MEMORY_DB_PATH:
            return None
        return Path(self.database)

    @property
    def backup_folder(self) -> Optional[Path]:
        if self._backup_folder is None:
            return None

        return self._backup_folder

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value: Union[float, Callable[[int], bool], None]):
        if value is None:
            if self._timeout is value:
                return
            self._timeout = value

        elif callable(value):
            if self._timeout is value:
                return
            self._timeout = value
            if not self.is_closed():
                self.connection().setbusyhandler(self._timeout)

        else:
            if self._timeout == (value * 1000):
                return
            self._timeout = value * 1000

            if not self.is_closed():
                self.connection().setbusytimeout(self._timeout)

    def _connect(self):

        conn = apsw.Connection(self.database, **self.connect_params)
        if callable(self._timeout):
            conn.setbusyhandler(self._timeout)
        elif self._timeout is not None:
            conn.setbusytimeout(self._timeout * 1000)
        try:
            self._add_conn_hooks(conn)
        except:
            conn.close()
            raise
        return conn

    def _add_conn_hooks(self, conn: apsw.Connection):
        super()._add_conn_hooks(conn)
        self.hook_manager.apply(conn)
        wal_autocheckpoint = next((i[1] for i in self._pragmas if i[0] == "wal_autocheckpoint"), None)
        if wal_autocheckpoint is not None:
            conn.wal_autocheckpoint(wal_autocheckpoint)

    def vacuum(self, incremental: bool = True) -> bool:
        if self.is_closed() is True:
            return False

        try:
            conn: apsw.Connection = self.connection()
            if incremental is True:
                conn.execute("PRAGMA incremental_vacuum").fetchall()
                return True

            else:
                conn.execute("VACUUM").fetchall()
                return True
        except apsw.Error as e:
            return False

    def optimize(self, analysis_limit: int = 1000) -> bool:
        if self.is_closed() is True:
            return False

        try:
            conn: apsw.Connection = self.connection()
            conn.execute(f"PRAGMA analysis_limit={analysis_limit};PRAGMA optimize").fetchall()
            return True
        except apsw.Error as e:
            return False

    def _close(self, conn: apsw.Connection) -> None:
        if self.is_closed() is False:
            conn.execute("PRAGMA analysis_limit=0;PRAGMA optimize").fetchall()

        conn.close()

    def _setup_db_path(self, overwrite: bool = False) -> None:
        if self.db_path is not None:
            self.db_path.parent.mkdir(exist_ok=True, parents=True)
            if overwrite is True:
                self.db_path.unlink(missing_ok=True)

    def _set_page_size(self):
        print("setting page size")
        wal_mode = False
        conn: apsw.Connection = self.connection()
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        if journal_mode.casefold() == "wal":
            wal_mode = True
        page_size = next((i[1] for i in self._pragmas if i[0] == "page_size"), None)

        if page_size is None:
            return

        conn.execute(f"PRAGMA page_size={page_size};").fetchall()

        if wal_mode is True:
            conn.execute("PRAGMA journal_mode=OFF;").fetchall()

        conn.execute("VACUUM;").fetchall()

        if wal_mode is True:
            conn.execute("PRAGMA journal_mode=WAL;").fetchall()

    def setup(self,
              db_proxy: peewee.DatabaseProxy = None,
              data_setup: Callable[["GidAPSWDatabase"], None] = data_setup_noop,
              migration: Callable[["GidAPSWDatabase"], None] = migration_noop,
              overwrite: bool = False) -> Self:
        with self.setup_lock:
            if self.setup_status is not DatabaseSetupStatus.NOT_SETUP:
                return self

            self.setup_status = DatabaseSetupStatus.SETUP_RUNNING
            self._pre_setup()
            self._setup_db_path(overwrite=overwrite)
            db_exists = self.db_path is not None and self.db_path.exists()
            self.connect()
            if db_exists is False:
                self._set_page_size()
            if db_proxy:
                db_proxy.initialize(self)

            data_setup(self)

            migration(self)

            self._post_setup()
            self.setup_status = DatabaseSetupStatus.OPERATIONAL
            return self

    def _pre_setup(self) -> None:
        ...

    def _post_setup(self) -> None:
        self.pragma_info = PragmaInfo(self).fill_with_data()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(database_name={self.db_file_name!r}, setup_status={self.setup_status.name!r})"


# region[Main_Exec]
if __name__ == '__main__':

    def run_setup(db):
        script_path = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_database\sqlite\data\simple_db_setup.sql")
        script = script_path.read_text(encoding='utf-8', errors='ignore')
        db.execute(peewee.SQL(script))
    x = GidAPSWDatabase(MEMORY_DB_PATH)
    x.setup(data_setup=run_setup)
    with x:
        print(x.execute(peewee.SQL('SELECT "Person"."name", "Country"."name" FROM "Person"  INNER JOIN "Country"  ON "Country"."id"=="Person"."country"')).fetchall())
    pp(x.pragma_info.pragma_data)


# endregion[Main_Exec]
