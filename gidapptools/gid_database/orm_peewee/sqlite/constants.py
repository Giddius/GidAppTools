"""
WiP.

Soon.
"""

# region [Imports]

from pathlib import Path
import os
from frozendict import frozendict
from gidapptools.general_helper.conversion import human2bytes, bytes2human

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

STD_DEFAULT_PRAGMAS = frozendict({
    "wal_autocheckpoint": 1_000,
    "auto_vacuum": 2,
    "cache_size": -1 * 256_000,  # 128mb
    "journal_mode": 'WAL',
    "synchronous": 0,
    "ignore_check_constraints": 0,
    "foreign_keys": 1,
    "journal_size_limit": 786432000,  # 750mb
    "page_size": 8192,
    "analysis_limit": 100_000,
    "case_sensitive_like": False,
    "threads": 8,
    # "temp_store": "MEMORY",
    # "mmap_size": 30_000_000_000,
})

STD_DEFAULT_EXTENSIONS = frozendict({"c_extensions": True,
                                     "rank_functions": False,
                                     "hash_functions": True,
                                     "json_contains": True,
                                     "bloomfilter": False,
                                     "regexp_function": True})


MEMORY_DB_PATH = ":memory:"

# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
