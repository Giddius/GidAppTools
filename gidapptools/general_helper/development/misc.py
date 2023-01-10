"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Any, Literal, Callable, Optional
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import MissingOptionalDependencyError

with MissingOptionalDependencyError.try_import("gidapptools"):
    from rich import inspect as rinspect
    from rich import terminal_theme
    from rich.console import Console as RichConsole

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def make_dprint(**console_kwargs) -> Callable:
    use_seperator: bool = console_kwargs.pop('use_seperator', True)
    seperator_char: str = console_kwargs.pop('seperator_char', '-')
    use_print_count: bool = console_kwargs.pop('use_print_count', True)

    extra_newline: bool = console_kwargs.pop('extra_newline', True)

    prefix: Optional[str] = console_kwargs.pop('prefix', None)

    console_kwargs = {'soft_wrap': True} | console_kwargs
    console = RichConsole(**console_kwargs)
    print_count = 0

    convert_table = {'odict_keys': list, }

    def _convert_stupid_fake_iterables(in_object: Any):
        try:
            if in_object.__class__.__name__ in convert_table:
                return convert_table.get(in_object.__class__.__name__)(in_object)
        except Exception:
            return in_object
        return in_object

    def _dprint(*args, **kwargs) -> None:
        nonlocal print_count
        print_count += 1
        if use_seperator is True:
            title = "" if use_print_count is False else f"Output No.{print_count}"
            console.rule(title=title, characters=seperator_char)
        if extra_newline is True:
            kwargs['end'] = '\n\n'
        if prefix:
            console.print(prefix, end='')
        args = list(map(_convert_stupid_fake_iterables, args))
        console.print(*args, **kwargs)

    return _dprint


dprint = make_dprint()


def obj_inspection(obj: object, out_dir: Path = None, out_type: Literal["txt", "html"] = 'html', width: int = None, theme: terminal_theme.TerminalTheme = None, **rinspect_kwargs) -> None:
    console = RichConsole(soft_wrap=True, record=True)
    theme = theme or terminal_theme.MONOKAI
    rinspect_kwargs = {"methods": True, "help": True, "private": True} | rinspect_kwargs
    rinspect(obj=obj, console=console, **rinspect_kwargs)
    out_dir = Path.cwd() if out_dir is None else Path(out_dir)

    name = obj.__qualname__ or obj.__name__
    try:
        name = obj.__qualname__ or obj.__name__
    except AttributeError:
        name = obj.__name__

    out_file = out_dir.joinpath(f"{name}.{out_type}")
    if out_type == "html":
        console.save_html(out_file, theme=theme)
    elif out_type == "txt":
        console.save_text(out_file)


def is_dunder_name(in_name: str) -> bool:
    return in_name.startswith("__") and in_name.endswith("__")


    # region [Main_Exec]
if __name__ == '__main__':
    from PySide6.QtWidgets import QMenu
    obj_inspection(QMenu)

# endregion [Main_Exec]
