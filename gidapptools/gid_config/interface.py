"""
WiP.

Soon.
"""

# region [Imports]
import os
from pprint import pprint
from collections.abc import Mapping
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any, Union, Iterable, Callable, Hashable, TYPE_CHECKING, Literal, Optional
from collections import UserDict
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.timing import time_execution, time_func
from gidapptools.general_helper.dict_helper import get_by_keypath, set_by_key_path
from warnings import warn
from gidapptools.general_helper.dict_helper import AdvancedDict, multiple_dict_get, multiple_dict_pop
from gidapptools.gid_config.enums import SpecialTypus
from gidapptools.gid_config.parser.config_data import ConfigData, ConfigFile
from gidapptools.gid_config.conversion.spec_data import SpecData, SpecFile, SpecVisitor
from gidapptools.errors import EntryMissingError, SectionMissingError
from gidapptools.gid_config.conversion.entry_typus_item import EntryTypus
from gidapptools.gid_config.conversion.conversion_table import ConfigValueConversionTable, ValueEncoder
from gidapptools.gid_config.parser.ini_parser import BaseIniParser
from gidapptools.gid_config.parser.tokens import Entry, Section
from gidapptools.general_helper.timing import time_func
from gidapptools.errors import MissingTypusOrSpecError, SectionExistsError

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
    default_spec_visitor: SpecVisitor = SpecVisitor()
    default_parser: BaseIniParser = BaseIniParser()
    default_converter: ConfigValueConversionTable = ConfigValueConversionTable()

    def __init__(self,
                 config_file: Path,
                 config_file_auto_write: bool = True,
                 spec_file: Optional[SpecFile] = None,
                 converter: ConfigValueConversionTable = None,
                 empty_is_missing: bool = True,
                 spec_visitor: SpecVisitor = None,
                 parser: BaseIniParser = None,
                 file_changed_parameter: str = 'size') -> None:

        self.parser = self.default_parser if parser is None else parser
        self.spec_visitor = self.default_spec_visitor if spec_visitor is None else spec_visitor
        self.config = ConfigFile(file_path=config_file, parser=self.parser, changed_parameter=file_changed_parameter, auto_write=config_file_auto_write)
        self.spec = SpecFile(file_path=spec_file, visitor=self.spec_visitor, changed_parameter=file_changed_parameter) if spec_file is not None else None
        self.converter = self.default_converter if converter is None else converter
        self.empty_is_missing = empty_is_missing

    def reload(self) -> None:
        self.config.reload()
        self.spec.reload()

    def get_section(self, section_name: str) -> dict[str, Any]:
        section = self.config.get_section(section_name=section_name)
        return {entry.key: self.get(section_name=section_name, entry_key=entry.key) for entry in section.entries.values()}

    def get(self,
            section_name: str,
            entry_key: str,
            typus: Union[type, EntryTypus] = SpecialTypus.AUTO,
            fallback_entry: Iterable[str] = None,
            default: Any = MiscEnum.NOTHING) -> Any:
        try:
            entry = self.config.get_entry(section_name=section_name, entry_key=entry_key)

        except (EntryMissingError, SectionMissingError):
            if fallback_entry is not None:
                return self.get(fallback_entry[0], fallback_entry[1], default=default)
            if default is not MiscEnum.NOTHING:
                return default
            raise

        if not entry.value:
            if self.empty_is_missing is True:
                if fallback_entry is not None:
                    return self.get(fallback_entry[0], fallback_entry[1], default=default)
                if default is not MiscEnum.NOTHING:
                    return default
            return None

        if typus is SpecialTypus.AUTO:
            if self.spec is None:
                raise MissingTypusOrSpecError("You have to provide a typus if no spec file has been set in the __init__.")
            typus = self.spec.get_entry_typus(section_name=section_name, entry_key=entry_key)

        return self.converter(entry=entry, typus=typus)

    def set(self, section_name: str, entry_key: str, entry_value: Any, create_missing_section: bool = False, spec_typus: str = None) -> None:
        self.config.set_value(section_name=section_name, entry_key=entry_key, entry_value=self.converter.encode(entry_value), create_missing_section=create_missing_section)
        if spec_typus is not None:
            self.spec.set_typus_value(section_name=section_name, entry_key=entry_key, typus_value=spec_typus)

    def clear_section(self, section_name: str, missing_ok: bool = True) -> None:
        self.config.clear_entries(section_name=section_name, missing_ok=missing_ok)

    def remove_section(self, section_name: str, missing_ok: bool = True) -> None:
        self.config.remove_section(section_name=section_name, missing_ok=missing_ok)

    def add_section(self, section_name: str, existing_ok: bool = True) -> None:

        self.config.add_section(section=Section(section_name), existing_ok=existing_ok)

    def add_spec_value_handler(self, target_name: str, handler: Callable[[Any, list[Any]], EntryTypus]) -> None:
        self.spec_visitor.add_handler(target_name=target_name, handler=handler)

    def add_converter_function(self, typus: Any, converter_function: Callable) -> None:
        self.converter[typus] = converter_function

    def as_dict(self, raw: bool = False) -> dict[str, dict[str, Any]]:
        raw_dict = self.config.as_raw_dict()
        if raw is True:
            return raw_dict
        _out = {}
        for section_name, values in raw_dict.items():
            _out[section_name] = {}
            for entry_name in values:
                _out[section_name][entry_name] = self.get(section_name, entry_name)

        return _out


# region[Main_Exec]
if __name__ == '__main__':
    pass
    # x = GidIniConfig(config_file=Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\example_config_1.ini"),
    #                  spec_file=Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\example_spec_1.json"))
    # x.reload()
# endregion[Main_Exec]