"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
import pkgutil
import importlib
import importlib.util
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def is_importable(package_name: str) -> bool:
    """
    Checks if the package is importable, without actually trying to import it.

    :param package_name: Name of the Package to check, is case-sensitive
    :type package_name: str
    :return: True if the package is importable in the current environment
    :rtype: bool
    """
    return importlib.util.find_spec(name=package_name) is not None


def all_importable_package_names(exclude_underscored: bool = True, exclude_std_lib: bool = False) -> tuple[str]:

    def _check_exclude(in_name: str) -> bool:
        if exclude_underscored is True and in_name.startswith("_"):
            return False
        if exclude_std_lib is True and in_name in sys.stdlib_module_names:
            return False
        return True

    return tuple(sorted([i for i in pkgutil.iter_modules() if _check_exclude(i.name)], key=lambda x: x.name.casefold()))

# region[Main_Exec]


if __name__ == '__main__':
    print(all_importable_package_names(exclude_std_lib=True, exclude_underscored=True))


# endregion[Main_Exec]
