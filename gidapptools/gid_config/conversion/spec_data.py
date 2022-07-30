"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import json
import os
from typing import Any, Union, Literal, Callable, Hashable, Optional, TYPE_CHECKING
from pathlib import Path
from datetime import datetime, timedelta
from threading import RLock
from collections import defaultdict
from inspect import isfunction, ismethod
# * Third Party Imports --------------------------------------------------------------------------------->
from yarl import URL

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.custom_types import PATH_TYPE

from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.dict_helper import BaseVisitor, AdvancedDict, KeyPathError, set_by_key_path
from gidapptools.general_helper.string_helper import split_quotes_aware
from gidapptools.general_helper.mixins.file_mixin import FileMixin
from gidapptools.gid_config.conversion.conversion_table import EntryTypus
from gidapptools.gid_config.conversion.extra_base_typus import NonTypeBaseTypus
from gidapptools.gid_config.conversion.converter_grammar import parse_specification, ConverterSpecification, ConverterSpecData
from gidapptools.gid_config.conversion.spec_item import SpecItem
if TYPE_CHECKING:
    from gidapptools.meta_data.meta_info.meta_info_item import MetaInfo
    from gidapptools.meta_data.meta_paths.meta_paths_item import MetaPaths

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SpecVisitor:

    def __init__(self, spec_item_class: type["SpecItem"] = SpecItem) -> None:
        self.spec_item_class = spec_item_class
        self.parse_func: Callable[[str], ConverterSpecData] = parse_specification

    def visit(self, in_dict: Union["AdvancedDict", dict], key_path: tuple[str], value: dict[str, object], default_convertert_data: ConverterSpecData = MiscEnum.NOTHING) -> None:

        key_path = tuple(key_path)
        try:
            converter_data = self.parse_func(value["converter"])
        except KeyError:
            converter_data = default_convertert_data
        new_value = self.spec_item_class(section_name=key_path[0], key_name=key_path[1], converter_data=converter_data, **{k: v for k, v in value.items() if k != "converter"})

        if isinstance(in_dict, AdvancedDict):
            in_dict.set(key_path, new_value)
        else:
            set_by_key_path(in_dict, key_path, new_value)


class SpecData(AdvancedDict):
    visit_lock = RLock()
    special_section_names: dict[str, str] = {"config_file_creation_settings": "__CONFIG_FILE_CREATION_SETTINGS__"}

    def __init__(self, name: str, visitor: SpecVisitor, default_converter_data: ConverterSpecData = None, **kwargs) -> None:
        self.name = name
        self.visitor = visitor
        self.default_converter_data = default_converter_data or ConverterSpecData(typus="string", kw_arguments={})
        self._spec_items: dict[tuple[str, str], SpecItem] = None
        super().__init__(data=None, **kwargs)

    @property
    def spec_items(self) -> dict[tuple[str, str], SpecItem]:
        if self._spec_items is None:
            self.reload()

        return self._spec_items

    @property
    def data(self) -> dict:
        with self.visit_lock:
            return super().data

    @property
    def all_spec_items(self) -> tuple[SpecItem]:
        _out = []
        for section_content in self.data.values():
            _out += section_content.values()
        return tuple(sorted(_out, key=lambda x: (x.section_name, x.key_name)))

    def get_spec_item(self, section_name: str, key_name: str) -> SpecItem:
        return self.spec_items[(section_name, key_name)]

    def _get_section_default(self, section_name: str) -> EntryTypus:

        return self.get_spec_item(section_name, '__default__')

    def _get_entry_default(self, section_name: str, entry_key: str) -> Union[str, MiscEnum]:
        return self.get_spec_attribute(section_name, entry_key, 'default', MiscEnum.NOTHING)

    def get_verbose_name(self, section_name: str, entry_key: str = None) -> Optional[str]:
        return self.get_spec_attribute(section_name=section_name, entry_key=entry_key, attribute="verbose_name", default=None)

    def get_description(self, section_name: str, entry_key: str) -> str:
        return self.get_spec_attribute(section_name, entry_key, "short_description", default="")

    def get_gui_visible(self, section_name: str, entry_key: str) -> bool:
        return self.get_spec_attribute(section_name, entry_key, "gui_visible", default=True)

    def get_spec_attribute(self, section_name: str, entry_key: str, attribute: str, default=None) -> Any:

        result = getattr(self.get_spec_item(section_name, entry_key), attribute)
        if result is MiscEnum.NOTHING:
            return default

    def modify_with_visitor(self, visitor: "BaseVisitor") -> None:
        for section, section_content in self.data.items():
            for key, key_content in sorted(section_content.items(), key=lambda x: x[0] != "__default__"):
                default_convertert_data = self.default_converter_data.copy()
                if key != "__default__":
                    try:
                        default_convertert_data = self[(section, "__default__")].converter_data
                    except KeyPathError:
                        pass
                visitor.visit(self, key_path=(section, key), value=key_content, default_convertert_data=default_convertert_data)

    def _resolve_values(self) -> None:
        self.modify_with_visitor(self.visitor)
        self._spec_items = {}
        for item in self.all_spec_items:
            self._spec_items[(item.section_name, item.key_name)] = item

    def reload(self) -> None:
        with self.visit_lock:
            self._resolve_values()

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}'


class SpecFile(FileMixin, SpecData):
    def __init__(self, file_path: PATH_TYPE, visitor: SpecVisitor, changed_parameter: Union[Literal['size'], Literal['file_hash']] = 'size', **kwargs) -> None:
        super().__init__(name=Path(file_path).stem.removesuffix("spec").removesuffix("config").removesuffix("_"), visitor=visitor, file_path=file_path, changed_parameter=changed_parameter, ** kwargs)
        self._data = None

    @property
    def data(self) -> dict:
        if self._data is None or self.has_changed is True:
            self.load()
        return self._data

    def reload(self) -> None:
        self.load()

    def load(self) -> None:
        with self.lock:
            self._data = json.loads(self.read())
            super().reload()

    def save(self) -> None:
        with self.lock:
            data = defaultdict(dict)
            for section, section_content in self.data.items():
                for key, spec_item in section_content.items():
                    data[section][key] = spec_item.to_json()

            json_data = json.dumps(data, indent=4, sort_keys=False)
            self.write(json_data)

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}(name={self.name!r},visitor={self.visitor!r}, file_path={self.file_path.as_posix()!r})'


# region[Main_Exec]
if __name__ == '__main__':
    x = SpecFile(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\data\general_configspec.json", visitor=SpecVisitor())
    x.reload()
    import pp

    x.save()
# endregion[Main_Exec]
