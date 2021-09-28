"""
WiP.

Soon.
"""

# region [Imports]


from pathlib import Path
from typing import Any, Callable, Union
from datetime import datetime

from gidapptools.general_helper.dispatch_table import BaseDispatchTable
from gidapptools.errors import DispatchError
import attr
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.enums import SpecialTypus
from gidapptools.gid_config.conversion.entry_typus_item import EntryTypus
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ConversionTable(BaseDispatchTable):

    def get_converter(self, typus: Union[type, EntryTypus]) -> Callable:
        if not isinstance(typus, EntryTypus):
            typus = EntryTypus(base_typus=typus)

        return self.get(typus)

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
