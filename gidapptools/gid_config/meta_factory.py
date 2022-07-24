"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import json
import os
from typing import TYPE_CHECKING, Any, Union, Literal, Callable, Optional
from pathlib import Path
from weakref import WeakSet
from types import MethodType, FunctionType
import re
# * Third Party Imports --------------------------------------------------------------------------------->
import attr

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.helper import make_pretty
from gidapptools.gid_config.interface import GidIniConfig, BaseIniParser
from gidapptools.gid_config.parser.config_data import ConfigFile
from gidapptools.gid_config.conversion.spec_data import EntryTypus, SpecVisitor, SpecFile
from gidapptools.abstract_classes.abstract_meta_factory import AbstractMetaItem, AbstractMetaFactory
from gidapptools.gid_config.conversion.conversion_table import ConfigValueConversionTable
from gidapptools.errors import GidConfigError
# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.meta_data.config_kwargs import ConfigKwargs
    from gidapptools.meta_data.meta_info.meta_info_item import MetaInfo
    from gidapptools.meta_data.meta_paths.meta_paths_item import MetaPaths

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

CONFIG_SPEC_PAIRS_TYPE = dict[
    str, dict[
        Union[Literal["config_file"], Literal["spec_file"]], Path
    ]
]


class MetaVarReplacer:
    replace_regex = re.compile(r"%(?P<variable_name>[A-Z_][A-Z1-9_]*)%")

    def __init__(self, meta_info: "MetaInfo" = None, meta_paths: "MetaPaths" = None, **kwargs):
        self.meta_info = meta_info
        self.meta_paths = meta_paths
        self.other_replacements = dict(kwargs)

    def _replace_action(self, match: re.Match) -> str:
        var_name: str = match.group("variable_name")
        try:
            _out = str(self.other_replacements[var_name.casefold()])

        except KeyError:
            pass

        try:
            _out = str(getattr(self.meta_paths, var_name.casefold()))

            return _out
        except AttributeError:
            pass

        try:
            replacement = getattr(self.meta_info, var_name.casefold())
            if isinstance(replacement, (MethodType, FunctionType)):
                raise AttributeError(var_name)
            _out = str(replacement)

            return _out
        except AttributeError:
            pass

        try:
            _out = os.environ[var_name]

            return _out
        except KeyError:
            pass

        return f"%{var_name}%"

    def apply(self, text: str) -> str:
        return self.replace_regex.sub(self._replace_action, text)

    def __call__(self, text: str) -> str:
        return self.apply(text=text)


@attr.s(auto_attribs=True, auto_detect=True, kw_only=True)
class MetaConfig(AbstractMetaItem):
    config_dir: Path = attr.ib()
    specs: list[SpecFile] = attr.ib()
    meta_var_replacer: MetaVarReplacer = attr.ib()
    config_class: type = attr.ib(default=GidIniConfig)
    spec_file_class: type = attr.ib(default=SpecFile)
    config_file_class: type = attr.ib(default=ConfigFile)
    file_changed_parameter: str = attr.ib(default='size')
    instances: WeakSet[config_class] = WeakSet()

    def get_config(self, name: str) -> Optional[GidIniConfig]:
        spec = next((s for s in self.specs if s.name == name), None)
        if spec is None:
            raise GidConfigError(f"Unknown config_name {name!r}")
        config_file_path: Path = spec.get_config_path(self.meta_var_replacer)
        if config_file_path.exists() is False and spec.config_file_creation_settings.create_if_missing is True:
            config_file_path.parent.mkdir(exist_ok=True, parents=True)
            config_file_path.touch(exist_ok=True)

        config = ConfigFile(file_path=config_file_path, parser=BaseIniParser())
        if spec.config_file_creation_settings.fill_with_defaults is True:
            ...

        _out = GidIniConfig(spec_file=spec, config_file=config)

        self.instances.add(_out)
        return _out

    def add_spec_value_handler(self, target_name: str, handler: Callable[[Any, list[Any]], EntryTypus]) -> None:
        SpecVisitor.add_handler(target_name=target_name, handler=handler)
        for config in self.instances:
            config.spec.reload()

    def add_converter_function(self, typus: Any, converter_function: Callable) -> None:
        ConfigValueConversionTable.add_extra_dispatch(typus, converter_function)

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    def reset(self, config_name: str = None):
        paths_to_clear = set()
        if config_name is None:
            paths_to_clear = {s.get_config_path(self.meta_var_replacer) for s in self.specs} + set(s.file_path for s in self.specs)

        else:
            paths_to_clear = {s.get_config_path(self.meta_var_replacer) for s in self.specs if s.name == config_name} + set(s.file_path for s in self.specs if s.name == config_name and s.spec_name)

        for path in paths_to_clear:
            path.unlink(missing_ok=True)

    def clean_up(self, **kwargs) -> None:
        pass

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:

        if pretty is True:
            return make_pretty(self)
        return attr.asdict(self)


class MetaConfigFactory(AbstractMetaFactory):
    product_class = MetaConfig
    default_configuration = {}

    def __init__(self, config_kwargs: "ConfigKwargs") -> None:
        super().__init__(config_kwargs=config_kwargs)
        self.config_dir: Path = config_kwargs.get("config_dir")
        self.spec_dir: Path = config_kwargs.get("config_spec_dir")
        self.config_paths: list[Path] = []
        self.specs: list["SpecFile"] = []

    def _dev_init(self) -> None:
        self.config_dir: Path = self.config_kwargs.get("code_base_dir").joinpath("dev_temp", "config")
        self.spec_dir: Path = self.config_kwargs.get("code_base_dir").joinpath("dev_temp", "config", "spec")

    def setup(self) -> None:
        if self.config_kwargs.get('is_dev', False) is True:
            self._dev_init()

        self.spec_dir.mkdir(exist_ok=True, parents=True)
        self.config_dir.mkdir(exist_ok=True, parents=True)

        for file in self.spec_dir.iterdir():
            if file.is_file() is False or file.suffix != '.spec':
                continue
            spec = SpecFile(file, visitor=SpecVisitor())
            if spec.name not in {s.name for s in self.specs}:
                self.specs.append(spec)

        for spec_file in self.config_kwargs.get("spec_files", []):
            spec = SpecFile(spec_file, visitor=SpecVisitor())
            if spec.name not in {s.name for s in self.specs}:
                self.specs.append(spec)

    def _build(self) -> AbstractMetaItem:
        if self.is_setup is False:
            self.setup()
        if self.config_kwargs.get('is_dev', False) is True:
            meta_var_replacer = MetaVarReplacer(meta_info=self.config_kwargs.created_meta_items["meta_info"], meta_paths=self.config_kwargs.created_meta_items["meta_paths"], config_dir=self.config_dir)
        else:
            meta_var_replacer = MetaVarReplacer(meta_info=self.config_kwargs.created_meta_items["meta_info"], meta_paths=self.config_kwargs.created_meta_items["meta_paths"])
        kwargs = self.config_kwargs.get_kwargs_for(self.product_class, defaults={"config_paths": self.config_paths, "specs": self.specs, "meta_var_replacer": meta_var_replacer})
        return self.product_class(**kwargs)

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
