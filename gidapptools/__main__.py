"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.cli_info import cli_show_info  # noqa: F401

from gidapptools.general_helper import bytes2human_cli, human2bytes_cli  # noqa: F401

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


# region [Main_Exec]


if __name__ == '__main__':

    cli_show_info()


# endregion [Main_Exec]
