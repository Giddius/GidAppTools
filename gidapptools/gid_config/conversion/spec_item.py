"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Optional
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.conversion.converter_grammar import ConverterSpecData, reverse_replace_value_words

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    pass

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SpecSection:
    __slots__ = ("name",
                 "default_converter",
                 "description",
                 "dynamic_entries_allowed",
                 "gui_visible",
                 "implemented",
                 "verbose_name",
                 "entries")

    def __init__(self,
                 name: str,
                 default_converter: ConverterSpecData = MiscEnum.NOTHING,
                 description: str = "",
                 dynamic_entries_allowed: bool = False,
                 gui_visible: bool = True,
                 implemented: bool = True,
                 verbose_name: str = MiscEnum.NOTHING) -> None:
        self.name = name
        self.default_converter = default_converter
        self.description = description
        self.dynamic_entries_allowed = dynamic_entries_allowed
        self.gui_visible = gui_visible
        self.implemented = implemented
        self.verbose_name = verbose_name if verbose_name is not MiscEnum.NOTHING else self.name.replace("_", " ").title()
        self.entries: dict[str, "SpecEntry"] = {}

    def __getitem__(self, name: str) -> "SpecEntry":
        return self.entries[name]

    def add_entry(self, entry: "SpecEntry") -> None:
        entry.set_section(self)
        self.entries[entry.name] = entry

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name!r})'


def converter_data_to_string(converter_data: "ConverterSpecData") -> str:
    text = converter_data["typus"]
    if converter_data["kw_arguments"]:
        sub_args = []
        for k, v in converter_data["kw_arguments"].items():
            sub_args.append(f"{k}={reverse_replace_value_words(v)}")

        text += "(" + ', '.join(sub_args) + ")"
    return text


class SpecEntry:
    __slots__ = ("name",
                 "converter",
                 "default",
                 "description",
                 "gui_visible",
                 "implemented",
                 "verbose_name",
                 "_section")

    def __init__(self,
                 name: str,
                 converter: ConverterSpecData = MiscEnum.NOTHING,
                 default: str = MiscEnum.NOTHING,
                 description: str = "",
                 verbose_name: str = MiscEnum.NOTHING,
                 implemented: bool = True,
                 gui_visible: bool = True) -> None:
        self.name = name
        self.converter = converter
        self.default = default
        self.description = description
        self.verbose_name = verbose_name if verbose_name is not MiscEnum.NOTHING else self.name.replace("_", " ").title()
        self.implemented = implemented
        self.gui_visible = gui_visible
        self._section: SpecSection = None

    @property
    def section(self) -> Optional[SpecSection]:
        return self._section

    def set_section(self, section: SpecSection) -> None:
        self._section = section
        if self.converter is MiscEnum.NOTHING and self.section.default_converter is not MiscEnum.NOTHING:
            self.converter = self.section.default_converter

        if self.section.gui_visible is False:
            self.gui_visible = False

        if self.section.implemented is False:
            self.implemented = False

    def __getitem__(self, name: str):
        if name in {"name", "converter", "default", "description", "verbose_name", "implemented", "gui_visible"}:
            return getattr(self, name)
        raise KeyError(name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name!r})'


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
