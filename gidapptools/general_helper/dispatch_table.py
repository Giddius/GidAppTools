"""
WiP.

Soon.
"""

# region [Imports]


import inspect

from pathlib import Path
from typing import Callable, Hashable, Mapping, Union

from gidapptools.general_helper.enums import MiscEnum

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class dispatch_mark:
    """
    Marks a method as a dispatch function for an instance `BaseDispatchTable`.
    """
    attribute_name: str = '_dispatch_key'
    DEFAULT = MiscEnum.DEFAULT

    def __init__(self, dispatch_key: Hashable = None):
        self.dispatch_key = dispatch_key

    def __call__(self, func: Callable):
        dispatch_key = func.__name__ if self.dispatch_key is None else self.dispatch_key
        setattr(func, self.attribute_name, dispatch_key)

        return func


class BaseDispatchTable:
    DEFAULT = MiscEnum.DEFAULT
    mark = dispatch_mark

    def __init__(self,
                 instance: object = None,
                 auto_collect_prefix: str = None,
                 extra_dispatch: Mapping[Hashable, Callable] = None,
                 default_value: Callable = None,
                 key_conversion: Union[Mapping, Callable] = None,
                 aliases: Mapping[Hashable, Hashable] = None) -> None:
        """
        [summary]

        [extended_summary]

        Args:
            instance (object, optional): [description]. Defaults to None.
            auto_collect_prefix (str, optional): [description]. Defaults to None.
            extra_dispatch (Mapping[Hashable, Callable], optional): [description]. Defaults to None.
            default_value (Callable, optional): [description]. Defaults to None.
            key_conversion (Union[Mapping, Callable], optional): [description]. Defaults to None.
            aliases (Mapping[Hashable, Hashable], optional): [description]. Defaults to None.
        """
        self.instance = instance
        self.auto_collect_prefix = auto_collect_prefix
        self.extra_dispatch = {} if extra_dispatch is None else extra_dispatch
        self._table: dict[Hashable, Callable] = None
        self.default_value: Callable = default_value
        self._aliases = {} if aliases is None else aliases
        if key_conversion is None:
            self.key_conversion = lambda x: x
        elif isinstance(key_conversion, Mapping):
            self.key_conversion = lambda x: key_conversion.get(x, x)
        else:
            self.key_conversion = key_conversion

    def set_default_value(self, value: Callable) -> None:
        self.default_value = value
        self._table[dispatch_mark.DEFAULT] = value

    def _collect_dispatch_data(self) -> None:
        instance = self if self.instance is None else self.instance
        collected_data = {}
        for meth_name, meth_obj in inspect.getmembers(instance, inspect.ismethod):
            if self.auto_collect_prefix is not None and meth_name.startswith(self.auto_collect_prefix):
                key = self.key_conversion(meth_name.removeprefix(self.auto_collect_prefix))
                collected_data[key] = meth_obj

            key = self.key_conversion(getattr(meth_obj, dispatch_mark.attribute_name, None))
            if key in self._aliases:
                raise KeyError(f'An alias cannot be the same as a dispatch key, {key=!r}')
            if key is dispatch_mark.DEFAULT and self.default_value is None:
                self.default_value = meth_obj
            if key is not None:
                collected_data[key] = meth_obj

        self._table = collected_data

    def __getitem__(self, key) -> Callable:
        if self._table is None:
            self._collect_dispatch_data()
        combined_table = self._table | self.extra_dispatch
        key = self._aliases.get(key, key)
        return combined_table[key]

    def get(self, key: Hashable, default=MiscEnum.NOTHING) -> Callable:
        try:
            return self[key]
        except KeyError:
            return self.default_value if default is MiscEnum.NOTHING else default


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
