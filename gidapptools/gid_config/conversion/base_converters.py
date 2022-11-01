"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Union, TypeVar, Optional, TypeAlias, TypeGuard, get_args, get_origin, get_type_hints, Literal
from pathlib import Path
from functools import cached_property
from datetime import datetime, timedelta
import inspect
# * Third Party Imports --------------------------------------------------------------------------------->
from frozendict import frozendict
from pprint import pprint
# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.conversion import bytes2human, human2bytes, str_to_bool, seconds2human, human2timedelta
from gidapptools.general_helper.import_helper import is_importable
import re
from gidapptools.errors import MinError, MaxError
try:
    import rich
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.gid_config.conversion.conversion_table import ConversionTable

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]
PYSIDE6_AVAILABLE = is_importable("PySide6")
YARL_AVAILABLE = is_importable("yarl")
THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]


class ConfigValueConverter(ABC):
    __slots__ = ("conversion_table",)
    is_standard_converter: bool = False
    value_typus: str = None
    value_typus_aliases: tuple[str] = tuple()
    named_arguments_options: frozendict[str, object] = frozendict()
    dependencies: list[str] = None

    def __init__(self, conversion_table: "ConversionTable") -> None:
        self.conversion_table = conversion_table

    def __init_subclass__(cls) -> None:
        if cls.value_typus in {None, ..., "", MiscEnum.NOTHING}:
            raise ValueError(f"{cls.__name__!r} has an invalid value_typus({cls.value_typus!r})")

    @property
    def encode(self):
        return self.to_config_value

    @property
    def decode(self):
        return self.to_python_value

    def validate_value(self, value, entry_name: str, section_name: str, config) -> None:
        ...

    @abstractmethod
    def to_config_value(self, value: Any) -> str:
        ...

    @abstractmethod
    def to_python_value(self, value: str) -> Any:
        ...

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}'


class IntegerConfigValueConverter(ConfigValueConverter):
    __slots__ = ("minimum", "maximum", "on_min_error", "on_max_error")
    is_standard_converter: bool = True
    value_typus = "integer"
    value_typus_aliases = ("int",)
    is_default: bool = True

    def __init__(self, conversion_table: "ConversionTable", minimum: int = None, maximum: int = None, on_min_error: Literal["raise", "set_minimum"] = "raise", on_max_error: Literal["raise", "set_maximum"] = "raise") -> None:
        super().__init__(conversion_table)
        self.minimum = minimum
        self.maximum = maximum
        self.on_min_error = on_min_error
        self.on_max_error = on_max_error

    def to_config_value(self, value: int) -> str:
        try:
            self.validate_value(value, None, None, None)
        except MinError:
            if self.on_min_error == "raise":
                raise
            elif self.on_min_error == "set_minimum":
                value = self.minimum

        except MaxError:
            if self.on_max_error == "raise":
                raise
            elif self.on_max_error == "set_maximum":
                value = self.maximum

        if value is None:
            return ""

        return str(value)

    def to_python_value(self, value: str) -> Union[int, None]:
        if value is None:
            return None

        converted_value = int(value)
        if self.minimum:
            converted_value = max(converted_value, self.minimum)
        if self.maximum:
            converted_value = min(converted_value, self.maximum)
        return converted_value

    def validate_value(self, value: Optional[int], entry_name: str, section_name: str, config) -> None:
        if value is None:
            return

        if self.minimum is not None and value < self.minimum:
            raise MinError(value, self.minimum, converter=self, section_name=section_name, entry_name=entry_name, config=config)

        if self.maximum is not None and value > self.maximum:
            raise MaxError(value, self.maximum, converter=self, section_name=section_name, entry_name=entry_name, config=config)


class FloatConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "float"
    value_typus_aliases = ("floating_point", "double")

    def to_config_value(self, value: float) -> str:
        if value is None:
            return ""
        return str(value)

    def to_python_value(self, value: str) -> Union[float, None]:
        if value is None:
            return None
        return float(value)


class BooleanConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "boolean"
    value_typus_aliases = ("bool",)
    true_string_value = "yes"
    false_string_value = "no"

    def to_config_value(self, value: bool) -> str:
        if value is None:
            return ""
        if value is True:
            return self.true_string_value

        if value is False:
            return self.false_string_value

    def to_python_value(self, value: str) -> Union[bool, None]:
        if value is None:
            return None
        return str_to_bool(str(value))


class StringConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "string"
    value_typus_aliases = ("str",)

    def to_config_value(self, value: str) -> str:
        if value is None:
            return ""
        return value

    def to_python_value(self, value: str) -> Union[str, None]:
        if value is None:
            return None
        return value


class DateTimeConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "datetime"

    def to_config_value(self, value: datetime) -> str:
        if value is None:
            return ""
        return value.isoformat(timespec="seconds")

    def to_python_value(self, value: str) -> Union[datetime, None]:
        if value is None:
            return None
        return datetime.fromisoformat(value)


class TimedeltaConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "timedelta"

    def to_config_value(self, value: timedelta) -> str:
        if value is None:
            return ""
        return seconds2human(value)

    def to_python_value(self, value: str) -> Union[timedelta, None]:
        if value is None:
            return None
        return human2timedelta(value)


class PathConfigValueConverter(ConfigValueConverter):
    __slots__ = ("resolve",)
    is_standard_converter: bool = True
    value_typus = "path"
    value_typus_aliases = ("fs_path",)

    def __init__(self, conversion_table: "ConversionTable", resolve: bool = False) -> None:
        super().__init__(conversion_table)
        self.resolve = resolve

    def to_config_value(self, value: Path) -> str:
        if value is None:
            return ""
        path = Path(value)
        if self.resolve is True:
            path = path.resolve()
        return path.as_posix()

    def to_python_value(self, value: str) -> Union[Path, None]:
        if value is None:
            return None
        path = Path(value)
        if self.resolve is True:
            path = path.resolve()
        return path


class FileSizeConfigValueConverter(ConfigValueConverter):
    __slots__ = ()
    is_standard_converter: bool = True
    value_typus: str = "file_size"

    def to_config_value(self, value: int) -> str:
        if value is None:
            return ""
        return bytes2human(value)

    def to_python_value(self, value: str) -> Union[int, None]:
        if value is None:
            return None

        return human2bytes(value)


SUB_TYPUS_TYPE = TypeVar("SUB_TYPUS_TYPE")


class ListConfigValueConverter(ConfigValueConverter):
    __slots__ = ("sub_typus", "split_char")
    is_standard_converter: bool = True
    value_typus = "list"

    def __init__(self, conversion_table: "ConversionTable", sub_typus: str = "string", split_char: str = ",") -> None:
        super().__init__(conversion_table)
        self.sub_typus = sub_typus
        self.split_char = split_char

    def to_config_value(self, value: list) -> str:
        if value is None:
            return ""
        sub_converter: "ConfigValueConverter" = self.conversion_table.converters[self.sub_typus](self.conversion_table)
        return f"{self.split_char} ".join(sub_converter.to_config_value(item) for item in value)

    def to_python_value(self, value: str) -> Union[list[SUB_TYPUS_TYPE], None]:
        if value is None:
            return None
        sub_converter: "ConfigValueConverter" = self.conversion_table.converters[self.sub_typus](self.conversion_table)
        return [sub_converter.to_python_value(item) for item in value.split(self.split_char) if item.strip()]


if PYSIDE6_AVAILABLE is True:
    from PySide6.QtGui import QColor

    class QColorValueConverter(ConfigValueConverter):
        __slots__ = tuple()
        is_standard_converter: bool = True
        value_typus = "qcolor"
        dependencies: list[str] = ["PySide6"]

        def to_config_value(self, value: Any, **named_arguments) -> str:
            if value is None:
                return ""
            return ', '.join(str(i) for i in value.getRgb())

        def to_python_value(self, value: str, **named_arguments) -> Union[QColor, None]:
            if value is None:
                return None
            r, g, b, a = (int(i.strip()) for i in value.split(',') if i.strip())
            return QColor(r, g, b, a)


if YARL_AVAILABLE is True:
    from yarl import URL

    class URLValueConverter(ConfigValueConverter):
        __slots__ = tuple()
        is_standard_converter: bool = True
        value_typus = "url"
        dependencies: list[str] = ["yarl"]

        def to_config_value(self, value: Union[URL, None]) -> str:
            if value is None:
                return ""
            return value.human_repr()

        def to_python_value(self, value: Union[str, None]) -> Union[URL, None]:
            if value is None:
                return None
            return URL(value)


def get_standard_converter() -> tuple[type["ConfigValueConverter"]]:
    return tuple(sc for sc in ConfigValueConverter.__subclasses__() if sc.is_standard_converter is True)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
