"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import ast
import json
import inspect
import pkgutil
from types import ModuleType
from typing import Any, Union, Optional
from pathlib import Path
from collections import namedtuple, OrderedDict
from importlib import import_module
from importlib.metadata import metadata, distributions
from collections.abc import Iterable
from sortedcontainers import SortedDict
import importlib.util
from importlib.abc import MetaPathFinder, PathEntryFinder
# * Third Party Imports --------------------------------------------------------------------------------->
import attrs

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import MissingOptionalDependencyError
from gidapptools.general_helper.development.misc import is_dunder_name
with MissingOptionalDependencyError.try_import("gidapptools"):
    import isort

try:
    import rich
    from rich.console import Console as RichConsole, ConsoleOptions, RenderResult
    from rich.table import Table
    from rich.rule import Rule
    from rich.segment import Segment
    from rich.tree import Tree
    from rich.region import Region
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.columns import Columns
    from rich.bar import Bar
    from rich.style import Style
    from rich.align import Align
    from rich.containers import Renderables, Lines
    RICH_IMPORTABLE = True

except ImportError:
    RICH_IMPORTABLE = False


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ClassNameFinder(ast.NodeVisitor):

    def __init__(self) -> None:
        super().__init__()
        self.class_names: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.class_names.append(node.name)
        self.generic_visit(node)

    def get_unique_class_names(self) -> tuple[str]:
        class_names = set(self.class_names)
        return tuple(sorted(class_names, key=lambda x: (not x.startswith("Q"), x.casefold())))


@attrs.define(frozen=True, slots=True)
class SubModule:
    name: str
    qualname: str
    package: str
    module_info: pkgutil.ModuleInfo = attrs.field(default=None)

    @classmethod
    def from_module_info(cls, in_module_info: pkgutil.ModuleInfo) -> "SubModule":
        name = in_module_info.name.split('.')[-1]
        qualname = in_module_info.name
        package = in_module_info.name.split('.')[0]

        return cls(name=name, qualname=qualname, module_info=in_module_info, package=package)

    @property
    def full_name(self) -> str:
        return self.module.__name__

    @property
    def path(self) -> Optional[Path]:
        try:
            path = self.module.__file__
            if path is not None:
                return Path(path)
        except AttributeError:
            return None

    @property
    def is_top_module(self) -> bool:
        return False

    @property
    def dunder_names(self) -> tuple[str]:
        exclude_names = {"__builtins__"}
        return tuple(name for name in dir(self.module) if is_dunder_name(name) is True and name not in exclude_names)

    @property
    def doc(self) -> str:
        doc = self.module.__doc__
        if doc is None and self.path.suffix == ".pyd":
            typing_file = self.path.with_suffix(".pyi")
            if typing_file.is_file() is True:
                tree = ast.parse(typing_file.read_text(encoding='utf-8', errors='ignore'))
                doc = ast.get_docstring(tree)

        if doc is not None:
            doc = inspect.cleandoc(doc)
        return doc

    @property
    def meta_data(self) -> dict[str, Any]:
        return dict(metadata(self.package))

    @property
    def module(self) -> ModuleType:
        return import_module(self.qualname, self.package)

    @property
    def import_string(self) -> str:
        import_path = self.qualname.rsplit('.', 1)[0]
        return f"from {import_path} import {self.name}"

    @property
    def all_members_import_string(self) -> str:
        text = f"from {self.qualname} import ({', '.join(self.member_names)})"

        return isort.code(text, line_length=200).strip()

    @property
    def member_names(self) -> tuple[str]:

        def _check(_name: str, _obj: object) -> bool:
            return not any([
                getattr(_obj, "__module__", None) != self.module.__name__,
                inspect.ismodule(_obj),
                inspect.isbuiltin(_obj),
                _name.startswith("_"),
                _name.endswith("__")
            ])

        def _sort_key(in_name: str) -> tuple:
            norm_name = in_name.casefold()
            has_upper_q_prefix = in_name.startswith("Q")
            has_lower_q_prefix = in_name.startswith("q")

            return (not has_upper_q_prefix, not has_lower_q_prefix, norm_name, len(norm_name))

        _out = set()
        for name, obj in inspect.getmembers(self.module):
            if _check(name, obj) is False:
                continue

            _out.add(name)

        return tuple(sorted(_out, key=_sort_key))

    def to_dict(self, for_json: bool = False) -> dict[str, Any]:

        def _std_serialize(inst: "SubModule", field_name: str, value: Any) -> Any:
            match value:
                case pkgutil.ModuleInfo:
                    raise RuntimeError("Module info should not hit this")
            return value

        def _json_serialize(inst: "SubModule", field_name: str, value: Any) -> Any:
            match value:

                case Path():
                    return value.as_posix()

                case float():
                    return str(value)

                case tuple():
                    return [_json_serialize(inst, field_name, i) for i in value]

                case set():
                    return [_json_serialize(inst, field_name, i) for i in value]

                case str():
                    return value

                case list():
                    return [_json_serialize(inst, field_name, i) for i in value]

                case dict():
                    return {_json_serialize(inst, field_name, k): _json_serialize(inst, field_name, v) for k, v in value.items()}

                case int():
                    return value

                case None:
                    return value

                case _:
                    return str(value)

        def _filter(field_name: str, value: Any) -> bool:
            match field_name:
                case "module_info":
                    return False

                case "module":
                    return False

            return True

        def _result_sorting_key(name_value: tuple[str, object]) -> Optional[int]:
            fixed_order = ("name",
                           "qualname",
                           "package",
                           "doc")
            try:
                pos = fixed_order.index(name_value[0])
            except ValueError:
                if isinstance(name_value[1], str):
                    pos = 1_000
                elif isinstance(name_value[1], Path):
                    pos = 2_000
                elif isinstance(name_value[1], Iterable):
                    pos = 3_000
                else:
                    pos = 10_000
            return pos

        _out = {}

        attrs_attribute_names = [field.name for field in attrs.fields(self.__class__)]
        extra_attribute_names = ["path", "doc", "module", "import_string", "all_members_import_string", "member_names", "dunder_names"]

        attribute_names = attrs_attribute_names + extra_attribute_names

        _serialize = _std_serialize if for_json is False else _json_serialize

        for name in attribute_names:
            value = getattr(self, name)
            if _filter(name, value) is False:
                continue
            serialized_value = _serialize(self, name, value)
            _out[name] = serialized_value
        return {k: v for k, v in sorted(_out.items(), key=_result_sorting_key)}


class TopModule(SubModule):

    @property
    def is_top_module(self) -> bool:
        return True


class PackageInfoData:

    def __init__(self, module: ModuleType) -> None:
        self._sub_modules_data: dict[str, "SubModule"] = dict()
        self._top_module_data: "TopModule" = TopModule.from_module_info(pkgutil.ModuleInfo(pkgutil.find_loader(module.__name__), module.__name__, getattr(module, "__path__", None) is not None))

    @property
    def top_module_data(self) -> TopModule:
        return self._top_module_data

    @property
    def name(self) -> str:
        return self.top_module_data.full_name

    def _insert_item(self, item: SubModule):
        if item.name != item.full_name:
            top_name = (self.name.rsplit(".", 1)[0] + ".") if "." in self.name else ""
            new_key = item.full_name.replace(top_name, "")
            self._sub_modules_data[new_key] = item
        else:
            self._sub_modules_data[item.name] = item

    def append(self, item: "SubModule") -> None:
        self._insert_item(item)
        self._sort_sub_modules()

    def add(self, items: Iterable["SubModule"]) -> None:
        for item in items:
            self._insert_item(item)
        self._sort_sub_modules()

    def _sort_key_func(self, in_item_tuple: tuple[str, "SubModule"]) -> tuple[bool, str, int]:
        return (in_item_tuple[0].startswith("_"), in_item_tuple[1].qualname, len(in_item_tuple[1].qualname.split(".")))

    def _sort_sub_modules(self) -> None:
        self._sub_modules_data = dict(sorted(self._sub_modules_data.items(), key=self._sort_key_func))

    def __iter__(self):
        return iter([self.top_module_data] + list(self._sub_modules_data.values()))

    def __getitem__(self, name: str) -> "SubModule":
        if name == self.top_module_data.name:
            return self.top_module_data

        return self._sub_modules_data[name]

    def to_dict(self, for_json: bool = False) -> list[dict[str, Any]]:
        return [i.to_dict(for_json=for_json) for i in ([self.top_module_data] + list(self._sub_modules_data.values()))]

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}({self.name!r}, sub_modules={list(self._sub_modules_data.keys())!r})"


def get_all_sub_modules(in_module: ModuleType) -> PackageInfoData:
    module_data = PackageInfoData(in_module)

    try:
        module_path = in_module.__path__
        module_prefix = in_module.__package__ + "."

        for info in pkgutil.walk_packages(module_path, module_prefix):
            sub_module = SubModule.from_module_info(info)
            module_data.append(sub_module)

    except AttributeError:
        pass
    return module_data


def get_all_sub_module_data(in_module: ModuleType, for_json: bool = False) -> list[dict[str, object]]:
    return get_all_sub_modules(in_module).to_dict(for_json=for_json)


def print_all_sub_module_data(in_module: ModuleType, no_rich: bool = False) -> None:

    if no_rich is True or RICH_IMPORTABLE is False:
        from pprint import pprint
        pprint(get_all_sub_module_data(in_module=in_module))
        return

    console = RichConsole(soft_wrap=True)
    console.print(get_all_sub_module_data(in_module))


# region[Main_Exec]
if __name__ == '__main__':
    from PySide6 import QtWidgets
    print_all_sub_module_data(QtWidgets)

# endregion[Main_Exec]
