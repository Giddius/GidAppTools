"""
WiP.

Soon.
"""

# region [Imports]

from enum import Enum
from pathlib import Path
from typing import Any, Literal, Mapping, Union
from hashlib import blake2b
from gidapptools.gid_config.parser.ini_parser import BaseIniParser
from threading import Lock
from pathlib import Path
from typing import Any, TYPE_CHECKING, Union, Optional
from gidapptools.errors import AdvancedDictError, DispatchError, SectionMissingError, EntryMissingError
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.enums import SpecialTypus
from gidapptools.gid_config.parser.tokens import Section, Entry
from gidapptools.errors import ConversionError, UnconvertableTypusError
from gidapptools.general_helper.mixins.file_mixin import FileMixin
if TYPE_CHECKING:
    from gidapptools.gid_config.conversion.conversion_table import ConversionTable
    from gidapptools.gid_config.conversion.spec_data import SpecData
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ConfigData:

    def __init__(self) -> None:
        self._sections: dict[str, Section] = None

    @property
    def sections(self) -> dict[str, Section]:
        if self._sections is None:
            self._sections = {}
        return self._sections

    @property
    def all_sections(self) -> tuple[Section]:
        return tuple(self.sections.values())

    @property
    def all_section_names(self) -> tuple[str]:
        return tuple(self.sections)

    def get_section(self, section_name: str, create_missing_section: bool = False) -> Section:
        try:
            return self.sections[section_name]
        except KeyError as error:
            if create_missing_section is False:
                raise SectionMissingError(section_name=section_name, config_data=self) from error
            section = Section(section_name)
            self.add_section(section=section)
            return section

    def add_section(self, section) -> None:
        self._sections[section.name] = section

    def remove_section(self, section_name: str, missing_ok: bool = False) -> None:
        try:
            del self._sections[section_name]
        except KeyError as error:
            if missing_ok is False:
                raise SectionMissingError(section_name=section_name, config_data=self) from error

    def clear_all_sections(self) -> None:
        self._sections = None

    def get_entry(self, section_name: str, entry_key: str) -> Entry:
        section = self.get_section(section_name=section_name)
        try:
            return section[entry_key]
        except KeyError as error:
            raise EntryMissingError(section_name=section_name, entry_key=entry_key, config_data=self) from error

    def add_entry(self, section_name: str, entry: Entry, create_missing_section: bool = False) -> None:
        section = self.get_section(section_name=section_name, create_missing_section=create_missing_section)
        section.add_entry(entry=entry)

    def remove_entry(self, section_name: str, entry_key: str, missing_ok: bool = False) -> None:
        try:
            section = self.get_section(section_name=section_name)
        except SectionMissingError:
            if missing_ok is False:
                raise
            return

        try:
            del section[entry_key]
        except KeyError as error:
            if missing_ok is False:
                raise EntryMissingError(section_name=section_name, entry_key=entry_key, config_data=self) from error
            return

    def clear_entries(self, section_name: str, missing_ok: bool = False):
        try:
            section = self.get_section(section_name=section_name)
        except SectionMissingError:
            if missing_ok is False:
                raise
            return
        section.entries = {}

    def reload(self) -> None:
        pass

    def as_dict(self) -> dict[str, dict[str, Any]]:
        _out = {}
        for section in self.sections.values():
            _out |= section.as_dict()
        return _out


class ConfigFile(FileMixin, ConfigData):

    def __init__(self,
                 file_path: Path,
                 parser: BaseIniParser = None,
                 changed_parameter: Union[Literal['size'], Literal['file_hash']] = 'size') -> None:

        self.parser: BaseIniParser = BaseIniParser() if parser is None else parser
        super().__init__(file_path=file_path, changed_parameter=changed_parameter)

    @property
    def sections(self) -> dict[str, Section]:
        if self._sections is None or self.has_changed is True:
            self.reload()
        return self._sections

    def reload(self) -> None:
        content = self.read()
        self._sections = {section.name: section for section in self.parser.parse(content)}
        self.changed_signal.emit(self)
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
