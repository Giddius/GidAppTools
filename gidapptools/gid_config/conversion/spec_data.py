"""
WiP.

Soon.
"""

# region [Imports]


import re
import json


from pathlib import Path
from typing import Any, Callable, Hashable, Union, Literal
from datetime import datetime
from threading import Lock
from yarl import URL
from gidapptools.general_helper.dict_helper import AdvancedDict, AdvancedDictError, KeyPathError, BaseVisitor, set_by_key_path
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

    def visit(self, in_dict: Union["AdvancedDict", dict], key_path: tuple[str], value: Any) -> None:

        key_path = tuple(key_path)
        value_key = self._modify_value(value)

        handler = self.handlers.get(key_path, self.handlers.get(value_key, self.default_handler))
        if handler is None:
            return
        if isinstance(in_dict, AdvancedDict):
            in_dict.set(key_path, handler(value, self._get_sub_arguments(value)))
        else:
            set_by_key_path(in_dict, key_path, handler(value, self._get_sub_arguments(value)))

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
        default = [] if default is None else default
        try:
            match = self.sub_argument_regex.match(value)
            sub_arguments_string = match.groupdict().get("sub_arguments", default)
            sub_arguments = [i.strip() for i in sub_arguments_string.split(self.sub_argument_separator) if i]
            if not sub_arguments:
                return default
            return sub_arguments
        except AttributeError:
            return default

    def _handle_default(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
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

    def _handle_boolean(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=bool, other_arguments=self._get_sub_arguments(value, None))

    def _handle_string(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=str, other_arguments=sub_arguments)

    def _handle_integer(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=int, other_arguments=sub_arguments)

    def _handle_float(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=float, other_arguments=sub_arguments)

    def _handle_bytes(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=bytes, other_arguments=sub_arguments)

    def _handle_list(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
        """
        Converts the value to `list` with optional sub_type (eg: `list[int]`).

        NAMED_VALUE_ARGUMENTS:
            subtype: The subtype of the list, defaults to `string`, can be any other handled type.
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        subtypus_string = defaultable_list_pop(sub_arguments, 0, "string")
        split_char = defaultable_list_pop(sub_arguments, 0, ",")
        handler = self._get_handler_direct(subtypus_string)

        subtypus = handler(subtypus_string, [])
        return EntryTypus(original_value=value, base_typus=list, named_arguments={"subtypus": subtypus, "split_char": split_char}, other_arguments=sub_arguments)

    def _handle_datetime(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
        """
        [summary]

        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=datetime, other_arguments=sub_arguments)

    def _handle_path(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=Path, other_arguments=sub_arguments)

    def _handle_url(self, value: Any, sub_arguments: list[Any]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=URL, other_arguments=sub_arguments)


class SpecData(AdvancedDict):
    default_visitor_class = SpecVisitor

    def __init__(self, visitor: SpecVisitor, **kwargs) -> None:
        self.visitor = visitor
        super().__init__(data=None, **kwargs)

    def _get_section_default(self, section_name: str) -> EntryTypus:

        return self.get([section_name, '__default__'], str)

    def get_entry_typus(self, section_name: str, entry_key: str) -> EntryTypus:
        try:
            return self[[section_name, entry_key]]
        except KeyPathError as error:
            try:
                return self._get_section_default(section_name=section_name)
            except KeyPathError:
                raise error

    def set_typus_value(self, section_name: str, entry_key: str, typus_value: str) -> None:
        if section_name not in self:
            self[section_name] = {}
        self[section_name][entry_key] = typus_value

    def _resolve_values(self) -> None:
        self.modify_with_visitor(self.visitor)

    def reload(self) -> None:
        self.visitor.reload()
        self._resolve_values()


class SpecFile(FileMixin, SpecData):
    def __init__(self, file_path: PATH_TYPE, visitor: SpecVisitor, changed_parameter: Union[Literal['size'], Literal['file_hash']] = 'size', **kwargs) -> None:
        super().__init__(visitor=visitor, file_path=file_path, changed_parameter=changed_parameter, ** kwargs)
        self._data = None
        self.spec_name = self.file_path.stem.casefold()

    @property
    def data(self) -> dict:
        if self._data is None or self.has_changed is True:
            self.load()
        return self._data

    def reload(self) -> None:
        self.load()

    def load(self) -> None:
        self._data = json.loads(self.read())
        super().reload()

    def save(self) -> None:
        json_data = json.dumps(self.data, indent=4, sort_keys=False, default=lambda x: x.convert_for_json())
        self.write(json_data)

    def set_typus_value(self, section_name: str, entry_key: str, typus_value: str) -> None:
        super().set_typus_value(section_name=section_name, entry_key=entry_key, typus_value=typus_value)
        self.save()

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
