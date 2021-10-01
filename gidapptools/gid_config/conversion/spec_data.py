"""
WiP.

Soon.
"""

# region [Imports]


import re
import json


from pathlib import Path
from typing import Any, Callable, Hashable, Union
from datetime import datetime
from threading import Lock
from yarl import URL
from gidapptools.general_helper.dict_helper import AdvancedDict, AdvancedDictError, KeyPathError, BaseVisitor
from gidapptools.gid_config.conversion.conversion_table import EntryTypus
from gidapptools.general_helper.general import defaultable_list_pop
from gidapptools.general_helper.conversion import str_to_bool
from hashlib import blake2b
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.mixins.file_mixin import FileMixin
from gidapptools.types import PATH_TYPE
from gidapptools.gid_signal.interface import get_signal
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SpecVisitor(BaseVisitor):
    sub_argument_regex = re.compile(r"(?P<base_type>\w+)\(((?P<sub_arguments>.*)\))?")

    def __init__(self, extra_handlers: dict[Hashable, Callable] = None, default_handler: Callable = None, sub_argument_separator: str = ',') -> None:
        super().__init__(extra_handlers=extra_handlers, default_handler=default_handler)
        self.sub_argument_separator = sub_argument_separator

    def _modify_value(self, value: Any) -> Any:
        value = super()._modify_value(value)
        try:
            value = self.sub_argument_regex.sub(r"\g<base_type>", value)
        except (AttributeError, TypeError):
            pass

        return value

    def _get_handler_direct(self, value: str) -> Callable:
        return self.handlers.get(value, self._handle_string)

    def _get_sub_arguments(self, value: str, default: list[Any] = None) -> list[Any]:

        try:
            match = self.sub_argument_regex.match(value)
            sub_arguments_string = match.groupdict().get("sub_arguments", default)
            sub_arguments = [i.strip() for i in sub_arguments_string.split(self.sub_argument_separator) if i]
            if not sub_arguments:
                return default
            return sub_arguments
        except AttributeError:
            return default

    def _handle_default(self, value: Any) -> EntryTypus:
        """
        handles all values that other handlers, can't or that raised an error while dispatching to handlers.

        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): The nodes value.

        Returns:
            EntryTypus: An `EntryTypus` with only an `original_value` and the base_typus set to `SpecialTypus.DELAYED)
        """
        return EntryTypus(original_value=value)

    def _handle_boolean(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=bool, other_arguments=self._get_sub_arguments(value, None))

    def _handle_string(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=str, other_arguments=self._get_sub_arguments(value, None))

    def _handle_integer(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=int, other_arguments=self._get_sub_arguments(value, None))

    def _handle_float(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=float, other_arguments=self._get_sub_arguments(value, None))

    def _handle_bytes(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=bytes, other_arguments=self._get_sub_arguments(value, None))

    def _handle_list(self, value: Any) -> EntryTypus:
        """
        Converts the value to `list` with optional sub_type (eg: `list[int]`).

        NAMED_VALUE_ARGUMENTS:
            subtype: The subtype of the list, defaults to `string`, can be any other handled type.
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        sub_arguments = self._get_sub_arguments(value)

        subtypus_string = defaultable_list_pop(sub_arguments, 0, "string")

        handler = self._get_handler_direct(subtypus_string)

        subtypus = handler(subtypus_string)
        return EntryTypus(original_value=value, base_typus=list, named_arguments={"subtypus": subtypus}, other_arguments=sub_arguments)

    def _handle_datetime(self, value: Any) -> EntryTypus:
        """
        [summary]

        NAMED_VALUE_ARGUMENTS:
            fmt: The format to use with `datetime.strptime`, if it is "isoformat" then `datetime.fromisoformat` will be used and if it is `timestamp` then `datetime.fromtimestamp`, defaults to "isoformat"
            time_zone: The timezone to provide to datetime, defaults to: "utc"
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        sub_arguments = self._get_sub_arguments(value)
        fmt = defaultable_list_pop(sub_arguments, 0, "isoformat")
        time_zone = defaultable_list_pop(sub_arguments, 0, "utc")
        return EntryTypus(original_value=value, base_typus=datetime, named_arguments={'fmt': fmt, 'tz': time_zone}, other_arguments=sub_arguments)

    def _handle_path(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            resolve: if the path should be auto-resolved or not.
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        sub_arguments = self._get_sub_arguments(value)
        resolve = defaultable_list_pop(sub_arguments, 0, 'true')
        return EntryTypus(original_value=value, base_typus=Path, named_arguments={'resolve': resolve}, other_arguments=sub_arguments)

    def _handle_url(self, value: Any) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        sub_arguments = self._get_sub_arguments(value)
        return EntryTypus(original_value=value, base_typus=URL, other_arguments=sub_arguments)


class SpecData(AdvancedDict):
    default_visitor_class = SpecVisitor

    def __init__(self, data: dict = None, visitor: SpecVisitor = None, **kwargs) -> None:
        self.visitor = self._make_default_visitor(kwarg_dict=kwargs) if visitor is None else visitor
        super().__init__(data=data, **kwargs)

    def _make_default_visitor(self, kwarg_dict: dict[str, Any]) -> SpecVisitor:
        visitor_kwargs = {"extra_handlers": kwarg_dict.pop('extra_handlers', None),
                          "default_handler": kwarg_dict.pop('default_handler', None),
                          "sub_argument_separator": kwarg_dict.pop("sub_argument_separator", None)}
        return self.default_visitor_class(**visitor_kwargs)

    def _get_section_default(self, section_name: str) -> EntryTypus:
        return self[[section_name, '__default__']]

    def get_entry_typus(self, section_name: str, entry_key: str) -> EntryTypus:
        try:
            return self[[section_name, entry_key]]
        except KeyPathError as error:
            try:
                return self._get_section_default(section_name=section_name)
            except KeyPathError:
                raise error

    def _resolve_values(self) -> None:
        self.modify_with_visitor(self.visitor)

    def reload(self) -> None:
        self.visitor.reload()
        self._resolve_values()


class SpecFile(FileMixin, SpecData):
    def __init__(self, file_path: PATH_TYPE, visitor: SpecVisitor = None, **kwargs) -> None:
        super().__init__(visitor=visitor, file_path=file_path, ** kwargs)
        self._data = None
        self.spec_name = self.file_path.stem.casefold()

    @property
    def data(self) -> dict:
        if self._data is None or self.has_changed is True:
            self.load()
        return self._data

    def load(self) -> None:
        self._data = json.loads(self.read())
        self.reload()


# class SpecDataFile(SpecData):

#     def __init__(self, in_file: Path, changed_parameter: str = 'size', ensure: bool = True, visitor_class: SpecVisitor = None, **kwargs) -> None:
#         super().__init__(visitor_class=visitor_class, **kwargs)

#         self.file_path = Path(in_file).resolve()
#         self.changed_parameter = changed_parameter
#         self.ensure = ensure
#         self.last_size: int = None
#         self.last_file_hash: str = None
#         self.data = None
#         self.lock = Lock()

#     @property
#     def has_changed(self) -> bool:
#         if self.changed_parameter == 'always':
#             return True
#         if self.changed_parameter == 'both':
#             if any([param is None for param in [self.last_size, self.last_file_hash]] + [self.last_size != self.size, self.last_file_hash != self.last_file_hash]):
#                 return True
#         if self.changed_parameter == 'size':
#             if self.last_size is None or self.size != self.last_size:
#                 return True
#         elif self.changed_parameter == 'file_hash':
#             if self.last_file_hash is None or self.file_hash != self.last_file_hash:
#                 return True
#         return False

#     def get_converter(self, key_path: Union[list[str], str]) -> EntryTypus:
#         with self.lock:
#             if self.data is None or self.has_changed is True:
#                 self.reload(locked=True)
#             return super().get_converter(key_path)

#     @property
#     def size(self) -> int:
#         return self.file_path.stat().st_size

#     @property
#     def file_hash(self) -> str:
#         _file_hash = blake2b()
#         with self.file_path.open('rb') as f:
#             for chunk in f:
#                 _file_hash.update(chunk)
#         return _file_hash.hexdigest()

#     def reload(self, locked: bool = False) -> None:
#         self.load(locked)
#         super().reload()

#     def _json_converter(self, item: Union[EntryTypus, type]) -> str:
#         try:
#             return item.convert_for_json()
#         except AttributeError:
#             return EntryTypus.special_name_conversion_table(type.__name__, type.__name__)

#     def load(self, locked: bool = False):
#         def _load():
#             with self.file_path.open('r', encoding='utf-8', errors='ignore') as f:
#                 return json.load(f)

#         if self.file_path.exists() is False and self.ensure is True:
#             self.write(locked=locked)
#         if locked is False:
#             with self.lock:
#                 self.data = _load()
#         else:
#             self.data = _load()

#     def write(self, locked: bool = False) -> None:
#         def _write():
#             with self.file_path.open('w', encoding='utf-8', errors='ignore') as f:
#                 data = {} if self.data is None else self.data
#                 json.dump(data, f, default=self._json_converter, indent=4, sort_keys=True)

#         if locked is False:
#             with self.lock:
#                 _write()
#         else:
#             _write()


# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
