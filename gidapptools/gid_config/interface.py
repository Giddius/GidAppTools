"""
WiP.

Soon.
"""

# region [Imports]
import os
from pprint import pprint
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Union, Iterable, Callable, Hashable, TYPE_CHECKING
from collections import UserDict
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.timing import time_execution, time_func
from gidapptools.general_helper.dict_helper import get_by_keypath, set_by_key_path
from warnings import warn
from gidapptools.general_helper.dict_helper import AdvancedDict, multiple_dict_get, multiple_dict_pop
from gidapptools.gid_config.enums import SpecialTypus
from gidapptools.gid_config.parser.config_data import ConfigData, ConfigFile
from gidapptools.gid_config.conversion.spec_data import SpecData, SpecFile
from gidapptools.errors import EntryMissingError, SectionMissingError
from gidapptools.gid_config.conversion.entry_typus_item import EntryTypus
from gidapptools.gid_config.conversion.conversion_table import ConfigValueConversionTable
from gidapptools.gid_config.parser.ini_parser import BaseIniParser
from gidapptools.gid_config.parser.tokens import Entry
from gidapptools.general_helper.timing import time_func
from gidapptools.errors import MissingTypusOrSpecError
if TYPE_CHECKING:
    from gidapptools.gid_config.parser.grammar import BaseIniGrammar, TokenFactory
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidIniConfig:

    def __init__(self,
                 config_file: Path,
                 spec_file: Path = None,
                 empty_is_missing: bool = True,
                 parser: BaseIniParser = None) -> None:

        self.config = ConfigFile(file_path=config_file, parser=parser)
        self.spec = None if spec_file is None else SpecFile(file_path=spec_file)
        self.converter = ConfigValueConversionTable()
        self.empty_is_missing = empty_is_missing

    def reload(self) -> None:
        self.config.reload()
        self.spec.reload()

    def get(self, section_name, entry_key: str, typus: Union[type, EntryTypus] = SpecialTypus.AUTO, default: Any = MiscEnum.NOTHING) -> Any:
        try:
            entry = self.config.get_entry(section_name=section_name, entry_key=entry_key)

        except (EntryMissingError, SectionMissingError):
            if default is MiscEnum.NOTHING:
                raise
            return default

        if not entry.value:
            if self.empty_is_missing is True and default is not MiscEnum.NOTHING:
                return default
            return None

        if typus is SpecialTypus.AUTO:
            if self.spec is None:
                raise MissingTypusOrSpecError("You have to provide a typus if no spec file has been set in the __init__.")
            typus = self.spec.get_entry_typus(section_name=section_name, entry_key=entry_key)
        return self.converter(entry=entry, typus=typus)


# region[Main_Exec]
if __name__ == '__main__':
    xample_config_file = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\parser_tests\simple_example_config.ini")
    xample_spec_file = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\parser_tests\simple_example_config_spec.json")
    x = GidIniConfig(config_file=xample_config_file, spec_file=xample_spec_file)
    print(x.get('jih', 'guild_id', default=None))
    print(x.get("this", "something"))
    print(x.get('general_settings', 'owner_ids', default=None))
# endregion[Main_Exec]
