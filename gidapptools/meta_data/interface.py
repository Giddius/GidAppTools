"""
WiP.

Soon.
"""

# region [Imports]


from warnings import warn

from pathlib import Path
from typing import Any, Union
from functools import reduce
from operator import or_
from importlib.metadata import entry_points
from gidapptools.utility.enums import NamedMetaPath
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.errors import NotSetupError, NoFactoryFoundError, MetaItemNotFoundError, RegisterAfterSetupError
from gidapptools.meta_data.config_kwargs import ConfigKwargs
from gidapptools.types import PATH_TYPE

from gidapptools.meta_data.meta_info import MetaInfoFactory, MetaInfo
from gidapptools.meta_data.meta_paths import MetaPathsFactory, MetaPaths
from gidapptools.abstract_classes.abstract_meta_factory import AbstractMetaFactory
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem
from gidapptools.meta_data.meta_print.meta_print_factory import MetaPrintFactory, MetaPrint
import inspect
from gidapptools.data import ENTRY_POINT_NAME

# REMOVE_BEFORE_BUILDING_DIST
from gidapptools.utility._debug_tools import dprint

print = dprint

# end REMOVE_BEFORE_BUILDING_DIST

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


META_ITEMS_TYPE = Any


class AppMeta:
    factories: list[AbstractMetaFactory] = [MetaInfoFactory,
                                            MetaPathsFactory,
                                            MetaPrintFactory]
    plugin_data: list[dict[str, Any]] = []
    default_to_initialize = [factory.product_name for factory in factories]
    default_base_configuration: dict[str, Any] = reduce(or_, (factory.default_configuration for factory in factories))

    def __init__(self) -> None:
        self.is_setup = False
        self.meta_items: dict[str, AbstractMetaItem] = {}
        self._get_plugins()

    @property
    def all_item_names(self) -> list[str]:

        return list(self.meta_items.keys())

    @property
    def all_items(self) -> list[META_ITEMS_TYPE]:
        return list(self.meta_items.values())

    def check_is_setup(self):
        if self.is_setup is False:
            raise NotSetupError(self)

    def _get_plugins(self):
        all_entry_points = entry_points()
        if ENTRY_POINT_NAME not in all_entry_points:
            return
        for plugin in all_entry_points[ENTRY_POINT_NAME]:
            try:
                loaded_plugin = plugin.load()
                loaded_plugin(self)
            except AttributeError as e:
                warn(f'plugin could not be loaded because of {e}.', stacklevel=4)

    def add_plugin_data(self, factory: AbstractMetaFactory) -> None:
        plugin_dict = {"product_name": factory.product_name,
                       "file": Path(inspect.getfile(factory)).resolve().as_posix(),
                       "module": inspect.getmodule(factory).__name__}
        self.plugin_data.append(plugin_dict)

    def register(self, factory: AbstractMetaFactory, default_configuration: dict[str, Any] = None) -> None:
        if self.is_setup is True:
            raise RegisterAfterSetupError(f'Unable to register new plug-ins after setting up {self.__class__.__name__!r}.')
        if not issubclass(factory, AbstractMetaFactory):
            raise TypeError(f"'factory' needs to be a subclass of {AbstractMetaFactory.__name__!r}.")

        self.factories.append(factory)
        default_configuration = {} if default_configuration is None else default_configuration
        default_configuration = factory.default_configuration | default_configuration

        self.default_base_configuration |= default_configuration
        self.add_plugin_data(factory=factory)

    def __getitem__(self, item_name) -> META_ITEMS_TYPE:
        self.check_is_setup()
        _out = self.meta_items.get(item_name, MiscEnum.NOTHING)
        if _out is MiscEnum.NOTHING:
            raise MetaItemNotFoundError(item_name, self.all_item_names)
        return _out

    def get(self, item_name: str = None) -> META_ITEMS_TYPE:
        if item_name is None:
            self.check_is_setup()
            return dict(self.meta_items)
        return self[item_name]

    def __contains__(self, item: Union[str, AbstractMetaItem]) -> bool:
        if isinstance(item, str):
            return item in self.all_item_names
        if isinstance(item, AbstractMetaItem):
            return item in self.all_items
        if isinstance(item, AbstractMetaFactory):
            return item in self.factories
        return NotImplemented

    def _initialize_data(self, config_kwargs: ConfigKwargs) -> None:
        factory_map = {factory.product_name: factory for factory in self.factories}
        for name in config_kwargs.get('to_initialize'):
            factory = factory_map.get(name, MiscEnum.NOTHING)
            if factory is MiscEnum.NOTHING:
                raise NoFactoryFoundError(name)
            meta_item = factory.build(config_kwargs)
            self.meta_items[factory.product_name] = meta_item
            config_kwargs.created_meta_items[factory.product_name] = meta_item

    def setup(self, init_path: PATH_TYPE, **kwargs) -> None:

        self._get_plugins()
        base_configuration = self.default_base_configuration.copy() | {'init_path': init_path}
        kwargs_to_initialize = kwargs.pop('to_initialize', [])
        if isinstance(kwargs_to_initialize, str):
            kwargs_to_initialize = [kwargs_to_initialize]
        to_initialize = self.default_to_initialize + kwargs_to_initialize + base_configuration.pop('to_initialize', [])
        base_configuration['to_initialize'] = to_initialize
        config_kwargs = ConfigKwargs(base_configuration=base_configuration, **kwargs)

        self._initialize_data(config_kwargs=config_kwargs)

        self.is_setup = True

    def clean_up(self, **kwargs) -> None:
        """
        possible kwargs:
            remove_all_paths: bool, default=False, remove all paths that were created by meta_paths
            dry_run:bool, default=False, only prints a message, and does not do actuall clean up
        """

        for item in self.all_items:
            try:
                item.clean_up(**kwargs)
            except AttributeError:
                warn(f"Meta-Item {item.name!r} has no Method named 'clean_up'.")


app_meta = AppMeta()


def setup_meta_data(init_path: PATH_TYPE, **kwargs) -> None:
    app_meta.setup(init_path=Path(init_path), **kwargs)


def get_meta_item(item_name: str = None) -> Union[dict[str, META_ITEMS_TYPE], META_ITEMS_TYPE]:
    return app_meta.get(item_name)


def get_meta_info() -> MetaInfo:
    return app_meta['meta_info']


def get_meta_paths() -> MetaPaths:
    return app_meta['meta_paths']


def get_meta_print() -> MetaPrint:
    return app_meta['meta_print']

    # region[Main_Exec]
if __name__ == '__main__':
    from faked_pack_src import call_and_return
    call_and_return(setup_meta_data)

# endregion[Main_Exec]
