"""
Config-Parser that auto-converts values based on an extra configspec file.

currently available:
    - ini, comment-preserving
"""


from .interface import get_config
import sys
from typing import TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, Protocol, runtime_checkable, NoReturn, NewType, Literal, AnyStr, IO, BinaryIO, TextIO, Any
from collections.abc import Hashable, Iterable, Mapping, Sequence, MutableMapping, MutableSet, MutableSequence, Callable, Generator, Collection, Container, Coroutine
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
