"""
WiP.

Soon.
"""

# region [Imports]


from pathlib import Path
from typing import Any, Callable, Union, Hashable, Mapping
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


class ConfigValueConversionTable(BaseDispatchTable):

    def __init__(self, instance: object = None, extra_dispatch: Mapping[Hashable, Callable] = None, default_value: Callable = None) -> None:
        super().__init__(instance=instance, extra_dispatch=extra_dispatch, default_value=default_value)

    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    @BaseDispatchTable.mark(MiscEnum.DEFAULT)
    def _default(self, value: str, **named_arguments) -> str:
        return value

    @BaseDispatchTable.mark(str)
    def _string(self, value: str, **named_arguments) -> str:
        return str(value)

    @BaseDispatchTable.mark(int)
    def _integer(self, value: str, **named_arguments) -> int:
        return int(value)

    @BaseDispatchTable.mark(float)
    def _float(self, value: str, **named_arguments) -> float:
        return float(value)

    @BaseDispatchTable.mark(bool)
    def _boolean(self, value: str, **named_arguments) -> bool:
        string_value = str(value)
        return str_to_bool(string_value)

    @time_func()
    @BaseDispatchTable.mark(list)
    def _list(self, value: str, **named_arguments) -> list[Any]:
        subtypus = named_arguments.get('subtypus')

        converter = self.get(subtypus)

        return [converter(item.strip(), **named_arguments) for item in value.split(',') if item]

    @BaseDispatchTable.mark(datetime)
    def _datetime(self, value: str, **named_arguments) -> datetime:
        fmt = named_arguments.get('fmt')
        time_zone = named_arguments.get('tz')
        # TODO: NEEDS TO CHANGE TO BE ABLE TO PARSE MORE FORMATS
        time_zone = timezone.utc if time_zone == 'utc' else time_zone
        if hasattr(datetime, fmt):
            try:
                value = getattr(datetime, fmt)(value, tz=time_zone)
            except TypeError:
                value = getattr(datetime, fmt)(value)
        else:
            value = datetime.strptime(value, fmt)
        if value.tzinfo is not time_zone:
            value = value.replace(tzinfo=time_zone)
        return value

    @BaseDispatchTable.mark(Path)
    def _path(self, value: str, **named_arguments) -> Path:
        path = Path(value)
        if named_arguments.get("resolve") is True:
            path = path.resolve()
        return path

    @BaseDispatchTable.mark(URL)
    def _url(self, value: str, **named_arguments) -> URL:
        return URL(value)

    def get_converter(self, typus: Union[type, EntryTypus]) -> Callable:
        if not isinstance(typus, EntryTypus):
            typus = EntryTypus(base_typus=typus)

        converter = self.get(typus.base_typus)
        return partial(converter, **typus.named_arguments)
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
