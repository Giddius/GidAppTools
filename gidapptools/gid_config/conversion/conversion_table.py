"""
WiP.

Soon.
"""

# region [Imports]


from pathlib import Path
from typing import Any, Callable, Union, Hashable, Mapping, TYPE_CHECKING
from datetime import datetime, timezone
from yarl import URL
from gidapptools.general_helper.dispatch_table import BaseDispatchTable
from gidapptools.errors import DispatchError
import attr
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.enums import SpecialTypus
from gidapptools.gid_config.conversion.entry_typus_item import EntryTypus
from gidapptools.general_helper.conversion import str_to_bool
from functools import partial
from gidapptools.general_helper.timing import time_func

from gidapptools.gid_config.parser.tokens import Entry
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

# Function for conversion
#
# def conversion_function(value: Any, *other_arguments, **named_arguments)->Any:
#     ...


class ValueEncoder:

    def __init__(self, datetime_fmt: str = "isoformat") -> None:
        self.datetime_fmt = datetime_fmt

    def _encode_list(self, value: list) -> str:
        return ', '.join(self.encode(item) for item in value)

    def _encode_datetime(self, value: datetime) -> str:
        if hasattr(value, self.datetime_fmt):
            return self.encode(getattr(value, self.datetime_fmt)())
        else:
            return value.strftime(self.datetime_fmt)

    def _encode_path(self, value: Path) -> str:
        return value.as_posix()

    def _encode_url(self, value: URL) -> str:
        return value.human_repr()

    def encode(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        sub_encoder = {int: str,
                       float: str,
                       bool: str,
                       list: self._encode_list,
                       datetime: self._encode_datetime,
                       Path: self._encode_path,
                       URL: self._encode_url}
        for path_subclass in Path.__subclasses__():
            sub_encoder[path_subclass] = self._encode_path

        return sub_encoder.get(type(value), str)(value)

    def __call__(self, value: Any) -> str:
        return self.encode(value=value)


class ConfigValueConversionTable(BaseDispatchTable):

    def __init__(self, extra_dispatch: Mapping[Hashable, Callable] = None) -> None:
        super().__init__(extra_dispatch=extra_dispatch)

    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    @BaseDispatchTable.mark(MiscEnum.DEFAULT)
    def _default(self, value: str, mode: str = 'decode', **named_arguments) -> str:
        if mode == "decode":
            return value
        elif mode == "encode":
            return value

    @BaseDispatchTable.mark(str)
    def _string(self, value: str, mode: str = 'decode', **named_arguments) -> str:
        if mode == "decode":
            return str(value)
        elif mode == "encode":
            return value

    @BaseDispatchTable.mark(int)
    def _integer(self, value: str, mode: str = 'decode', **named_arguments) -> int:
        if mode == "decode":
            return int(value)
        elif mode == "encode":
            str(value)

    @BaseDispatchTable.mark(float)
    def _float(self, value: str, mode: str = 'decode', **named_arguments) -> float:
        if mode == "decode":
            return float(value)
        elif mode == "encode":
            return str(value)

    @BaseDispatchTable.mark(bool)
    def _boolean(self, value: str, mode: str = 'decode', **named_arguments) -> bool:

        if mode == "decode":
            string_value = str(value)
            new_value = str_to_bool(string_value)
        elif mode == "encode":
            new_value = str(value)

        return new_value

    @BaseDispatchTable.mark(list)
    def _list(self, value: str, mode: str = 'decode', **named_arguments) -> list[Any]:
        if mode == "decode":
            sub_typus = named_arguments.get('sub_typus')
            split_char = named_arguments.get('split_char', ',')
            return [self.convert(entry=item.strip(), typus=sub_typus) for item in value.split(split_char) if item]
        elif mode == "encode":
            return ', '.join(self.encode(item) for item in value)

    @BaseDispatchTable.mark(datetime)
    def _datetime(self, value: str, mode: str = 'decode', **named_arguments) -> datetime:
        if mode == "decode":
            return datetime.fromisoformat(value)
        elif mode == "encode":
            return value.isoformat()

    @BaseDispatchTable.mark(Path, aliases=Path.__subclasses__())
    def _path(self, value: str, mode: str = 'decode', **named_arguments) -> Path:
        if mode == "decode":
            path = Path(value)

            return path
        elif mode == "encode":
            return value.as_posix()

    @BaseDispatchTable.mark(URL)
    def _url(self, value: str, mode: str = 'decode', **named_arguments) -> URL:
        if mode == "decode":
            return URL(value)
        elif mode == "encode":
            return value.human_repr()

    def _convert_by_type(self, entry: "Entry", typus: type) -> Any:
        converter = self.get(typus)
        value = entry.value if isinstance(entry, Entry) else entry
        return converter(value=value)

    def _convert_by_entry_typus(self, entry: "Entry", typus: EntryTypus) -> Any:
        converter = self.get(typus.base_typus)
        value = entry.value if isinstance(entry, Entry) else entry
        return converter(value=value, **typus.named_arguments)

    def encode(self, value: Any) -> str:
        converter = self.get_converter(type(value))
        return converter(value, mode="encode")

    def convert(self, entry: "Entry", typus: Union[type, EntryTypus]) -> Any:
        if not isinstance(typus, EntryTypus):
            return self._convert_by_type(entry=entry, typus=typus)

        return self._convert_by_entry_typus(entry=entry, typus=typus)

    def __call__(self, entry: "Entry", typus: Union[type, EntryTypus]) -> Any:

        return self.convert(entry=entry, typus=typus)

    def get_converter(self, typus: Union[type, EntryTypus]) -> Callable:
        if not isinstance(typus, EntryTypus):
            typus = EntryTypus(base_typus=typus)

        converter = self.get(typus.base_typus)
        return partial(converter, **typus.named_arguments)
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
