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

from functools import partial
import random
from copy import copy
from decimal import Decimal
from enum import Enum, auto, Flag

from gidapptools.errors import MissingOptionalDependencyError
from gidapptools.gidcolor.misc_calculations import calculate_contrast_ratio
from math import radians, degrees, ceil, floor, sqrt
from functools import total_ordering
import sys


from gidapptools.gidcolor.coversion import hsv_to_rgb, rgb_to_hsv, rgb_int_to_rgb_float, rgb_to_hsl, hsl_to_rgb

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


def _clamp_float(in_float: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, in_float))


def _clamp_between_zero_one(in_float: float) -> float:
    return _clamp_float(in_float=in_float, minimum=0.0, maximum=1.0)


def percent_float_to_degrees(in_value: float) -> float:
    return (in_value * 360) % 360


def degrees_to_percent_float(in_value: float) -> float:
    return (in_value / 360) % 1.0


def truncate_float(value: float, ndigits: int) -> float:
    float_string = str(value)
    pre_comma, post_comma = float_string.split(".")
    return float(pre_comma + '.' + post_comma[:ndigits])


class BasicFormat(Enum):
    DEFAULT = auto()

    RGB = auto()
    HSV = auto()
    HSL = auto()

    RGB_INT = auto()

    HEX = auto()

    CSS = auto()

    @classmethod
    def from_string(cls, in_string: str) -> Self:
        in_string = in_string.casefold()
        for name, member in cls._member_map_.items():
            if name.casefold() == in_string:
                return member

        raise ValueError(f"No Member with name {in_string!r}.")


@total_ordering
class Color:

    light_dark_factor_threshold: float = 127.5

    __slots__ = ("_rgb",
                 "_hsv",
                 "_hsl",
                 "alpha",
                 "_qcolor")

    def __init__(self,
                 rgb: _FLOAT_COLOR_VALUE,
                 hsv: _FLOAT_COLOR_VALUE,
                 hsl: _FLOAT_COLOR_VALUE,
                 alpha: float = 1.0) -> None:

        self._rgb: np.ndarray
        self._hsl: np.ndarray
        self._hsv: np.ndarray

        super().__setattr__("_rgb", np.asarray([_clamp_between_zero_one(i) for i in rgb], dtype=np.float32))
        super().__setattr__("_hsv", np.asarray([_clamp_between_zero_one(i) for i in hsv], dtype=np.float32))
        super().__setattr__("_hsl", np.asarray([_clamp_between_zero_one(i) for i in hsl], dtype=np.float32))

        self.alpha: float

        super().__setattr__("alpha", alpha)
        super().__setattr__("_qcolor", None)

    @property
    def rgb(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        return tuple(self._rgb.tolist())

    @property
    def rgba(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        return tuple(self._rgb.tolist()) + (self.alpha,)

    @property
    def hsv(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        return tuple(self._hsv.tolist())

    @property
    def hsva(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        return tuple(self._hsv.tolist()) + (self.alpha,)

    @property
    def hsl(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        return tuple(self._hsl.tolist())

    @property
    def hsla(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        return tuple(self._hsl.tolist()) + (self.alpha,)

    @property
    def hls(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        hsl = self.hsl
        return (hsl[0], hsl[2], hsl[1])

    @property
    def hlsa(self) -> _FLOAT_COLOR_W_ALPHA_VALUE:
        hsl = self.hsl
        return (hsl[0], hsl[2], hsl[1]) + (self.alpha,)

    @property
    def rgb_int(self) -> _INT_COLOR_VALUE:
        return tuple(round(i * 255) for i in self._rgb)

    @property
    def rgba_int(self) -> _INT_COLOR_W_ALPHA_VALUE:
        return tuple(round(i * 255) for i in self._rgb) + (self.alpha,)

    @property
    def hex(self) -> str:
        return '#' + ''.join(f"{p:02X}" for p in (self.rgb_int + (round(self.alpha * 255),)))

    @property
    def hex_no_alpha(self) -> str:
        return '#' + ''.join(f"{p:02X}" for p in self.rgb_int)

    @property
    def qcolor(self) -> "QColor":
        if PYSIDE6_AVAILABLE is False:
            raise MissingOptionalDependencyError("PySide6", "gidapptools")

        if self._qcolor is None:
            super().__setattr__("_qcolor", QColor.fromRgbF(*self._rgb, a=self._alpha))

        return self._qcolor

    @property
    def hue(self) -> float:
        return float(self.hsv[0])

    @property
    def hue_degrees(self) -> float:
        return round(percent_float_to_degrees(self.hsv[0]), ndigits=3)

    @classmethod
    def from_rgb(cls, r: float, g: float, b: float, alpha: float = 1.0) -> Self:
        rgb_value = (r, g, b)
        return cls(rgb=rgb_value,
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
        v = hsl_to_rgb(h, s, l)

        return cls.from_rgb(*v, alpha=alpha)

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
        if PYSIDE6_AVAILABLE is False:
            raise MissingOptionalDependencyError("PySide6", "gidapptools")
        instance = cls.from_rgb(*value.getRgbF())
        super(cls, instance).__setattr__("_qcolor", value)
        return instance

    def get_complementary_color(self) -> Self:
        old_hsl = self.hsl
        new_hsl = ((old_hsl[0] + 0.5), old_hsl[1], old_hsl[2])

        return self.__class__.from_hsl(*new_hsl, alpha=self.alpha)

    def contrast_ratio(self, other_color: Self) -> float:
        return calculate_contrast_ratio(self.rgb, other_color.rgb)

    def determine_light_dark_factor(self) -> float:
        r, g, b = self.rgb_int
        return sqrt((0.299 * (r * r)) + (0.587 * (g * g)) + (0.114 * (b * b)))

    @property
    def is_light(self) -> bool:
        return self.determine_light_dark_factor() > self.light_dark_factor_threshold

    @property
    def is_dark(self) -> bool:
        return self.determine_light_dark_factor() < self.light_dark_factor_threshold

    def as_string(self, string_format: BasicFormat = BasicFormat.DEFAULT, with_alpha: bool = True) -> str:

        if string_format in {BasicFormat.RGB, BasicFormat.HSL, BasicFormat.HSV, BasicFormat.RGB_INT}:
            attr_name = string_format.name.casefold()
            if with_alpha is True:
                attr_name += "a"

            return str(getattr(self, attr_name))

        if string_format is BasicFormat.CSS:
            if with_alpha is True:
                return f"rgba{self.rgba_int!s}"
            else:
                return f"rgb{self.rgb_int!s}"

        if string_format is BasicFormat.HEX:
            if with_alpha is True:
                return str(self.hex)
            else:
                return str(self.hex_no_alpha)

        return str(self)

    def as_pillow_color_value(self) -> tuple[int, int, int, int]:
        return self.rgb_int + (round(self.alpha * 255),)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Color):
            return self._rgb == other._rgb and self.alpha == other.alpha

        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Color):
            return sum(self.rgba) < sum(other.rgba)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._rgb) + hash(self._hsv) + hash(self._hsl) + hash(self.alpha)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"Unable to set {name!r} to {value!r} for {self!r} as instances of {self.__class__.__name__!r} are immutable.")

    def __format__(self, format_spec: str) -> str:
        with_alpha = None
        if format_spec.startswith(("+a", "-a")):
            with_alpha = format_spec[0] == "+"
            format_spec = format_spec[2:]

        elif format_spec.endswith(("+a", "-a")):
            with_alpha = format_spec[-2] == "+"
            format_spec = format_spec[:-2]

        string_format = BasicFormat.from_string(format_spec)

        return self.as_string(*(i for i in (string_format, with_alpha) if i is not None))

    def __repr__(self) -> str:
        # return f'{self.__class__.__name__}(rgb={self.rgb!r}, hsv={self.hsv!r}, hsl={self.hsl!r}, alpha={self.alpha!r})'
        return f'{self.__class__.__name__}({self.hex!r})'


# region [Main_Exec]


if __name__ == '__main__':
    x = Color.from_hex("#556B2F")
    print(type(x.rgb[0]))

    print(x.hue_degrees)
    print(x)


# endregion [Main_Exec]
