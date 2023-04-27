"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import json
from typing import TYPE_CHECKING, Union, Literal, Callable, Optional
from types import ModuleType
from pathlib import Path
from threading import RLock

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import SpecDataMissingError
from gidapptools.custom_types import PATH_TYPE
from gidapptools.general_helper.timing import get_dummy_profile_decorator_in_globals
from gidapptools.general_helper.class_helper import MethodEnabledWeakSet
from gidapptools.gid_config.conversion.spec_item import SpecEntry, SpecSection
from gidapptools.general_helper.mixins.file_mixin import FileMixin
from gidapptools.gid_config.conversion.converter_grammar import ConverterSpecData, parse_specification
import orjson
# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    pass

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]
get_dummy_profile_decorator_in_globals()
THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class SpecLoader:
    __slots__ = ("spec_section_class",
                 "spec_entry_class",
                 "parse_func",
                 "loaded_data")

    def __init__(self,
                 spec_section_class: type[SpecSection] = SpecSection,
                 spec_entry_class: type[SpecEntry] = SpecEntry,
                 parse_function: Callable[[str], ConverterSpecData] = parse_specification) -> None:
        self.spec_section_class = spec_section_class
        self.spec_entry_class = spec_entry_class
        self.parse_func = parse_function
        self.loaded_data: dict[str, SpecSection] = None

    @property
    def is_loaded(self) -> bool:
        return self.loaded_data is not None

    def process_entry(self, entry_name: str, entry_data: dict[str, object]) -> SpecEntry:
        entry_data = dict(entry_data)
        if entry_data.get("converter", None) is not None:
            entry_data["converter"] = self.parse_func(entry_data["converter"])
        return self.spec_entry_class(name=entry_name, **entry_data)

    def process_section(self, section_name: str, section_data: dict[str, object]) -> SpecSection:
        section_data = {k: v for k, v in section_data.items() if k != "entries"}
        if section_data.get("default_converter", None) is not None:
            section_data["default_converter"] = self.parse_func(section_data["default_converter"])

        return self.spec_section_class(name=section_name, **section_data)

    def process_data(self, data: dict[str, object]) -> None:
        self.reset()
        sections_data = data["sections"]
        for section_name, section_data in sections_data.items():
            section = self.process_section(section_name=section_name, section_data=section_data)

            for entry_name, entry_data in section_data["entries"].items():
                section.add_entry(self.process_entry(entry_name=entry_name, entry_data=entry_data))
            self.loaded_data[section_name] = section

    def create_dynamic_entry(self, section: SpecSection, entry_name: str) -> SpecEntry:
        entry = self.spec_entry_class(name=entry_name)
        entry.set_section(section)
        return entry

    def reset(self) -> None:
        self.loaded_data = {}

    def __repr__(self) -> str:

        return f'{self.__class__.__name__}(spec_section_class={self.spec_section_class!r}, spec_entry_class={self.spec_entry_class!r})'


class SpecData:

    def __init__(self, name: str, loader: SpecLoader) -> None:
        self.name = name
        self.loader = loader
        self.load_lock: RLock = RLock()
        self._original_data: dict[str, object] = None

    @property
    def original_data(self) -> Optional[dict[str, object]]:
        with self.load_lock:
            return self._original_data

    @property
    def sections(self) -> dict[str, SpecSection]:
        with self.load_lock:
            return {k: v for k, v in self.loader.loaded_data.items()}

    @property
    def entries(self) -> dict[tuple[str, str], SpecEntry]:
        with self.load_lock:
            _out = {}
            for section in self.loader.loaded_data.values():
                for entry in section.entries.values():
                    _out[(section.name, entry.name)] = entry
        return _out

    def get_spec_entry(self, section_name: str, entry_name: str) -> SpecEntry:
        with self.load_lock:
            section = self.sections[section_name]
            try:
                return section[entry_name]
            except KeyError as e:
                if section.dynamic_entries_allowed is True and entry_name is not None:
                    return self.loader.create_dynamic_entry(section=section, entry_name=entry_name)
                else:
                    raise SpecDataMissingError(f"No entry with name {entry_name!r} in section {section_name!r} of {self!r}.") from e

    def load_data(self, data: dict) -> "SpecData":
        with self.load_lock:
            self._original_data = data
            self.loader.process_data(self.original_data)
        return self

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}(name={self.name!r}, loader={self.loader!r})'


class SpecFile(FileMixin, SpecData):
    _name_suffixes_to_remove: tuple[str] = ("_configspec", "_spec", "_config", "_config_spec", "_spec_config", "_specconfig")

    json_load_func: Callable[[str], dict[str, object]] = orjson.loads

    def __init__(self,
                 file_path: PATH_TYPE,
                 loader: SpecLoader = None,
                 changed_parameter: Union[Literal['size'], Literal['file_hash']] = 'size') -> None:
        super().__init__(name=self._generate_name_from_path(file_path, suffixes_to_remove=self._name_suffixes_to_remove),
                         loader=loader or SpecLoader(),
                         file_path=file_path,
                         changed_parameter=changed_parameter,
                         missing_ok=False)
        self._on_reload_targets: MethodEnabledWeakSet = MethodEnabledWeakSet()

    @property
    def original_data(self) -> dict:
        self.reload_if_changed()
        return self._original_data

    @property
    def sections(self) -> dict[str, SpecSection]:
        self.reload_if_changed()
        return super().sections

    @property
    def entries(self) -> dict[tuple[str, str], SpecEntry]:
        self.reload_if_changed()
        return super().entries

    def add_on_reload_target(self, target: Callable[[], None]) -> None:
        self._on_reload_targets.add(target)

    def reload_if_changed(self) -> None:
        if self._original_data is None or self.has_changed is True:
            self.reload()

    def reload(self) -> "SpecFile":
        self.load()
        for target in self._on_reload_targets:
            target()
        return self

    def load(self) -> "SpecFile":
        with self.lock:

            self.load_data(self.json_load_func(self.read()))

        return self

    def save(self) -> None:
        with self.lock:
            data = self.original_data
            json_data = json.dumps(data, indent=4, sort_keys=False)
            self.write(json_data)

    def __repr__(self) -> str:

        return f'{self.__class__.__name__}(name={self.name!r}, file_path={self.file_path.as_posix()!r})'


# region [Main_Exec]
if __name__ == '__main__':
    pass

# endregion [Main_Exec]
