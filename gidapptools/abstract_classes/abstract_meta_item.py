"""
WiP.

Soon.
"""

# region [Imports]


from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable

from gidapptools.utility.helper import abstract_class_property
from gidapptools.meta_data.config_kwargs import ConfigKwargs
from gidapptools.general_helper.string_helper import StringCaseConverter
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AbstractMetaItem(ABC):

    @classmethod
    @property
    def name(cls) -> str:
        return StringCaseConverter.convert_to(cls.__name__, StringCaseConverter.SNAKE)

    @abstractmethod
    def as_dict(self, pretty: bool = False) -> dict[str, Any]:
        ...

    @abstractmethod
    def to_storager(self, storager: Callable = None) -> None:
        ...

    @abstractmethod
    def clean_up(self, **kwargs) -> None:
        ...


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
