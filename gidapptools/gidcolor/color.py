"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Iterable, Optional, Union, Protocol, Callable, TypeAlias, TypeGuard, TypedDict, NamedTuple, TypeVar, TypeVarTuple, TYPE_CHECKING
from pathlib import Path
import numpy as np
from abc import ABC, abstractmethod
from colorsys import hsv_to_rgb, rgb_to_hls, rgb_to_hsv, hls_to_rgb
from functools import partial
import random
from copy import copy
from enum import Enum, auto, Flag
import scipy
from gidapptools.errors import MissingOptionalDependencyError

from math import radians, degrees, ceil, floor

import sys
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
try:
    from PySide6.QtGui import QColor
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

if TYPE_CHECKING:
    from PySide6.QtGui import QColor
# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

RGB_FLOAT_TO_INT_FACTOR: float = 1.0 / 255
# endregion [Constants]

# region [Types]

_FLOAT_COLOR_VALUE: TypeAlias = tuple[float, float, float]

_FLOAT_COLOR_W_ALPHA_VALUE: TypeAlias = tuple[float, float, float, float]

_INT_COLOR_VALUE: TypeAlias = tuple[int, int, int]

_INT_COLOR_W_ALPHA_VALUE: TypeAlias = tuple[int, int, int, float]

# endregion [Types]


def rgb_to_hsl(r: float, g: float, b: float) -> tuple[float, float, float]:
    h, l, s = rgb_to_hls(r, g, b)
    return h, s, l


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[float, float, float]:
    return hls_to_rgb(h, l, s)


def rgb_float_to_rgb_int(in_rgb_float: tuple[float]) -> tuple[int]:
    return tuple(round(255 * i) for i in in_rgb_float)


def rgb_int_to_rgb_float(in_rgb_int: tuple[float]) -> tuple[int]:
    return tuple(float(i / 255) for i in in_rgb_int)


def rgb_float_to_hex(in_rgb_float: tuple[float]) -> str:
    values = rgb_float_to_rgb_int(in_rgb_float)
    return '#' + ''.join(f"{p:02X}" for p in values)


def hex_to_rgb_float(in_hex: str) -> tuple[float]:
    cleaned_hex = in_hex.removeprefix("#")
    rgb_int_values = tuple(bytes.fromhex(cleaned_hex))
    return rgb_int_to_rgb_float(rgb_int_values)


def standard_string_format(color: "Color", with_alpha: bool = True) -> str:
    return str(color)


def hex_string_format(color: "Color", with_alpha: bool = True) -> str:

    return rgb_float_to_hex(color.internal_value[:3 + int(with_alpha)])


def _clamp_float(in_float: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, in_float))


def _clamp_between_zero_one(in_float: float) -> float:
    return _clamp_float(in_float=in_float, minimum=0.0, maximum=1.0)


def percent_float_to_degrees(in_value: float) -> float:
    return (in_value * 360) % 360


def degrees_to_percent_float(in_value: float) -> float:
    return (in_value / 360) % 1.0


class Color:
    __slots__ = ("_rgb",
                 "_hsv",
                 "_hsl",
                 "_alpha",
                 "_rgb_int",
                 "_hex",
                 "_qcolor",
                 "_is_frozen")

    def __init__(self,
                 rgb: _FLOAT_COLOR_VALUE,
                 hsv: _FLOAT_COLOR_VALUE,
                 hsl: _FLOAT_COLOR_VALUE,
                 rgb_int: _INT_COLOR_VALUE,
                 alpha: float = 1.0) -> None:

        self._rgb = np.asarray(tuple(_clamp_between_zero_one(i) for i in rgb), dtype=np.float16)
        self._hsv = np.asarray(tuple(_clamp_between_zero_one(i) for i in hsv), dtype=np.float16)
        self._hsl = np.asarray(tuple(_clamp_between_zero_one(i) for i in hsl), dtype=np.float16)
        self._alpha = alpha
        self._rgb_int = rgb_int

        # lazy optional values
        self._hex: str = '#' + ''.join(f"{p:02X}" for p in (self._rgb_int + (round(self._alpha * 255),)))

        if PYSIDE6_AVAILABLE is True:
            self._qcolor: Optional["QColor"] = None

    @property
    def alpha(self) -> float:
        return self._alpha

    @property
    def rgb(self) -> _FLOAT_COLOR_VALUE:
        return tuple(self._rgb)

    @property
    def rgba(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        return tuple(self._rgb) + (self._alpha,)

    @property
    def hsv(self) -> _FLOAT_COLOR_VALUE:
        return tuple(self._hsv)

    @property
    def hsva(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        return tuple(self._hsv) + (self._alpha,)

    @property
    def hsl(self) -> _FLOAT_COLOR_VALUE:
        return tuple(self._hsl)

    @property
    def hsla(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        return tuple(self._hsl) + (self._alpha,)

    @property
    def rgb_int(self) -> _INT_COLOR_VALUE:
        return tuple(self._rgb_int)

    @property
    def rgba_int(self) -> _INT_COLOR_W_ALPHA_VALUE:
        return tuple(self._rgb_int) + (self._alpha,)

    @property
    def hex(self) -> str:
        return self._hex

    @property
    def qcolor(self) -> "QColor":
        if PYSIDE6_AVAILABLE is False:
            raise MissingOptionalDependencyError("PySide6", "gidapptools")

        if self._qcolor is None:
            self._qcolor = QColor.fromRgbF(*self._rgb, self._alpha)

        return self._qcolor

    @classmethod
    def from_rgb(cls, r: float, g: float, b: float, alpha: float = 1.0) -> Self:

        rgb_value = tuple(_clamp_between_zero_one(i) for i in (r, g, b))

        return cls(rgb=rgb_value,
                   rgb_int=tuple(round(255 * i) for i in rgb_value),
                   hsv=rgb_to_hsv(*rgb_value),
                   hsl=rgb_to_hsl(*rgb_value),
                   alpha=alpha)

    @classmethod
    def from_rgb_int(cls, r: int, g: int, b: int, alpha: float = 1.0) -> Self:
        r_float, g_float, b_float = rgb_int_to_rgb_float((r, g, b))
        return cls.from_rgb(r=r_float,
                            g=g_float,
                            b=b_float,
                            alpha=alpha)

    @classmethod
    def from_hsl(cls, h: float, s: float, l: float, alpha: float = 1.0) -> Self:
        return cls.from_rgb(*hsl_to_rgb(h, s, l), alpha=alpha)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float, alpha: float = 1.0) -> Self:
        return cls.from_rgb(*hsv_to_rgb(h, s, v), alpha=alpha)

    @classmethod
    def from_hex(cls, value: str) -> Self:
        rgb_int_values = tuple(bytes.fromhex(value.removeprefix("#")))
        if len(rgb_int_values) == 4:
            rgb_int_values = (*rgb_int_values[:-1], float(rgb_int_values[-1] / 255))

        return cls.from_rgb_int(*rgb_int_values)

    @classmethod
    def from_qcolor(cls, value: "QColor") -> Self:
        instance = cls.from_rgb(*value.getRgbF())
        instance._qcolor = value
        return instance

    def get_complementary_color(self) -> Self:
        new_hsl = ((self.hsl[0] + 0.5) % 1.0, self.hsl[1], self.hsl[2], self.alpha)

        return self.__class__.from_hsl(*new_hsl)

    def as_string(self) -> str:
        ...

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.rgba == other.rgba

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._rgb) + hash(self._hsv) + hash(self._hsl) + hash(self._rgb_int) + hash(self._alpha)

    def __format__(self, format_spec: str) -> str:
        ...

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(rgb={self._rgb!r}, hsv={self._hsv!r}, hsl={self._hsl}, rgb_int={self._rgb_int}, alpha={self._alpha})'
# region [Main_Exec]


def float_to_degrees(in_value: float) -> float:
    return (in_value * 360) % 360


if __name__ == '__main__':
    x = Color.from_rgb(0.5, 0.5, 0.5)
    y = x.get_complementary_color()

    print(f"{x.hsla=}")
    print(f"{y.hsla=}")
    print(f"{x.rgb=}")
    z = QColor.fromRgb(128, 128, 128, 255)
    print(f"{z.getRgb()=}")
    print(f"{z.getRgbF()=}")
    uu = z.convertTo(QColor.Spec.Hsl)
    print(f"{uu=}")
    print(f"{uu.getRgb()=}")

    print(f"{z.getHsvF()=}")


# endregion [Main_Exec]
