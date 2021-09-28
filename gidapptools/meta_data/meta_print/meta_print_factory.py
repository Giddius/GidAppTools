"""
WiP.

Soon.
"""

# region [Imports]


from pathlib import Path

from gidapptools.utility.enums import NamedMetaPath, EnvName
from gidapptools.errors import AppNameMissingError
from gidapptools.meta_data.meta_paths.meta_paths_item import MetaPaths
from gidapptools.abstract_classes.abstract_meta_factory import AbstractMetaFactory, AbstractMetaItem
from gidapptools.meta_data.meta_paths.appdirs_implementations import GidAppDirs
from gidapptools.meta_data.config_kwargs import ConfigKwargs
from gidapptools.meta_data.meta_print.meta_print_item import MetaPrint
from gidapptools.meta_data.meta_print.console_implementations import ExtraConsoleConfiguration
from rich.console import Console as RichConsole
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MetaPrintFactory(AbstractMetaFactory):
    product_class = MetaPrint

    def setup(self) -> None:
        self.is_setup = True

    def _build(self) -> AbstractMetaItem:
        if self.is_setup is False:
            self.setup()

        kwargs = self.config_kwargs.get_kwargs_for(RichConsole) | self.config_kwargs.get_kwargs_for(ExtraConsoleConfiguration)

        return self.product_class(**kwargs)


# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
