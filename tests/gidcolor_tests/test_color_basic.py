# region [Imports]

import pytest
from pytest import param
from pytest_lazyfixture import lazy_fixture

from pathlib import Path
from gidapptools.gidcolor.color import Color

from ._data import RawColorDataItem, COLOR_DATA

# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion [Constants]

FROM_CHECK_PARAMETER = [param(_raw_color_data, id=f"{_raw_color_data['name']}") for _raw_color_data in COLOR_DATA]


def _check_color_to_raw_data(_color: "Color", _raw_data: "RawColorDataItem") -> None:

    rel_approx_value = 1e-3

    assert _color.alpha == _raw_data["alpha"]

    assert _color.rgb == pytest.approx(_raw_data["rgb"], rel=rel_approx_value)
    assert _color.rgba == pytest.approx(_raw_data["rgb"] + (_raw_data["alpha"],), rel=rel_approx_value)

    assert _color.rgb_int == pytest.approx(_raw_data["rgb_int"], abs=1.0)
    assert _color.rgba_int == pytest.approx(_raw_data["rgb_int"] + (_raw_data["alpha"],), abs=1.0)

    assert _color.hsl == pytest.approx(_raw_data["hsl"], rel=rel_approx_value)
    assert _color.hsla == pytest.approx(_raw_data["hsl"] + (_raw_data["alpha"],), rel=rel_approx_value)

    assert _color.hsv == pytest.approx(_raw_data["hsv"], rel=rel_approx_value)
    assert _color.hsva == pytest.approx(_raw_data["hsv"] + (_raw_data["alpha"],), rel=rel_approx_value)

    # assert _color.hex.casefold() == (_raw_data["hex"] + f"{int(_raw_data['alpha'] * 255):02X}").casefold()


@pytest.mark.parametrize(["in_raw_color_data"], FROM_CHECK_PARAMETER)
def test_from_rgb(in_raw_color_data: RawColorDataItem):
    col: Color = Color.from_rgb(*in_raw_color_data["rgb"], alpha=in_raw_color_data["alpha"])

    _check_color_to_raw_data(col, in_raw_color_data)


@pytest.mark.parametrize(["in_raw_color_data"], FROM_CHECK_PARAMETER)
@pytest.mark.skip()
def test_from_rgb_int(in_raw_color_data: RawColorDataItem):
    col: Color = Color.from_rgb_int(*in_raw_color_data["rgb_int"], alpha=in_raw_color_data["alpha"])

    _check_color_to_raw_data(col, in_raw_color_data)


@pytest.mark.parametrize(["in_raw_color_data"], FROM_CHECK_PARAMETER)
def test_from_hsl(in_raw_color_data: RawColorDataItem):
    col: Color = Color.from_hsl(*in_raw_color_data["hsl"], alpha=in_raw_color_data["alpha"])

    _check_color_to_raw_data(col, in_raw_color_data)


@pytest.mark.parametrize(["in_raw_color_data"], FROM_CHECK_PARAMETER)
def test_from_hsv(in_raw_color_data: RawColorDataItem):
    col: Color = Color.from_hsv(*in_raw_color_data["hsv"], alpha=in_raw_color_data["alpha"])

    _check_color_to_raw_data(col, in_raw_color_data)


@pytest.mark.parametrize(["in_raw_color_data"], FROM_CHECK_PARAMETER)
@pytest.mark.skip()
def test_from_hex(in_raw_color_data: RawColorDataItem):
    col: Color = Color.from_hex(in_raw_color_data["hex"] + f"{int(in_raw_color_data['alpha'] * 255):02X}")

    _check_color_to_raw_data(col, in_raw_color_data)
