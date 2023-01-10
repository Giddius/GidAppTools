"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.conversion import ns_to_s, number_to_pretty

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    ...

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def print_profile_hook(db, stmt: str, time_taken: int):

    time_taken = ns_to_s(time_taken)
    time_taken = number_to_pretty(time_taken) + " s"
    print(f"Executed {stmt!r} in {time_taken}", flush=True)
# region [Main_Exec]


if __name__ == '__main__':
    pass

# endregion [Main_Exec]
