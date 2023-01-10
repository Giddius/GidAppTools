"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
import pkgutil
import importlib
import os
import importlib.util
import importlib.metadata
from types import ModuleType
from pathlib import Path
from typing import Union, Iterable, Mapping


if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.helper import PackageMetadataDict

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def is_importable(package_name: str) -> bool:
    """
    Checks if the package is importable, without actually trying to import it.

    :param package_name: Name of the Package to check, is case-sensitive
    :type package_name: str
    :return: True if the package is importable in the current environment
    :rtype: bool
    """
    return importlib.util.find_spec(name=package_name) is not None


def meta_data_from_module(in_module: ModuleType) -> PackageMetadataDict:
    module_metadata = importlib.metadata.metadata(in_module.__package__)
    return PackageMetadataDict.from_meta_importlib_meta_data(module_metadata)


def import_from_name(name: str) -> ModuleType:
    module = importlib.import_module(name)
    return module


def import_from_file_path(file_path: Union[str, os.PathLike, Path]) -> ModuleType:
    file_path = Path(file_path).resolve()
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    _module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(_module)

    return _module


def all_importable_package_names(exclude_underscored: bool = True, exclude_std_lib: bool = False, exclude_main: bool = True) -> tuple[str]:

    def _check_exclude(in_name: str) -> bool:
        if exclude_underscored is True and in_name.startswith("_"):
            return False
        if exclude_std_lib is True and in_name in sys.stdlib_module_names:
            return False
        if exclude_main is True and in_name == "__main__":
            return False
        return True

    return tuple(sorted([i.name for i in pkgutil.iter_modules() if _check_exclude(i.name)], key=lambda x: x.casefold()))

# region [Main_Exec]


if __name__ == '__main__':
    pass
# endregion [Main_Exec]
