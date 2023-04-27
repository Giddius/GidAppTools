"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
import random
from typing import Any, Union, TypeVar, Callable, Hashable, Iterable, Optional, Generator
from logging import Logger
from pathlib import Path
from itertools import tee, filterfalse


# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import MiscEnum

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

T = TypeVar("T")
_DEFAULT_TYPE = TypeVar("_DEFAULT_TYPE", object, None)


def defaultable_list_pop(in_list: Optional[list[T]], idx: int, default: _DEFAULT_TYPE = None) -> Union[T, _DEFAULT_TYPE]:
    if in_list is None:
        return default
    try:
        return in_list.pop(idx)
    except IndexError:
        return default


T = TypeVar("T")
IN_ITERABLE_TYPE = Iterable[T]
CHECK_FUNC_TYPE = Callable[[object], bool]


class _IterSplitter:
    __slots__ = ("output_type_strategies",)

    def __init__(self) -> None:
        self.output_type_strategies: dict[type, Callable[[IN_ITERABLE_TYPE, CHECK_FUNC_TYPE], tuple[Iterable[T], Iterable[T]]]] = {list: self._output_lists,
                                                                                                                                   set: self._output_sets,
                                                                                                                                   tuple: self._output_tuples,
                                                                                                                                   Generator: self._output_generators}

    def _output_lists(self, in_iterable: Iterable[T], check_func: Callable[[object], bool]) -> tuple[list[T], list[T]]:
        check_true_items = []
        check_false_items = []
        for item, check_result in ((i, check_func(i)) for i in in_iterable):

            if check_result is True:
                check_true_items.append(item)
            elif check_result is False:
                check_false_items.append(item)
            else:
                raise TypeError(f"check_func {check_func!r} returned a non-bool result {check_result!r}")

        return check_true_items, check_false_items

    def _output_sets(self, in_iterable: Iterable[T], check_func: Callable[[object], bool]) -> tuple[set[T], set[T]]:
        check_true_items, check_false_items = self._output_lists(in_iterable=in_iterable, check_func=check_func)
        return set(check_true_items), set(check_false_items)

    def _output_tuples(self, in_iterable: Iterable[T], check_func: Callable[[object], bool]) -> tuple[tuple[T], tuple[T]]:
        check_true_items, check_false_items = self._output_lists(in_iterable=in_iterable, check_func=check_func)
        return tuple(check_true_items), tuple(check_false_items)

    def _output_generators(self, in_iterable: Iterable[T], check_func: Callable[[object], bool]) -> tuple[Generator[T, None, None], Generator[T, None, None]]:
        t1, t2 = tee(in_iterable)
        return (i for i in filter(check_func, t2)), (i for i in filterfalse(check_func, t1))

    def _determine_output_type(self, in_iterable: Iterable[T]) -> Union[type[list], type[tuple], type[set], type[Generator]]:
        if isinstance(in_iterable, set):
            return set

        elif isinstance(in_iterable, tuple):
            return tuple

        elif isinstance(in_iterable, list):
            return list

        elif isinstance(in_iterable, Generator):
            return Generator

    def __call__(self, in_iterable: Iterable[T], check_func: Callable[[object], bool], output_type: Union[type[list], type[tuple], type[set], type[Generator], None] = None):
        if output_type is None:
            output_type = self._determine_output_type(in_iterable=in_iterable)

        strategy = self.output_type_strategies[output_type]
        return strategy(in_iterable=in_iterable, check_func=check_func)


split_iter = _IterSplitter()


def dict_pop_fallback(in_dict: dict, keys: Union[Iterable[Hashable], Hashable], default: Any = None) -> Any:
    for key in keys:
        value = in_dict.pop(key, MiscEnum.NOT_FOUND)
        if value is not MiscEnum.NOT_FOUND:
            return value
    return default


def is_frozen() -> bool:
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_all_available_loggers(logger: Logger = None) -> tuple[str]:
    manager = logger.manager if logger is not None else Logger.manager
    names = set(manager.loggerDict)
    return tuple(sorted(names, key=len))


T = TypeVar("T")


def iter_grouped(in_iterable: Iterable[T], group_size: int = 2) -> Generator[tuple[T, ...], None, None]:
    sentinel = object()
    _iterator = iter(in_iterable)
    collected = []
    while True:
        next_item = next(_iterator, sentinel)
        if next_item is sentinel:
            break

        collected.append(next_item)
        if len(collected) == group_size:
            yield tuple(collected)
            collected.clear()

    if len(collected) != 0:
        yield tuple(collected)

# region [Main_Exec]


if __name__ == '__main__':
    # from gidapptools.general_helper.timing import time_execution

    # def checker(in_num: int) -> bool:
    #     return len(in_num) == 2

    # t = [str(random.randint(0, 1_000)) for _ in range(10_000)]

    # with time_execution(also_pretty=True):
    #     a, b = split_iter(t, checker, Generator)
    #     for xx in a:
    #         print(xx)
    for l in get_all_available_loggers():
        print(l)

# endregion [Main_Exec]
